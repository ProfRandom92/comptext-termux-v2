#!/usr/bin/env python3
"""
CodexManager – Verwaltungs-Interface für Fachbereich-Module
============================================================
Lädt, verwaltet und befüllt den MedCodex automatisch mit fachspezifischen
Kürzeln. Kernstück des "Specialty Module Auto-Fill"-Systems.

Features:
    - Fachbereiche per Knopfdruck laden (NEU, RAD, KAR, INT, PÄD, CHI, ...)
    - Automatische Konflikt-Erkennung (Kürzel schon vorhanden?)
    - Status-Übersicht: welche Module sind geladen?
    - Selektives Laden nach Prio-Klasse
    - Export als Hermes-Skill-Datei (SKILL.md)
    - Triage-Preset-Konfigurationen (z.B. "Notaufnahme", "Kinderarzt")

Verwendung (TUI-Befehlszeile):
    /codex-mgr load NEU         → Neurologie laden
    /codex-mgr load ALL         → Alle Fachbereiche
    /codex-mgr status           → Was ist geladen?
    /codex-mgr unload RAD       → Radiologie entfernen
    /codex-mgr preset ER        → Notaufnahme-Preset
    /codex-mgr export-skill     → Als Hermes SKILL.md exportieren
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from med_codex import MedCodex, CodexEntry
from med_specialties import SPECIALTY_MODULES, SpecEntry, get_all_entries


# ============================================================================
# PRESETS: Vorkonfigurierte Modul-Sets für typische Einsatzbereiche
# ============================================================================
PRESETS: dict[str, dict] = {
    "ER": {
        "name": "Notaufnahme",
        "description": "Alle P1/P2-Notfälle, breite Abdeckung",
        "modules": ["NEU", "KAR", "INT", "CHI", "PÄD", "PUL", "GAS"],
        "priority_filter": ["P1", "P2"],
        "icon": "🚨",
    },
    "ICU": {
        "name": "Intensivstation",
        "description": "Beatmung, Monitoring, Organversagen",
        "modules": ["INT", "KAR", "PUL", "NEP"],
        "priority_filter": ["P1"],
        "icon": "💉",
    },
    "PEDS": {
        "name": "Pädiatrische Notaufnahme",
        "description": "Kindliche Notfälle, Dosierungen",
        "modules": ["PÄD", "PUL", "NEU"],
        "priority_filter": ["P1", "P2"],
        "icon": "👶",
    },
    "NEURO": {
        "name": "Neurologische Notaufnahme",
        "description": "Schlaganfall, Epilepsie, Bewusstsein",
        "modules": ["NEU", "RAD", "INT"],
        "priority_filter": ["P1", "P2"],
        "icon": "🧠",
    },
    "TRAUMA": {
        "name": "Traumazentrum",
        "description": "Polytrauma, ATLS, Chirurgie",
        "modules": ["CHI", "RAD", "INT", "KAR"],
        "priority_filter": ["P1", "P2"],
        "icon": "🚑",
    },
    "FULL": {
        "name": "Vollständiger Codex",
        "description": "Alle Fachbereiche, alle Prioritäten",
        "modules": list(SPECIALTY_MODULES.keys()),
        "priority_filter": None,  # alle
        "icon": "📚",
    },
}


@dataclass
class LoadResult:
    module_code: str
    added: int
    skipped: int
    conflicts: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodexStatus:
    total_entries: int
    base_entries: int
    specialty_entries: int
    loaded_modules: list[str]
    presets_active: list[str]
    top_used: list[tuple[str, int]]


class CodexManager:
    """
    Zentrales Interface für die Verwaltung des MedCodex-Inhalts.
    Lädt Fachbereich-Module in den Codex, verwaltet Konflikte und Presets.
    """

    # Manifest-Datei: welche Module sind aktuell geladen?
    MANIFEST_PATH = Path("~/comptext-termux/data/codex_manifest.json").expanduser()

    def __init__(self) -> None:
        self.codex = MedCodex()
        self._manifest: dict = self._load_manifest()

    # --- Manifest ---

    def _load_manifest(self) -> dict:
        if self.MANIFEST_PATH.exists():
            try:
                return json.loads(self.MANIFEST_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"loaded_modules": [], "load_history": [], "presets_active": []}

    def _save_manifest(self) -> None:
        self.MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.MANIFEST_PATH.write_text(
            json.dumps(self._manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _is_loaded(self, module_code: str) -> bool:
        return module_code in self._manifest.get("loaded_modules", [])

    # --- Load / Unload ---

    def load_module(
        self,
        module_code: str,
        priority_filter: list[str] | None = None,
        force: bool = False,
    ) -> LoadResult:
        """
        Lädt einen Fachbereich in den MedCodex.

        Args:
            module_code:     z.B. "NEU", "RAD", "KAR"
            priority_filter: None = alle, ["P1"] = nur Notfälle
            force:           Vorhandene Einträge überschreiben
        """
        if module_code not in SPECIALTY_MODULES:
            raise ValueError(
                f"Unbekannter Fachbereich: {module_code}\n"
                f"Verfügbar: {', '.join(SPECIALTY_MODULES.keys())}"
            )

        spec = SPECIALTY_MODULES[module_code]
        entries: list[SpecEntry] = spec["entries"]

        if priority_filter:
            entries = [e for e in entries if e.priority_hint in priority_filter]

        added = 0
        skipped = 0
        conflicts: list[str] = []

        for entry in entries:
            existing = self.codex.get(entry.shorthand)
            if existing and not force:
                # Konflikt: Kürzel schon vorhanden
                if existing.expansion != entry.expansion:
                    conflicts.append(
                        f"{entry.shorthand}: "
                        f"'{existing.expansion[:30]}' vs "
                        f"'{entry.expansion[:30]}'"
                    )
                skipped += 1
                continue

            # Eintrag hinzufügen
            self.codex.add(CodexEntry(
                shorthand=entry.shorthand,
                expansion=entry.expansion,
                category=entry.category,
                icd10=entry.icd10,
                priority_hint=entry.priority_hint,
                context=entry.context,
            ))
            added += 1

        # Manifest aktualisieren
        if module_code not in self._manifest["loaded_modules"]:
            self._manifest["loaded_modules"].append(module_code)
        self._manifest["load_history"].append({
            "module": module_code,
            "added": added,
            "skipped": skipped,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_manifest()

        return LoadResult(
            module_code=module_code,
            added=added,
            skipped=skipped,
            conflicts=conflicts,
        )

    def load_preset(self, preset_code: str, force: bool = False) -> list[LoadResult]:
        """Lädt ein vorkonfiguriertes Modul-Set."""
        if preset_code not in PRESETS:
            raise ValueError(
                f"Unbekanntes Preset: {preset_code}\n"
                f"Verfügbar: {', '.join(PRESETS.keys())}"
            )

        preset = PRESETS[preset_code]
        results: list[LoadResult] = []

        for module_code in preset["modules"]:
            if module_code not in SPECIALTY_MODULES:
                continue  # Modul existiert nicht (z.B. NEP noch nicht implementiert)
            try:
                r = self.load_module(
                    module_code,
                    priority_filter=preset.get("priority_filter"),
                    force=force,
                )
                results.append(r)
            except Exception:
                pass  # Fehler einzelner Module nicht abbrechen lassen

        if preset_code not in self._manifest.get("presets_active", []):
            self._manifest.setdefault("presets_active", []).append(preset_code)
        self._save_manifest()

        return results

    def unload_module(self, module_code: str) -> int:
        """Entfernt alle Einträge eines Fachbereichs aus dem Codex."""
        if module_code not in SPECIALTY_MODULES:
            raise ValueError(f"Unbekannter Fachbereich: {module_code}")

        spec = SPECIALTY_MODULES[module_code]
        entries: list[SpecEntry] = spec["entries"]
        removed = 0

        with sqlite3.connect(str(self.codex.db_path)) as conn:
            for entry in entries:
                cur = conn.execute(
                    "DELETE FROM codex WHERE shorthand = ?", (entry.shorthand,)
                )
                removed += cur.rowcount
            conn.commit()

        # Manifest aktualisieren
        if module_code in self._manifest.get("loaded_modules", []):
            self._manifest["loaded_modules"].remove(module_code)
        self._save_manifest()

        return removed

    # --- Status ---

    def get_status(self) -> CodexStatus:
        """Vollständiger Status des Codex."""
        total = self.codex.count()
        base = len(MedCodex.DEFAULT_CODEX)

        return CodexStatus(
            total_entries=total,
            base_entries=base,
            specialty_entries=max(0, total - base),
            loaded_modules=self._manifest.get("loaded_modules", []),
            presets_active=self._manifest.get("presets_active", []),
            top_used=self.codex.top_used(limit=5),
        )

    def format_status(self) -> str:
        """Status als formatierter String für TUI-Anzeige."""
        s = self.get_status()

        lines = [
            "📚 CODEX STATUS",
            "─" * 40,
            f"Gesamt-Einträge: {s.total_entries}",
            f"  Basis-Codex:   {s.base_entries}",
            f"  Fachbereiche:  {s.specialty_entries}",
            "",
            "📦 Geladene Module:",
        ]

        if s.loaded_modules:
            for code in s.loaded_modules:
                spec = SPECIALTY_MODULES.get(code, {})
                icon = spec.get("icon", "•")
                name = spec.get("name", code)
                count = len(spec.get("entries", []))
                lines.append(f"  {icon} [{code}] {name} ({count} Kürzel)")
        else:
            lines.append("  (keine Fachbereiche geladen)")

        if s.presets_active:
            lines.append("")
            lines.append("⚙️ Aktive Presets:")
            for preset in s.presets_active:
                p = PRESETS.get(preset, {})
                lines.append(f"  {p.get('icon','•')} {preset}: {p.get('name','')}")

        if s.top_used:
            lines.append("")
            lines.append("🔥 Meistgenutzte Kürzel:")
            for shorthand, count in s.top_used:
                if count > 0:
                    lines.append(f"  {shorthand}: {count}×")

        lines.append("")
        lines.append("Befehle: /codex-mgr load NEU | /codex-mgr preset ER")
        return "\n".join(lines)

    def list_available(self) -> str:
        """Zeigt alle verfügbaren Module und Presets."""
        lines = ["📋 VERFÜGBARE FACHBEREICHE:", ""]
        for code, spec in SPECIALTY_MODULES.items():
            loaded = "✓" if self._is_loaded(code) else "○"
            count = len(spec["entries"])
            lines.append(
                f"  {loaded} {spec['icon']} [{code}] {spec['name']} "
                f"– {count} Kürzel"
            )
            lines.append(f"      {spec['description']}")

        lines.extend(["", "⚙️ PRESETS:", ""])
        for code, preset in PRESETS.items():
            modules_str = "+".join(preset["modules"][:4])
            if len(preset["modules"]) > 4:
                modules_str += f"+{len(preset['modules'])-4}weitere"
            pf = preset.get("priority_filter")
            pf_str = f" [{'/'.join(pf)}]" if pf else " [alle Prioritäten]"
            lines.append(
                f"  {preset['icon']} [{code}] {preset['name']}{pf_str}"
            )
            lines.append(f"      {preset['description']}")
            lines.append(f"      Module: {modules_str}")

        return "\n".join(lines)

    # --- Hermes SKILL.md Export ---

    def export_hermes_skill(
        self,
        output_path: str | Path | None = None,
    ) -> Path:
        """
        Exportiert den aktuellen Codex als Hermes-kompatibler SKILL.md.
        Folgt dem agentskills.io Open Standard.
        """
        if output_path is None:
            output_path = Path("~/comptext-termux/skills/medcodex.SKILL.md").expanduser()

        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        status = self.get_status()
        loaded_names = [
            SPECIALTY_MODULES[c]["name"]
            for c in status.loaded_modules
            if c in SPECIALTY_MODULES
        ]

        # Alle Einträge für den Skill sammeln
        with sqlite3.connect(str(self.codex.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, expansion, category, icd10, priority_hint, context "
                "FROM codex ORDER BY priority_hint, category, shorthand"
            ).fetchall()

        # SKILL.md im Hermes-Format
        content = f"""---
