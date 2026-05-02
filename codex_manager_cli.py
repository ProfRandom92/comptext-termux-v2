#!/usr/bin/env python3
"""
codex_manager_cli.py – CompText Codex Module Manager CLI
=========================================================
Synchronisiert fachspezifische Kürzel-Module (Neurologie, Radiologie, etc.)
in die MedCodex SQLite-Datenbank und generiert Hermes-kompatible SKILL.md Dateien.

Es gibt zwei Betriebsmodi:
- AUTHORING:  Auf PC/Server, mit Cloud-LLMs (Cerebras, Groq, DeepSeek) zum Befüllen der Module
- RUNTIME:    Auf Termux/Android, vollständig offline mit lokalem llama-server (MedGemma GGUF)

Im RUNTIME-Modus sind alle Cloud-Aufrufe deaktiviert – auch wenn --llm-url gesetzt wird.

Workflow:
    1. JSON-Export aus dem Web-Interface laden (AUTHORING)
    2. Einträge in med_codex.db schreiben (INSERT OR REPLACE)
    3. Hermes SKILL.md Dateien generieren
    4. Komprimierungs-Test gegen Referenz-Texte

Verwendung:
    python codex_manager_cli.py --status
    python codex_manager_cli.py --import-json neurologie_entries.json --specialty neurologie
    python codex_manager_cli.py --generate-skills
    python codex_manager_cli.py --test-compression
    python codex_manager_cli.py --auto-fill neurologie --count 20 --mode authoring
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Lokaler Import aus comptext-termux
sys.path.insert(0, str(Path(__file__).parent))
try:
    from med_codex import MedCodex, CodexEntry
except ImportError:
    print("FEHLER: med_codex.py nicht gefunden. Skript im comptext-termux Verzeichnis ausführen.")
    sys.exit(1)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ============================================================================
# MODUS: AUTHORING vs. RUNTIME
# ============================================================================

DEFAULT_MODE = os.environ.get("COMPTEXT_MODE", "runtime").lower()


def is_runtime_mode(mode: str) -> bool:
    return (mode or DEFAULT_MODE).lower() == "runtime"


# ============================================================================
# FACHGEBIETE
# ============================================================================
SPECIALTIES = {
    "neurologie": {
        "name": "Neurologie",
        "category": "DIAGNOSE",
        "tags": ["neuro", "schlaganfall", "epilepsie", "neurologie"],
    },
    "radiologie": {
        "name": "Radiologie",
        "category": "DIAGNOSE",
        "tags": ["röntgen", "ct", "mrt", "bildgebung"],
    },
    "kardiologie": {
        "name": "Kardiologie",
        "category": "DIAGNOSE",
        "tags": ["herz", "kardial", "koronar"],
    },
    "paediatrie": {
        "name": "Pädiatrie",
        "category": "DIAGNOSE",
        "tags": ["kind", "neonatal", "pädiatrie"],
    },
    "intensiv": {
        "name": "Intensivmedizin",
        "category": "DIAGNOSE",
        "tags": ["icu", "intensiv", "beatmung"],
    },
    "chirurgie": {
        "name": "Chirurgie",
        "category": "DIAGNOSE",
        "tags": ["op", "chirurgie"],
    },
    "innere": {
        "name": "Innere Medizin",
        "category": "DIAGNOSE",
        "tags": ["internistisch", "metabolisch"],
    },
    "psychiatrie": {
        "name": "Psychiatrie",
        "category": "DIAGNOSE",
        "tags": ["psychisch", "mental"],
    },
    "anaesthesie": {
        "name": "Anästhesie",
        "category": "MEDIKAMENT",
        "tags": ["narkose", "anästhesie", "schmerz"],
    },
    "orthopaedie": {
        "name": "Orthopädie/Unfallchirurgie",
        "category": "DIAGNOSE",
        "tags": ["knochen", "fraktur", "gelenk"],
    },
}

# Referenz-Texte für Komprimierungstest (CompText-Kern)
COMPRESSION_TEST_TEXTS = [
    "Patient mit massiver arterieller Blutung und hämorrhagischem Schock, Blutdruck erniedrigt, Herzfrequenz erhöht, Sauerstoffsättigung normal.",
    "Akutes Koronarsyndrom mit Thoraxschmerz und Dyspnoe. EKG zeigt ST-Hebungsinfarkt. Troponin erhöht. Herzkatheter sofort.",
    "Schädel-Hirn-Trauma nach Sturz. Glasgow Coma Scale vermindert. CT-Schädel angeordnet. Neurochirurgie informiert.",
    "Subarachnoidalblutung mit Donnerschlagkopfschmerz. Kraniales CT sofort. Neurologiekonsil.",
    "Pädiatrische Reanimation. Kind ohne Spontanatmung. CPR läuft 15:2.",
]


# ============================================================================
# IMPORT
# ============================================================================

def import_from_json(json_path: Path, specialty: str, codex: MedCodex, dry_run: bool = False) -> int:
    """Importiert JSON-Einträge aus dem Web-Manager in die SQLite-DB."""
    with open(json_path, encoding="utf-8") as f:
        entries = json.load(f)

    if not isinstance(entries, list):
        print(f"FEHLER: Erwartet JSON-Array, bekommen: {type(entries)}")
        return 0

    sp_info = SPECIALTIES.get(specialty, {"name": specialty, "category": "DIAGNOSE"})
    count = 0

    for e in entries:
        shorthand = e.get("shorthand", "").strip().upper()
        expansion = e.get("expansion", "").strip()
        if not shorthand or not expansion:
            continue

        entry = CodexEntry(
            shorthand=shorthand,
            expansion=expansion,
            category=sp_info["category"],
            icd10=e.get("icd10"),
            priority_hint=e.get("prio", "P4"),
            context=e.get("context"),
        )

        if dry_run:
            print(f"  [DRY] {shorthand:16} → {expansion[:50]}")
        else:
            codex.add(entry)
            print(f"  ✓ {shorthand:16} → {expansion[:50]}")
        count += 1

    return count


def import_from_dict(entries: list[dict], specialty: str, codex: MedCodex) -> int:
    """Importiert Einträge direkt aus einem Dict (für auto-fill)."""
    sp_info = SPECIALTIES.get(specialty, {"name": specialty, "category": "DIAGNOSE"})
    count = 0
    for e in entries:
        shorthand = e.get("shorthand", "").strip().upper()
        expansion = e.get("expansion", "").strip()
        if not shorthand or not expansion:
            continue
        entry = CodexEntry(
            shorthand=shorthand,
            expansion=expansion,
            category=sp_info["category"],
            icd10=e.get("icd10"),
            priority_hint=e.get("prio", "P4"),
            context=e.get("context"),
        )
        codex.add(entry)
        count += 1
    return count


# ============================================================================
# HERMES SKILL GENERATOR
# ============================================================================

# (unverändert gelassen)

def generate_skill_md(specialty_id: str, entries: list[CodexEntry]) -> str:
    """Generiert eine Hermes-kompatible SKILL.md."""
    sp = SPECIALTIES.get(specialty_id, {"name": specialty_id, "tags": [specialty_id]})
    name = sp["name"]
    tags = sp.get("tags", [specialty_id])

    p1 = [e for e in entries if e.priority_hint == "P1"]
    p2 = [e for e in entries if e.priority_hint == "P2"]
    rest = [e for e in entries if e.priority_hint not in ("P1", "P2")]

    def entry_line(e: CodexEntry) -> str:
        icd = f" [{e.icd10}]" if e.icd10 else ""
        ctx = f" – {e.context}" if e.context else ""
        return f"  {e.shorthand:<14} → {e.expansion}{icd}{ctx}"

    blocks = []
    if p1:
        blocks.append("### P1 – Notfall\n" + "\n".join(entry_line(e) for e in p1))
    if p2:
        blocks.append("### P2 – Dringend\n" + "\n".join(entry_line(e) for e in p2))
    if rest:
        blocks.append("### P3/P4 – Elektiv\n" + "\n".join(entry_line(e) for e in rest))

    codex_block = "\n\n".join(blocks) if blocks else "  (leer)"

    first = entries[0].shorthand if entries else "KÜRZEL"

    return f"""---
