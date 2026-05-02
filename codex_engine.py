#!/usr/bin/env python3
"""
CodexEngine – Selbst-modifizierendes Modul-System
==================================================
Nutzt den lokalen llama-server, um Python-Module zu generieren und zu verwalten.
Inspiriert von Hermes Agent's Skills-System, aber offline-first und Termux-kompatibel.
"""
from __future__ import annotations

import asyncio
import importlib.util
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from med_db import MedDB


@dataclass
class GeneratedModule:
    name: str
    description: str
    source_code: str
    file_path: Path
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class CodexEngine:
    """
    Generiert, speichert und lädt dynamisch Python-Module via lokalem LLM.

    Workflow:
        1. describe() → LLM generiert Python-Code
        2. save()     → Gespeichert als modules/{name}.py
        3. load()     → Dynamisch importiert und als Instanz zurückgegeben
        4. run()      → Module.run(*args) wird aufgerufen
    """

    SYSTEM_PROMPT = """Du bist ein medizinischer Software-Engineer für Termux/Android.
Du schreibst sauberen Python-Code für das CompText Triage System.

REGELN:
- NUR Python-Code in deiner Antwort
- Der Code muss eine Klasse namens 'Module' enthalten
- Die Klasse braucht: __init__(self, db) und eine run(*args, **kwargs) -> dict Methode
- Keine externen Dependencies außer: sqlite3, json, datetime, pathlib
- return-Wert von run() ist immer ein Dict mit 'status' und 'data'
- Kommentiere den Code auf Deutsch
- Kompatibel mit Python 3.11+

ANTWORT: Nur Code zwischen ```python und ```. Keine anderen Texte."""

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8080",
        modules_dir: str | Path = "~/comptext-termux/modules",
    ) -> None:
        self.server_url = server_url
        self.modules_dir = Path(modules_dir).expanduser()
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        self.db = MedDB()
        self._loaded: dict[str, Any] = {}

    async def generate_module(
        self,
        user_request: str,
        module_name: str | None = None,
    ) -> GeneratedModule:
        """
        Fragt den lokalen LLM nach einem Modul und speichert es.

        Beispiele:
            await engine.generate_module("Vitals-Tracker für RR, Puls, SpO2")
            await engine.generate_module("Blutzucker-Log mit Zeitstempel und Trendanalyse")
            await engine.generate_module("Notfall-Kontaktliste mit Schnellwahl")
        """
        if not module_name:
            module_name = self._sanitize_name(user_request[:40])

        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"AUFGABE: {user_request}\n\n"
            f"Das Modul hat Zugriff auf 'self.db' (MedDB-Instanz mit SQLite).\n"
            f"Modulname: {module_name}\n\n"
            f"Erstelle jetzt den vollständigen Python-Code:\n"
        )

        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(
                f"{self.server_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": 1000,
                    "temperature": 0.2,
                    "stop": ["\n\n\n", "USER:", "ASSISTANT:", "Soll ich"],
                },
            )
            r.raise_for_status()
            raw = r.json().get("content", "")

        code = self._extract_code(raw)
        if not code:
            raise ValueError(
                f"Kein Python-Code in der LLM-Antwort gefunden.\n"
                f"Antwort (ersten 200 Zeichen): {raw[:200]}"
            )

        # Syntax-Check
        try:
            compile(code, module_name, "exec")
        except SyntaxError as e:
            raise ValueError(f"Generierter Code hat Syntaxfehler: {e}") from e

        # Speichern
        file_path = self.modules_dir / f"{module_name}.py"
        file_path.write_text(code, encoding="utf-8")

        mod = GeneratedModule(
            name=module_name,
            description=user_request,
            source_code=code,
            file_path=file_path,
            metadata={
                "prompt_length": len(prompt),
                "code_length": len(code),
                "raw_response_length": len(raw),
            },
        )

        return mod

    def _extract_code(self, text: str) -> str | None:
        """Extrahiert Python-Code aus Markdown-Blöcken."""
        # Versuch 1: ```python ... ```
        m = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if m:
            return m.group(1).strip()
        # Versuch 2: ``` ... ```
        m = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if m:
            return m.group(1).strip()
        # Fallback: Wenn 'class Module:' direkt im Text
        if "class Module:" in text:
            idx = text.find("class Module:")
            return text[idx:].strip()
        return None

    def _sanitize_name(self, text: str) -> str:
        """Erzeugt einen validen Python-Modulnamen."""
        clean = re.sub(r"[^a-z0-9_]", "_", text.lower().strip())[:40]
        return clean.strip("_") or "generated_module"

    def load_module(self, name: str) -> Any:
        """Lädt ein generiertes Modul dynamisch."""
        if name in self._loaded:
            return self._loaded[name]

        file_path = self.modules_dir / f"{name}.py"
        if not file_path.exists():
            available = [f.stem for f in self.modules_dir.glob("*.py")]
            raise FileNotFoundError(
                f"Modul '{name}' nicht gefunden.\n"
                f"Verfügbar: {', '.join(available) or '(keine)'}"
            )

        spec = importlib.util.spec_from_file_location(name, file_path)
        if not spec or not spec.loader:
            raise ImportError(f"Kann '{name}' nicht laden")

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"codex_{name}"] = module
        spec.loader.exec_module(module)  # type: ignore

        if not hasattr(module, "Module"):
            raise AttributeError(
                f"Modul '{name}' hat keine 'Module'-Klasse.\n"
                f"Generierte Module brauchen: class Module: def __init__(self, db): ..."
            )

        instance = module.Module(self.db)
        self._loaded[name] = instance
        return instance

    def list_modules(self) -> list[dict[str, Any]]:
        """Zeigt alle verfügbaren generierten Module."""
        mods = []
        for f in sorted(self.modules_dir.glob("*.py")):
            mods.append({
                "name": f.stem,
                "path": str(f),
                "size": f.stat().st_size,
                "modified": time.ctime(f.stat().st_mtime),
            })
        return mods

    async def run_module(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Lädt und führt ein Modul aus."""
        mod = self.load_module(name)
        if asyncio.iscoroutinefunction(mod.run):
            return await mod.run(*args, **kwargs)
        return mod.run(*args, **kwargs)

    def delete_module(self, name: str) -> bool:
        """Löscht ein generiertes Modul."""
        file_path = self.modules_dir / f"{name}.py"
        if file_path.exists():
            file_path.unlink()
            self._loaded.pop(name, None)
            return True
        return False