name: medcodex-triage
description: >
  Medical shorthand codex for German emergency medicine and ePA documentation.
  Bidirectional compression: expand abbreviations for LLM prompts, compress
  text for token-efficient storage. {status.total_entries} entries covering
  NOTFALL, SYMPTOM, DIAGNOSE, MEDIKAMENT, LABOR, EPA categories.
  Loaded specialties: {', '.join(loaded_names) or 'Base only'}.
version: "2.1.0"
author: ProfRandom92
license: MIT
platforms: [linux, macos, android]
metadata:
  hermes:
    tags: [medical, german, triage, epa, fhir, icd10, compression, termux]
    category: health
    config:
      codex_path:
        description: Path to MedCodex SQLite database
        default: "~/comptext-termux/data/medcodex.db"
---

# MedCodex Triage Skill

Du hast Zugriff auf ein medizinisches Kurzform-Lexikon für die deutsche
Notfallmedizin und ePA-Dokumentation.

## Kern-Aufgaben

1. **Expand**: Erkenne Kürzel im Text und ersetze sie durch Volltext
2. **Compress**: Erkenne Vollbegriffe und ersetze durch Kürzel
3. **Triage**: Leite aus Kürzeln die Priorität (P1–P5) ab
4. **Codex-Verwaltung**: Lade Fachbereich-Module auf Anfrage