name: medcodex-{specialty_id}
description: MedCodex Kürzel-Wissen für {name} – token-effiziente LLM-Kommunikation (CompText)
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [{', '.join(tags)}, medizin, comptext, kuerzel]
    category: medizin
---

# MedCodex – {name}

## When to Use

Aktiviere diesen Skill wenn medizinische Kommunikation oder Dokumentation
im Bereich {name} stattfindet. Der Skill enthält das komprimierte Kürzel-Lexikon
für token-effiziente Kommunikation mit dem lokalen LLM (CompText-Codex-Prinzip).

**Kernprinzip**: Kürzel → expand_prompt() → LLM → compress_prompt() → Doku

## Kürzel-Codex ({len(entries)} Einträge)

{codex_block}

## Procedure

1. Eingehenden Text scannen: enthält er Kürzel aus dem Codex oben?
2. `expand_prompt(text)` aufrufen → Volltext für LLM-Eingabe
3. LLM-Antwort mit `compress_prompt(text)` re-komprimieren für Dokumentation
4. Bei unbekannten Kürzeln: `/expand KÜRZEL` in CompText-TUI

## Pitfalls

- Kürzel sind case-sensitiv: `APOPLEX` ≠ `apoplex`
- Kombinationen wie `MAB+HS` matchen vor Teilkürzeln `MAB`
- Nicht für ICD-10 Diagnosekodierung verwenden (nur Referenz)

