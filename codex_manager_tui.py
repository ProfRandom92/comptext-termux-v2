#!/usr/bin/env python3
"""
CodexManager TUI – Fachbereich-Interface für comptext-termux
=============================================================
Eigenständiges Interface zum Verwalten und automatischen Befüllen
des MedCodex mit Fachbereich-Modulen.

Starten:
    python codex_manager_tui.py

Oder integriert aus comptrage.py via:
    /codex-mgr (öffnet dieses Panel als Overlay)
"""
from __future__ import annotations

import asyncio
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    RichLog,
    Static,
    Input,
)
from textual.reactive import reactive

from med_codex import MedCodex
from codex_manager import CodexManager, PRESETS, SPECIALTY_MODULES


class ModuleCard(Static):
    """Zeigt einen Fachbereich als Karte an."""

    def __init__(self, code: str, spec: dict, loaded: bool, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._code = code
        self._spec = spec
        self._loaded = loaded

    def compose(self) -> ComposeResult:
        status = "✓" if self._loaded else "○"
        count = len(self._spec["entries"])
        text = (
            f"{status} {self._spec['icon']} [{self._code}] "
            f"{self._spec['name']} ({count} Kürzel)\n"
            f"   {self._spec['description']}"
        )
        yield Static(text)


class CodexManagerApp(App[None]):
    """
    TUI für das Codex-Modul-Management.
    Zeigt verfügbare Fachbereiche, Presets und Codex-Status.
    """

    CSS = """
    Screen { background: #050505; color: #d1d1d1; }

    #header-bar {
        height: auto; background: #0a0f0a;
        border-bottom: solid #1a3a1a; padding: 1;
        text-align: center; color: #0f0; text-style: bold;
    }

    #main-grid {
        layout: grid; grid-size: 3; grid-columns: 28% 40% 1fr;
        height: 1fr;
    }

    /* Linke Spalte: Module */
    #module-panel { border-right: solid #222; background: #030803; padding: 1; }
    .panel-title {
        text-align: center; color: #0f0; background: #111; text-style: bold;
        padding: 1; border-bottom: solid #333; margin-bottom: 1;
    }

    .module-btn { width: 100%; margin-bottom: 1; height: auto; min-height: 3; border: none; }
    .module-btn.loaded  { background: #0a2a0a; color: #0f0; }
    .module-btn.unloaded { background: #1a1a1a; color: #888; }

    /* Mittlere Spalte: Presets + Status */
    #center-panel { border-right: solid #222; padding: 1; }

    .preset-btn { width: 100%; margin-bottom: 1; height: 3; background: #111522; color: #88f; border: none; }
    .preset-btn:hover { background: #1a2a44; }

    #status-display {
        border: tall #1a3a1a; padding: 1; background: #020a02;
        min-height: 10; color: #8f8; margin-top: 1;
    }

    /* Rechte Spalte: Codex-Vorschau + Log */
    #right-panel { padding: 1; }

    #codex-table { height: 1fr; border: tall #222; }
    #log-panel { height: 8; border-top: solid #222; color: #555; margin-top: 1; }

    #search-input { border: tall #333; background: #111; color: #0f0; margin-bottom: 1; }

    #stats-bar {
        height: auto; background: #0a0a0a; padding: 1;
        border-bottom: solid #222; color: #888; text-align: center;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Beenden"),
        Binding("ctrl+a", "load_all", "Alle laden"),
        Binding("ctrl+e", "export_skill", "Skill exportieren"),
        Binding("ctrl+r", "refresh_status", "Aktualisieren"),
        Binding("f1", "show_help", "Hilfe"),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.mgr = CodexManager()
        self.codex = MedCodex()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "🧠 COMPTEXT CODEX MANAGER – Fachbereich-Module",
            id="header-bar",
        )
        yield Static("", id="stats-bar")

        with Horizontal(id="main-grid"):

            # Linke Spalte: Fachbereiche
            with Vertical(id="module-panel"):
                yield Static("FACHBEREICHE", classes="panel-title")
                for code, spec in SPECIALTY_MODULES.items():
                    status = self.mgr._is_loaded(code)
                    css = "module-btn loaded" if status else "module-btn unloaded"
                    label = (
                        f"{'✓' if status else '○'} {spec['icon']} "
                        f"[{code}] {spec['name']}"
                    )
                    yield Button(label, id=f"mod-{code}", classes=css)

            # Mittlere Spalte
            with Vertical(id="center-panel"):
                yield Static("PRESETS", classes="panel-title")
                for code, preset in PRESETS.items():
                    yield Button(
                        f"{preset['icon']} [{code}] {preset['name']}",
                        id=f"preset-{code}",
                        classes="preset-btn",
                    )
                yield Static("STATUS", classes="panel-title")
                yield Static(
                    self.mgr.format_status(),
                    id="status-display",
                )

            # Rechte Spalte
            with Vertical(id="right-panel"):
                yield Static("CODEX-VORSCHAU", classes="panel-title")
                yield Input(
                    placeholder="Suche... (Kürzel, ICD-10, Begriff)",
                    id="search-input",
                )
                yield DataTable(id="codex-table")
                yield RichLog(id="log-panel")

        yield Footer()

    async def on_mount(self) -> None:
        self._setup_table()
        self._update_stats()
        self._load_table("")
        log = self.query_one("#log-panel", RichLog)
        log.write(f"[green]✓[/green] CodexManager bereit | {self.codex.count()} Einträge")

    def _setup_table(self) -> None:
        table = self.query_one("#codex-table", DataTable)
        table.add_columns("Kürzel", "Expansion", "ICD-10", "Prio", "Kategorie")

    def _load_table(self, search: str = "") -> None:
        table = self.query_one("#codex-table", DataTable)
        table.clear()
        if search:
            entries = self.codex.search(search, limit=50)
        else:
            import sqlite3
            with sqlite3.connect(str(self.codex.db_path)) as conn:
                rows = conn.execute(
                    "SELECT shorthand, expansion, icd10, priority_hint, category "
                    "FROM codex ORDER BY priority_hint, category LIMIT 100"
                ).fetchall()
            entries = rows  # type: ignore

        for e in entries:
            if hasattr(e, "shorthand"):
                row = (e.shorthand, e.expansion[:45], e.icd10 or "—", e.priority_hint, e.category)
            else:
                row = (e[0], e[1][:45], e[2] or "—", e[3], e[4])
            table.add_row(*row)

    def _update_stats(self) -> None:
        s = self.mgr.get_status()
        loaded_str = ", ".join(s.loaded_modules) if s.loaded_modules else "nur Basis"
        self.query_one("#stats-bar", Static).update(
            f"Gesamt: {s.total_entries} Einträge | "
            f"Fachbereiche: {s.specialty_entries} | "
            f"Geladen: {loaded_str}"
        )

    def _update_status_display(self) -> None:
        self.query_one("#status-display", Static).update(
            self.mgr.format_status()
        )

    def _update_module_buttons(self) -> None:
        for code in SPECIALTY_MODULES:
            try:
                btn = self.query_one(f"#mod-{code}", Button)
                spec = SPECIALTY_MODULES[code]
                is_loaded = self.mgr._is_loaded(code)
                btn.label = f"{'✓' if is_loaded else '○'} {spec['icon']} [{code}] {spec['name']}"
                if is_loaded:
                    btn.remove_class("unloaded")
                    btn.add_class("loaded")
                else:
                    btn.remove_class("loaded")
                    btn.add_class("unloaded")
            except Exception:
                pass

    # --- Events ---

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        log = self.query_one("#log-panel", RichLog)

        if btn_id.startswith("mod-"):
            code = btn_id[4:]
            await self._toggle_module(code, log)

        elif btn_id.startswith("preset-"):
            code = btn_id[7:]
            await self._load_preset(code, log)

    async def _toggle_module(self, code: str, log: RichLog) -> None:
        spec = SPECIALTY_MODULES.get(code, {})
        if self.mgr._is_loaded(code):
            # Entladen
            removed = self.mgr.unload_module(code)
            log.write(
                f"[red]−[/red] [{code}] {spec.get('name','')} entfernt "
                f"({removed} Einträge)"
            )
        else:
            # Laden
            r = self.mgr.load_module(code)
            log.write(
                f"[green]+[/green] [{code}] {spec.get('name','')} geladen "
                f"(+{r.added} Einträge)"
            )
            if r.conflicts:
                log.write(
                    f"  [yellow]⚠[/yellow] {len(r.conflicts)} Konflikte "
                    f"(bestehende Einträge behalten)"
                )

        self._update_module_buttons()
        self._update_status_display()
        self._update_stats()
        self._load_table("")

    async def _load_preset(self, code: str, log: RichLog) -> None:
        preset = PRESETS.get(code, {})
        log.write(
            f"[blue]⚙[/blue] Preset [{code}] {preset.get('name','')} "
            f"wird geladen..."
        )
        results = self.mgr.load_preset(code)
        total_added = sum(r.added for r in results)
        log.write(
            f"[green]✓[/green] Preset [{code}]: "
            f"{total_added} neue Einträge über {len(results)} Module"
        )
        self._update_module_buttons()
        self._update_status_display()
        self._update_stats()
        self._load_table("")

    async def on_input_changed(self, event: Input.Changed) -> None:
        self._load_table(event.value.strip())

    # --- Hotkey Actions ---

    def action_load_all(self) -> None:
        self.run_worker(self._load_all_worker())

    async def _load_all_worker(self) -> None:
        log = self.query_one("#log-panel", RichLog)
        log.write("[blue]⚙[/blue] Lade alle Fachbereiche (FULL)...")
        results = self.mgr.load_preset("FULL")
        total = sum(r.added for r in results)
        log.write(f"[green]✓[/green] Alle Module geladen: +{total} Einträge")
        self._update_module_buttons()
        self._update_status_display()
        self._update_stats()
        self._load_table("")

    def action_export_skill(self) -> None:
        path = self.mgr.export_hermes_skill()
        log = self.query_one("#log-panel", RichLog)
        log.write(f"[green]✓[/green] Hermes SKILL.md exportiert: {path}")

    def action_refresh_status(self) -> None:
        self.mgr = CodexManager()  # Manifest neu laden
        self._update_module_buttons()
        self._update_status_display()
        self._update_stats()
        self._load_table("")

    def action_show_help(self) -> None:
        log = self.query_one("#log-panel", RichLog)
        log.write(
            "[b]Tastenkürzel:[/b]\n"
            "  [b]Ctrl+A[/b] – Alle Fachbereiche laden (FULL)\n"
            "  [b]Ctrl+E[/b] – Hermes SKILL.md exportieren\n"
            "  [b]Ctrl+R[/b] – Status aktualisieren\n"
            "  [b]Klick Fachbereich[/b] – Laden/Entladen toggle\n"
            "  [b]Klick Preset[/b] – Preset laden\n"
            "  [b]Suche[/b] – Codex-Vorschau filtern\n"
        )


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    CodexManagerApp().run()