## Kürzel-Expansion (Beispiele)

| Kürzel | Expansion | Prio |
|--------|-----------|------|
| MAB+HS | Massive arterielle Blutung mit hämorrhagischem Schock | P1 |
| ACS | Akutes Koronarsyndrom | P1 |
| STEMI | ST-Hebungsinfarkt | P1 |
| APOPLEX | Ischämischer Schlaganfall | P1 |
| SEPSIS | Sepsis (qSOFA, Laktat, Antibiotika <1h) | P1 |
| DYSP | Dyspnoe / Atemnot | P2 |
| THX | Thoraxschmerz | P2 |
| GCS↓ | Glasgow Coma Scale vermindert | P2 |

## Fachbereich-Module

Lade bei Bedarf zusätzliche Kürzel:
```
/codex-mgr load NEU      # Neurologie (NIHSS, EEG, APOPLEX, GBS...)
/codex-mgr load RAD      # Radiologie (CCT, MRT, DWI, CTPA, ECHO...)
/codex-mgr load INT      # Intensivmedizin (RSI, PEEP, CRRT, SOFA...)
/codex-mgr load PÄD      # Pädiatrie (APGAR, REA-Dosierungen...)
/codex-mgr load CHI      # Chirurgie (ATLS, FAST-US, DAMAGE-C...)
/codex-mgr preset ER     # Notaufnahme-Preset (P1+P2, alle Felder)
/codex-mgr preset ICU    # Intensivmedizin-Preset
/codex-mgr status        # Aktueller Status
```