"""


def generate_all_skills(codex: MedCodex, output_dir: Path) -> None:
    """Generiert SKILL.md für alle Fachgebiete."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for specialty_id, sp_info in SPECIALTIES.items():
        entries = codex.search("", limit=1000)  # alle holen
        # Filtern nach Fachgebiet-Tags (rudimentär über context/category)
        sp_entries = [e for e in entries
                      if any(tag.lower() in (e.context or "").lower()
                             or tag.lower() in e.expansion.lower()
                             for tag in sp_info.get("tags", []))]

        if not sp_entries:
            continue

        skill_dir = output_dir / "medizin" / specialty_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(generate_skill_md(specialty_id, sp_entries), encoding="utf-8")
        print(f"  ✓ {skill_path} ({len(sp_entries)} Einträge)")


# ============================================================================
# KOMPRIMIERUNGS-TEST (CompText-Kern)
# ============================================================================

# (unverändert)

def run_compression_test(codex: MedCodex) -> dict:
    """Testet das CompText-Kern-Prinzip."""
    results = []
    print("\n" + "═" * 60)
    print("COMPTEXT KOMPRIMIERUNGS-TEST")
    print("═" * 60)

    for i, text in enumerate(COMPRESSION_TEST_TEXTS, 1):
        compressed = codex.compress_prompt(text)
        expanded_back = codex.expand_prompt(compressed)

        orig_tokens = len(text.split())
        comp_tokens = len(compressed.split())
        reduction = (1 - comp_tokens / orig_tokens) * 100 if orig_tokens > 0 else 0

        result = {
            "original": text,
            "compressed": compressed,
            "orig_tokens": orig_tokens,
            "comp_tokens": comp_tokens,
            "reduction_pct": round(reduction, 1),
        }
        results.append(result)

        status = "✓" if reduction > 5 else "~"
        print(f"\n[Test {i}] {status} {reduction:.1f}% Reduktion")
        print(f"  Original  ({orig_tokens:2d} Tokens): {text[:70]}")
        print(f"  Komprimiert ({comp_tokens:2d} Tokens): {compressed[:70]}")

    avg_reduction = sum(r["reduction_pct"] for r in results) / len(results)
    print(f"\n{'═' * 60}")
    print(f"GESAMT: Ø {avg_reduction:.1f}% Token-Reduktion | {len(results)} Texte getestet")
    print(f"Codex: {codex.count()} Einträge | Top-Kürzel: {', '.join(s for s, _ in codex.top_used(5))}")
    print("═" * 60)

    return {"avg_reduction": avg_reduction, "results": results}


# ============================================================================
# STATUS
# ============================================================================

# (unverändert)

def print_status(codex: MedCodex) -> None:
    """Zeigt den aktuellen Codex-Status."""
    total = codex.count()
    top = codex.top_used(10)

    print("\n" + "═" * 60)
    print("COMPTEXT CODEX STATUS")
    print("═" * 60)
    print(f"Gesamt-Einträge: {total}")
    print(f"Datenbank:       {codex.db_path}")

    for cat in ["NOTFALL", "DIAGNOSE", "SYMPTOM", "MEDIKAMENT", "LABOR", "EPA", "ADMIN"]:
        entries = codex.list_by_category(cat)
        if entries:
            print(f"  {cat:<12} {len(entries):3d} Einträge")

    if top:
        print(f"\nTop-Kürzel (Nutzung):")
        for shorthand, count in top:
            entry = codex.get(shorthand)
            print(f"  {shorthand:<14} {count:4d}x  → {entry.expansion[:40] if entry else '?'}")

    print("═" * 60)


