#!/usr/bin/env python3
"""
CompText Triage v2.1 – Termux Edition
Modulare medizinische Triage-TUI mit MedCodex, MedDB und Codex-Engine.
Optimiert für Android (Galaxy A33), Touch-freundlich, Offline-first.

Architektur:
    UI Layer (Textual) → TriageEngine → LLMClient (llama.cpp/MediaPipe)
                       ↓
                    MedCodex  ←→  MedDB
                       ↓
                    CodexEngine (Module-Generator)
"""
from __future__ import annotations

import asyncio
import time
from enum import Enum

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Static,
)

from med_db import MedDB, Patient, TriageLevel, TriageRecord
from med_codex import MedCodex
from codex_engine import CodexEngine

# ============================================================================
# KONFIGURATION
# ============================================================================
LLM_URL = "http://127.0.0.1:8080"


class Prio(Enum):
    P1 = ("P1 – KRITISCH", "prio-1", TriageLevel.P1)
    P2 = ("P2 – DRINGEND", "prio-2", TriageLevel.P2)
    P3 = ("P3 – AKUT", "prio-3", TriageLevel.P3)
    P4 = ("P4 – NORMAL", "prio-4", TriageLevel.P4)
    P5 = ("P5 – NICHT DRINGEND", "prio-5", TriageLevel.P5)
    ERR = ("FEHLER", "prio-err", TriageLevel.UNK)

    def __init__(self, label: str, css: str, db_level: TriageLevel) -> None:
        self.label = label
        self.css = css
        self.db_level = db_level


# ============================================================================
# QUICK-CASES
# ============================================================================
QUICK_CASES: dict[str, tuple[str, str]] = {
    "btn-bleed": ("P1: BLUTUNG", "MAB+HS, Patient blass, tachykard, RR↓"),
    "btn-acs":   ("P1: ACS/HERZ", "ACS, THX, DYSP, Schweißausbruch"),
    "btn-rea":   ("P1: REA KIND", "PÄD-REA, keine Spontanatmung, CPR läuft"),
    "btn-anap":  ("P1: ANAPHYLAXIE", "AP, Urtikaria, Angioödem, DYSP"),
    "btn-sepsis":("P1: SEPSIS", "SEPSIS, Fieber, Hypotonie, Tachykardie"),
    "btn-sht":   ("P2: SHT/STURZ", "SHT, Bewusstseinsstörung, GCS↓"),
}