## Vollständiger Codex ({status.total_entries} Einträge)

"""
        # Einträge nach Kategorie
        by_cat: dict[str, list] = {}
        for row in rows:
            cat = row[2]
            by_cat.setdefault(cat, []).append(row)

        for cat, entries in sorted(by_cat.items()):
            content += f"\n### {cat}\n\n"
            content += "| Kürzel | Expansion | ICD-10 | Prio | Kontext |\n"
            content += "|--------|-----------|--------|------|---------|\n"
            for sh, exp, _, icd, prio, ctx in entries:
                icd_str = icd or "—"
                ctx_str = (ctx[:40] + "…") if ctx and len(ctx) > 40 else (ctx or "—")
                content += f"| `{sh}` | {exp} | {icd_str} | {prio} | {ctx_str} |\n"

        content += f"""
---
*Exportiert: {datetime.now().strftime('%Y-%m-%d %H:%M')} | CompText Termux v2.1*
*Geladene Module: {', '.join(status.loaded_modules) or 'Basis'}*
"""

        output_path.write_text(content, encoding="utf-8")
        return output_path


# ============================================================================
# CLI-Interface für Termux / direkte Nutzung
# ============================================================================
def main() -> None:
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="CodexManager – Fachbereich-Module für MedCodex"
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Alle Module und Presets anzeigen")
    sub.add_parser("status", help="Aktueller Codex-Status")

    load_p = sub.add_parser("load", help="Fachbereich laden")
    load_p.add_argument("module", help="Modul-Code (NEU, RAD, KAR, INT, PÄD, CHI, PSY, GAS, PUL)")
    load_p.add_argument("--priority", "-p", nargs="+", help="Nur bestimmte Prioritäten")
    load_p.add_argument("--force", "-f", action="store_true", help="Konflikte überschreiben")

    preset_p = sub.add_parser("preset", help="Preset laden")
    preset_p.add_argument("preset", help="Preset-Code (ER, ICU, PEDS, NEURO, TRAUMA, FULL)")
    preset_p.add_argument("--force", "-f", action="store_true")

    unload_p = sub.add_parser("unload", help="Fachbereich entfernen")
    unload_p.add_argument("module", help="Modul-Code")

    sub.add_parser("export-skill", help="Als Hermes SKILL.md exportieren")

    args = parser.parse_args()
    mgr = CodexManager()

    if args.cmd == "list":
        print(mgr.list_available())

    elif args.cmd == "status":
        print(mgr.format_status())

    elif args.cmd == "load":
        code = args.module.upper()
        r = mgr.load_module(code, priority_filter=args.priority, force=args.force)
        print(f"✓ [{code}] {SPECIALTY_MODULES[code]['name']}")
        print(f"  Hinzugefügt: {r.added} | Übersprungen: {r.skipped}")
        if r.conflicts:
            print(f"  ⚠ Konflikte ({len(r.conflicts)}):")
            for c in r.conflicts[:5]:
                print(f"    {c}")

    elif args.cmd == "preset":
        code = args.preset.upper()
        results = mgr.load_preset(code, force=args.force)
        preset = PRESETS[code]
        total_added = sum(r.added for r in results)
        print(f"✓ Preset [{code}] {preset['name']}: {total_added} Einträge geladen")
        for r in results:
            spec = SPECIALTY_MODULES.get(r.module_code, {})
            print(f"  {spec.get('icon','•')} {r.module_code}: +{r.added}")

    elif args.cmd == "unload":
        code = args.module.upper()
        removed = mgr.unload_module(code)
        print(f"✓ [{code}] {removed} Einträge entfernt")

    elif args.cmd == "export-skill":
        path = mgr.export_hermes_skill()
        print(f"✓ Hermes SKILL.md exportiert: {path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