# ============================================================================
# AUTO-FILL VIA LLM (Autor vs Runtime)
# ============================================================================

async def auto_fill_specialty(
    specialty_id: str,
    codex: MedCodex,
    count: int = 20,
    llm_url: str = "http://127.0.0.1:8080",
    mode: str = DEFAULT_MODE,
) -> int:
    """
    Füllt ein Fachgebiet automatisch mit LLM-generierten Kürzeln.

    - Im AUTHORING-Modus: Cloud-Backends erlaubt (llm_url != localhost)
    - Im RUNTIME-Modus: Nur lokaler llama-server, keine Cloud-Aufrufe
    """
    if not HAS_HTTPX:
        print("FEHLER: httpx nicht installiert. pip install httpx")
        return 0

    runtime = is_runtime_mode(mode)

    # Sicherheitsnetz: Im Runtime-Modus nie Cloud-URLs verwenden
    if runtime:
        if not llm_url.startswith("http://127.0.0.1") and not llm_url.startswith("http://localhost"):
            print("RUNTIME-MODUS: Cloud-URL ignoriert, verwende lokalen llama-server (http://127.0.0.1:8080)")
        llm_url = "http://127.0.0.1:8080"

    sp = SPECIALTIES.get(specialty_id, {"name": specialty_id})
    existing = [e.shorthand for e in codex.search("", limit=5000)
                if any(t in (e.context or "").lower() or t in e.expansion.lower()
                       for t in sp.get("tags", [specialty_id]))]

    prompt = (
        f'Du bist ein medizinischer Terminologie-Experte.\n'
        f'Erstelle {count} medizinische Kürzel für das Fachgebiet "{sp["name"]}" im deutschen klinischen Alltag.\n'
        f'{("Bereits vorhanden (nicht wiederholen): " + ", ".join(existing[:20])) if existing else ""}\n\n'
        f'Antworte NUR als JSON-Array:\n'
        f'[\n  {{"shorthand": "KÜRZEL", "expansion": "Volltext-Beschreibung", "icd10": "X00.0 oder null", "prio": "P1-P4", "context": "Klinische Info"}}\n]\n\n'
        f'Prio: P1=Notfall, P2=Dringend, P3=Akut, P4=Elektiv. Kürzel 2-12 Zeichen, Großbuchstaben.'
    )

    raw = ""

    # Versuch 1: Lokaler llama-server (immer erlaubt)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{llm_url}/completion",
                json={"prompt": prompt, "n_predict": 1200, "temperature": 0.3,
                      "stop": ["\n\n\n"]},
            )
            r.raise_for_status()
            raw = r.json().get("content", "")
            print(f"  → LLM verwendet ({llm_url}) [mode={mode}]")
    except Exception as e:
        if runtime:
            print(f"  FEHLER: RUNTIME-Modus und lokaler LLM nicht erreichbar: {e}")
            return 0

        # AUTHORING-Modus: Cloud-Backends als Fallback zulassen
        print(f"  → Lokaler LLM nicht erreichbar, versuche Cloud-Backend (AUTHORING-Modus)...")
        try:
            # Beispiel: Groq / Cerebras / DeepSeek könnte hier angeschlossen werden
            # Placeholder: derzeit kein generischer Cloud-Client implementiert
            print("  WARNUNG: Cloud-Fallback ist noch nicht implementiert. Bitte llm_url lokal halten.")
            return 0
        except Exception as e2:
            print(f"  FEHLER: Kein LLM verfügbar: {e2}")
            return 0

    # JSON parsen
    json_match = re.search(r"\[[\s\S]*?\]", raw)
    if not json_match:
        print(f"  FEHLER: Kein JSON in Antwort gefunden")
        return 0

    try:
        entries = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        print(f"  FEHLER: JSON-Parse: {e}")
        return 0

    imported = import_from_dict(entries, specialty_id, codex)
    return imported