# ============================================================================
# MAIN APP
# ============================================================================
class CompTriageApp(App[None]):

    CSS = """
    Screen { background: #050505; color: #d1d1d1; }
    #app-grid { layout: grid; grid-size: 2; grid-columns: 34% 1fr; height: 100%; }
    #side-bar { border-right: solid #333; padding: 1; background: #080808; }
    #main-zone { padding: 1; }

    .panel-title {
        text-align: center; color: #0f0; background: #111; text-style: bold;
        padding: 1; border-bottom: solid #333; margin-bottom: 1;
    }

    #stats-bar { height: auto; color: #888; margin-bottom: 1; }

    #display-content {
        border: tall #444; padding: 1; background: #0a0a0a;
        min-height: 12; color: #eee; margin-bottom: 1;
    }
    #display-content.prio-1 { background: #600; border: double #f00; color: #fff; text-style: bold; }
    #display-content.prio-2 { background: #540; border: double #fa0; color: #fff; }
    #display-content.prio-3 { background: #550; border: double #ff0; color: #fff; }
    #display-content.prio-4 { background: #0a0a0a; border: tall #444; color: #eee; }
    #display-content.prio-5 { background: #002a00; border: tall #0a0; color: #8f8; }
    #display-content.prio-err { background: #300; border: double #f00; color: #f88; }

    /* Touch-optimiert: große Buttons */
    Button { width: 100%; margin-bottom: 1; height: 3; background: #222; border: none; }
    #btn-bleed  { background: #911; color: #fff; }
    #btn-acs    { background: #951; color: #fff; }
    #btn-rea    { background: #919; color: #fff; }
    #btn-anap   { background: #961; color: #fff; }
    #btn-sepsis { background: #491; color: #fff; }
    #btn-sht    { background: #448; color: #fff; }
    #btn-history { background: #115; color: #fff; margin-top: 1; }
    #btn-codex   { background: #151; color: #0f0; }

    Input { border: tall #333; background: #111; color: #fff; margin-top: 1; }
    Input:focus { border: tall #0f0; }
    #history-table { height: 1fr; border-top: solid #333; }
    #log-panel { height: 6; border-top: solid #333; color: #555; margin-top: 1; }
    """

    BINDINGS = [
        Binding("f1", "show_help", "Hilfe"),
        Binding("ctrl+c", "quit", "Beenden"),
        Binding("b", "quick_bleed", "Blutung"),
        Binding("h", "quick_acs", "ACS"),
        Binding("a", "quick_anap", "Anaphylaxie"),
        Binding("s", "quick_sepsis", "Sepsis"),
        Binding("t", "quick_sht", "SHT"),
        Binding("k", "quick_rea", "REA Kind"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = MedDB()
        self.codex = MedCodex()
        self._case_counter = 0

    async def on_mount(self) -> None:
        await self.db.init_schema()
        self._refresh_stats()
        self.query_one("#log-panel", RichLog).write(
            "[green]✓[/green] MedDB + MedCodex initialisiert"
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-grid"):
            with Vertical(id="side-bar"):
                yield Static("QUICK-TACTIC", classes="panel-title")
                for btn_id, (label, _) in QUICK_CASES.items():
                    yield Button(label, id=btn_id)
                yield Button("📋 HISTORY", id="btn-history")
                yield Button("🧬 CODEX", id="btn-codex")
            with Vertical(id="main-zone"):
                yield Static("COMPTRIAGE – DIAGNOSTIC ENGINE", classes="panel-title")
                yield Label("Fälle: 0 | P1: 0 | Heute: 0 | Ø Latenz: 0ms", id="stats-bar")
                yield Static(
                    "Bereit.\nQuick-Events: B/H/A/S/T/K\nCodex: /gen, /list, /run, /expand\nFreitext: direkt eingeben",
                    id="display-content",
                )
                yield Input(placeholder="Symptome, Kürzel oder /Befehl eingeben...", id="user-input")
                yield DataTable(id="history-table")
                yield RichLog(id="log-panel")
        yield Footer()

    # --- Helpers ---

    def _reset_display(self) -> Static:
        d = self.query_one("#display-content", Static)
        d.remove_class("prio-1", "prio-2", "prio-3", "prio-4", "prio-5", "prio-err")
        return d

    def _refresh_stats(self) -> None:
        self.run_worker(self._update_stats_worker(), exclusive=False)

    async def _update_stats_worker(self) -> None:
        stats = await self.db.get_stats()
        label = self.query_one("#stats-bar", Label)
        label.update(
            f"Fälle: {stats['total_cases']} | "
            f"P1: {stats['p1_cases']} | "
            f"Heute: {stats['today_cases']} | "
            f"Ø Latenz: {stats['avg_latency_ms']}ms"
        )

    async def _call_llm(self, prompt: str) -> tuple[str, float]:
        start = time.time()
        async with httpx.AsyncClient(timeout=25.0) as client:
            r = await client.post(
                f"{LLM_URL}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": 80,
                    "temperature": 0.1,
                    "stop": ["\n\n", "USER:", "ASSISTANT:"],
                },
            )
            r.raise_for_status()
            data = r.json()
            content = data.get("content", "").strip()
            if not content:
                raise ValueError("Leere Antwort vom Server")
            return content, time.time() - start

    def _classify(self, text: str) -> Prio:
        t = text.lower()
        if any(x in t for x in ["p1", "critical", "kritisch", "notfall", "reanimation", "rea", "stillstand"]):
            return Prio.P1
        if any(x in t for x in ["p2", "urgent", "dringend", "schwer"]):
            return Prio.P2
        if any(x in t for x in ["p3", "acute", "akut"]):
            return Prio.P3
        if any(x in t for x in ["p5", "non-urgent", "nicht dringend"]):
            return Prio.P5
        return Prio.P4

    async def _store_case(self, input_text: str, response: str, prio: Prio, latency: float) -> None:
        self._case_counter += 1
        case_num = f"{time.strftime('%Y%m%d')}-{self._case_counter:03d}"
        patient = Patient(case_number=case_num, chief_complaint=input_text[:200])
        patient_id = await self.db.create_patient(patient)
        record = TriageRecord(
            patient_id=patient_id,
            input_text=input_text,
            raw_llm_response=response,
            assigned_priority=prio.db_level.value,
            confidence=0.85 if prio != Prio.ERR else 0.3,
            latency_ms=int(latency * 1000),
            model_name="local-llm",
        )
        await self.db.save_triage(record)
        self._refresh_stats()

    # --- Triage ---

    async def run_analysis(self, raw_text: str) -> None:
        display = self._reset_display()
        log = self.query_one("#log-panel", RichLog)

        # Codex-Expansion: Kürzel → Volltext für LLM
        expanded = self.codex.expand_prompt(raw_text)
        if expanded != raw_text:
            log.write(f"[dim]Codex: {raw_text} → {expanded[:60]}[/dim]")

        prompt = (
            f"MEDIZINISCHE TRIAGE – FALL: {expanded}\n"
            f"Klassifiziere nach Manchester Triage System (P1-P5).\n"
            f"Antworte NUR im Format: PRIO: [P1-P5] | BEGRÜNDUNG: [kurz]\n"
            f"ANTWORT:"
        )

        display.update("⏳ Inferenz läuft...")
        log.write(f"→ {raw_text[:50]}")

        try:
            res, elapsed = await self._call_llm(prompt)
            prio = self._classify(res)
            await self._store_case(raw_text, res, prio, elapsed)
            display.add_class(prio.css)
            display.update(
                f"[b]{prio.label}[/b]\n\n"
                f"[dim]Eingabe:[/dim] {raw_text}\n"
                f"[dim]Expanded:[/dim] {expanded[:80]}\n\n"
                f"{res}\n\n"
                f"[dim]{elapsed:.2f}s | Gespeichert[/dim]"
            )
            log.write(f"✓ {prio.label} ({elapsed:.1f}s)")

        except httpx.ConnectError:
            display.add_class(Prio.ERR.css)
            display.update(
                "[red]OFFLINE[/red]\n\n"
                "llama-server auf :8080 nicht erreichbar.\n"
                "Starten mit:\n"
                "  llama-server -m ~/models/*.gguf --port 8080 -c 2048 -t 4"
            )
            log.write("✗ Server nicht erreichbar")

        except Exception as exc:
            display.add_class(Prio.ERR.css)
            display.update(f"[red]FEHLER[/red]\n\n{exc}")
            log.write(f"✗ {exc}")

    # --- Codex-Befehle ---

    async def _handle_codex_command(self, text: str) -> None:
        display = self._reset_display()
        log = self.query_one("#log-panel", RichLog)

        if text.startswith("/gen "):
            description = text[5:].strip()
            display.update(f"⏳ Generiere Modul: {description[:50]}...")
            log.write(f"🧬 /gen: {description[:40]}")
            try:
                engine = CodexEngine()
                mod = await engine.generate_module(description)
                display.update(
                    f"[green]✓ Modul erstellt:[/green] {mod.name}\n"
                    f"Pfad: {mod.file_path}\n"
                    f"Größe: {len(mod.source_code)} Zeichen\n\n"
                    f"[dim]{mod.description}[/dim]"
                )
                log.write(f"✓ {mod.name}.py gespeichert")
            except Exception as exc:
                display.update(f"[red]Codex-Fehler:[/red] {exc}")
                log.write(f"✗ {exc}")

        elif text.startswith("/list"):
            engine = CodexEngine()
            mods = engine.list_modules()
            lines = ["[b]📦 Generierte Module[/b]\n"]
            for m in mods:
                lines.append(f"• {m['name']} ({m['size']} bytes, {m['modified']})")
            display.update("\n".join(lines) if mods else "Keine Module vorhanden.\n/gen <Beschreibung> um ein Modul zu erstellen")

        elif text.startswith("/run "):
            name = text[5:].strip()
            log.write(f"▶ /run: {name}")
            try:
                engine = CodexEngine()
                result = await engine.run_module(name)
                display.update(f"[b]▶ {name}[/b]\n\nErgebnis:\n{result}")
                log.write(f"▶ {name} OK")
            except Exception as exc:
                display.update(f"[red]Laufzeitfehler:[/red] {exc}")
                log.write(f"✗ {exc}")

        elif text.startswith("/expand "):
            term = text[8:].strip()
            expanded = self.codex.expand_prompt(term)
            entries = self.codex.search(term, limit=5)
            lines = [f"[b]Codex-Expansion: {term}[/b]\n", f"→ {expanded}\n"]
            if entries:
                lines.append("\n[dim]Verwandte Einträge:[/dim]")
                for e in entries:
                    lines.append(f"  [{e.shorthand}] {e.expansion}")
                    if e.icd10:
                        lines.append(f"      ICD-10: {e.icd10} | Prio: {e.priority_hint}")
            display.update("\n".join(lines))

        elif text == "/help" or text == "/h":
            display.update(
                "[b]COMPTRIAGE – Befehle[/b]\n\n"
                "[b]Codex:[/b]\n"
                "  /expand <Kürzel>     – Kürzel aufschlüsseln\n"
                "  /gen <Beschreibung>  – Neues Modul via LLM generieren\n"
                "  /list                – Alle generierten Module anzeigen\n"
                "  /run <name>          – Modul ausführen\n\n"
                "[b]Hotkeys:[/b]\n"
                "  B – P1: Blutung    H – ACS/Herz\n"
                "  A – Anaphylaxie    S – Sepsis\n"
                "  T – SHT/Sturz      K – REA Kind\n\n"
                "[b]Kürzel (Beispiele):[/b]\n"
                "  MAB, ACS, AP, SHT, REA, SEPSIS\n"
                "  THX, DYSP, SYNK, STEMI, PE\n"
                "  Kombiniert: MAB+HS, RR↓ HF↑"
            )

    # --- Event Handler ---

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-history":
            await self._show_history()
            return
        if event.button.id == "btn-codex":
            display = self._reset_display()
            display.update(
                "[b]🧬 CODEX – Modul-Generator & Lexikon[/b]\n\n"
                "Befehle im Eingabefeld:\n"
                "  /expand MAB+HS     – Kürzel aufschlüsseln\n"
                "  /gen <Beschreibung>– Neues Modul generieren\n"
                "  /list              – Alle Module anzeigen\n"
                "  /run <name>        – Modul ausführen\n"
                "  /help              – Alle Befehle\n\n"
                f"Codex: {self.codex.count()} Einträge geladen"
            )
            return
        if event.button.id in QUICK_CASES:
            _, text = QUICK_CASES[event.button.id]
            await self.run_analysis(text)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        self.query_one("#user-input", Input).value = ""
        if not text:
            return
        if text.startswith("/"):
            await self._handle_codex_command(text)
        else:
            await self.run_analysis(text)

    async def _show_history(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Zeit", "Fall", "Prio", "Complaint", "ms")
        rows = await self.db.get_history(limit=20)
        for r in rows:
            table.add_row(
                r["created_at"][11:19],
                r["case_number"],
                r["assigned_priority"][:2],
                r["input_text"][:30] + "...",
                str(r["latency_ms"]),
            )
        self.query_one("#log-panel", RichLog).write(f"📋 {len(rows)} Einträge geladen")

    # --- Hotkey Actions ---
    def action_quick_bleed(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-bleed"][1]))
    def action_quick_acs(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-acs"][1]))
    def action_quick_anap(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-anap"][1]))
    def action_quick_sepsis(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-sepsis"][1]))
    def action_quick_sht(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-sht"][1]))
    def action_quick_rea(self) -> None:
        self.run_worker(self.run_analysis(QUICK_CASES["btn-rea"][1]))

    def action_show_help(self) -> None:
        self.run_worker(self._handle_codex_command("/help"))

    async def on_unmount(self) -> None:
        pass


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    CompTriageApp().run()