# ============================================================================
# ENTRY POINT
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="CompText Codex Module Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Beispiele:
  python codex_manager_cli.py --status
  python codex_manager_cli.py --import-json neurologie.json --specialty neurologie
  python codex_manager_cli.py --auto-fill neurologie --count 20 --mode authoring
  python codex_manager_cli.py --auto-fill all --count 15 --mode authoring
  python codex_manager_cli.py --generate-skills --output ~/.hermes/skills
  python codex_manager_cli.py --test-compression
  python codex_manager_cli.py --export-json ~/codex_backup.json
        """,
    )

    parser.add_argument("--status", action="store_true", help="Codex-Status anzeigen")
    parser.add_argument("--import-json", metavar="FILE", help="JSON-Datei importieren")
    parser.add_argument("--specialty", metavar="ID", choices=list(SPECIALTIES.keys()) + ["all"],
                        help="Fachgebiet ID")
    parser.add_argument("--dry-run", action="store_true", help="Import simulieren ohne zu schreiben")
    parser.add_argument("--auto-fill", metavar="SPECIALTY",
                        help="Fachgebiet via LLM befüllen ('all' für alle)")
    parser.add_argument("--count", type=int, default=20,
                        help="Anzahl Einträge pro Fachgebiet (default: 20)")
    parser.add_argument("--generate-skills", action="store_true",
                        help="Hermes SKILL.md Dateien generieren")
    parser.add_argument("--output", metavar="DIR", default="./hermes-skills",
                        help="Ausgabeverzeichnis für Skills")
    parser.add_argument("--test-compression", action="store_true",
                        help="CompText Komprimierungs-Test ausführen")
    parser.add_argument("--export-json", metavar="FILE",
                        help="Alle Codex-Einträge als JSON exportieren")
    parser.add_argument("--llm-url", default="http://127.0.0.1:8080",
                        help="llama-server URL (default: http://127.0.0.1:8080)")
    parser.add_argument("--db", default="~/comptext-termux/data/medcodex.db",
                        help="Pfad zur Codex-Datenbank")
    parser.add_argument("--mode", choices=["authoring", "runtime"], default=DEFAULT_MODE,
                        help="Betriebsmodus: authoring (Cloud erlaubt) oder runtime (offline, nur lokal)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    codex = MedCodex(db_path=args.db)

    if args.status:
        print_status(codex)

    if args.import_json:
        path = Path(args.import_json)
        if not path.exists():
            print(f"FEHLER: Datei nicht gefunden: {path}")
            sys.exit(1)
        specialty = args.specialty or "unknown"
        print(f"\nImportiere '{path}' → Fachgebiet: {specialty}")
        n = import_from_json(path, specialty, codex, dry_run=args.dry_run)
        print(f"{'[DRY] ' if args.dry_run else ''}Importiert: {n} Einträge")

    if args.auto_fill:
        targets = list(SPECIALTIES.keys()) if args.auto_fill == "all" else [args.auto_fill]
        for sp_id in targets:
            sp_name = SPECIALTIES.get(sp_id, {}).get("name", sp_id)
            print(f"\nAuto-Fill: {sp_name} ({args.count} Kürzel) [mode={args.mode}]...")
            n = asyncio.run(auto_fill_specialty(sp_id, codex, args.count, args.llm_url, args.mode))
            print(f"  ✓ {n} neue Einträge hinzugefügt")

        print(f"\nGesamt nach Auto-Fill: {codex.count()} Einträge")

    if args.generate_skills:
        out = Path(args.output).expanduser()
        print(f"\nGeneriere Hermes Skills → {out}")
        generate_all_skills(codex, out)
        print(f"Skills generiert in: {out}")

    if args.test_compression:
        run_compression_test(codex)

    if args.export_json:
        out = Path(args.export_json).expanduser()
        with sqlite3.connect(str(codex.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, expansion, category, icd10, priority_hint, context, usage_count "
                "FROM codex ORDER BY category, shorthand"
            ).fetchall()
        data = [
            {"shorthand": r[0], "expansion": r[1], "category": r[2],
             "icd10": r[3], "priority_hint": r[4], "context": r[5],
             "usage_count": r[6]}
            for r in rows
        ]
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nExportiert: {len(data)} Einträge → {out}")


if __name__ == "__main__":
    main()
