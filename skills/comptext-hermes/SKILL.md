---
name: comptext-hermes
description: >
  CompText Hermes – Haupt-Orchestrierungs-Skill für das gesamte CompText Termux Ökosystem.
  Aktiviere diesen Skill IMMER wenn:
  - Fragen zum CompText-Projekt, comptext-codex (PyPI), comptext-termux, Medgemma-CompText auftauchen
  - neue Hermes Skills für Fachgebiete (Neurologie, Radiologie etc.) erstellt oder befüllt werden sollen
  - codex_manager_cli.py Befehle erklärt oder ausgeführt werden sollen
  - das gesamte Ökosystem (5 Repos) beschrieben oder erweitert werden soll
  - autonome Skill-Generierung für medizinische Spezialgebiete gestartet werden soll
  - comptrage.py TUI-Fragen, Codex-Engine, MedDB oder Memory Palace gefragt werden
  - Benchmarks für Token-Komprimierung ausgewertet werden sollen
  Dieser Skill kennt alle Repos, die Architektur und die Schnittstellen des Projekts.
version: 2.1.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [comptext, hermes, medizin, termux, codex, orchestrierung, skills]
    category: medizin
    requires_toolsets: []
---

# CompText Hermes – Orchestrierungs-Skill

## Ökosystem-Übersicht

```
CompText Ecosystem (ProfRandom92)
├── comptext-codex          PyPI: comptext-codex | 2800+ LOC | 185/185 Tests
│   ├── Python DSL für token-effiziente LLM-Kommunikation
│   ├── MCP Server, CI/CD, Docker, REST API
│   └── Benchmark: ~30% netto, 64-73% bei Agent-Handoff
│
├── comptext-termux         Android/Termux | Offline-first | Galaxy A33
│   ├── comptrage.py        Textual TUI, Touch-optimiert, 6 Quick-Events
│   ├── med_codex.py        70+ Kürzel, bidirektional, SQLite
│   ├── med_db.py           Async SQLite, Memory Palace Schema
│   ├── codex_engine.py     LLM-basierter Modul-Generator
│   └── codex_manager_cli.py CLI-Sync, Hermes-Export, Komprimierungstest
│
├── Medgemma-CompText       Kaggle Hackathon | KVTC Sandwich Architektur
│   ├── PHI-Scrubbing (spaCy de_core_news_sm + Regex)
│   ├── ePA/FHIR R4 (§341 SGB V, LOINC, ICD-10)
│   ├── 78/78 Tests | Vercel Frontend
│   └── Huxley-Gödel Sicherheitsmuster
│
├── comptext-mcp-server     MCP Bridge | Claude Integration
└── comptext-dsl            DSL-Spezifikation
```

## Hermes Skills Struktur

Alle Skills leben in `~/.hermes/skills/medizin/`:

```
~/.hermes/skills/medizin/
├── comptext-hermes/        ← dieser Skill (Orchestrierung)
│   ├── SKILL.md
│   └── references/
│       ├── ecosystem.md    Vollständige Repo-Doku
│       └── api_reference.md CLI + Python API
├── comptext-codex/         ← Kürzel-Lexikon (70+ Einträge)
│   └── SKILL.md
├── comptext-epa/           ← ePA/FHIR Dokumentation
│   └── SKILL.md
└── {fachgebiet}/           ← Auto-generiert via codex_manager_cli.py
    └── SKILL.md
```

## Fachgebiet-Skills automatisch erstellen

### Via CLI (empfohlen für Batch)

```bash
cd ~/comptext-termux

# Einzelnes Fachgebiet befüllen + Skill generieren
python codex_manager_cli.py --auto-fill neurologie --count 20
python codex_manager_cli.py --generate-skills --output ~/.hermes/skills

# Alle 12 Fachgebiete auf einmal (dauert ~3 Minuten)
python codex_manager_cli.py --auto-fill all --count 15
python codex_manager_cli.py --generate-skills --output ~/.hermes/skills

# Status und Komprimierungstest
python codex_manager_cli.py --status
python codex_manager_cli.py --test-compression

# Export für Backup
python codex_manager_cli.py --export-json ~/codex_backup_$(date +%Y%m%d).json
```

### Via Codex Manager Interface (Web)

Das HTML-Interface im Chat generiert Skills direkt und ermöglicht:
- Pro Fachgebiet: "Auto-Fill" → Anthropic API → JSON → SQLite
- "Hermes Skill" Tab → SKILL.md generiert und kopierbar
- "Auto-Fill: Alle Fachgebiete" → sequentiell alle 12, Live-Log

### Via comptrage.py TUI

```
/gen Neurologie-Protokoll   → LLM generiert Python-Modul
/list                        → Alle generierten Module
/run neurologie_protokoll    → Modul ausführen
```

## Neuen Skill für Fachgebiet schreiben

Template für ein neues Fachgebiet (z.B. Dermatologie):

```markdown
---
name: medcodex-dermatologie
description: >
  MedCodex Dermatologie – Kürzel für Hauterkrankungen. Aktiviere bei:
  Dermatologie, Hautkrankheiten, Psoriasis, Ekzem, Melanom, Wundversorgung.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [dermatologie, haut, wunde, comptext, medizin]
    category: medizin
---

# MedCodex – Dermatologie

## Kürzel-Codex

### P1 – Notfall
  ANGIO-ÖDEM    → Angioödem [T78.3] | Atemweg, Adrenalin
  TEN           → Toxische epidermale Nekrolyse [L51.2] | ICU, Verbrennung

### P2 – Dringend
  ERYSIPEL      → Erysipel / Wundrose [A46] | Penicillin i.v.
  ...

## Verification
\`\`\`python
from med_codex import MedCodex
codex = MedCodex()
assert codex.get('ERYSIPEL') is not None
\`\`\`
```

## Codex-Engine: Autonome Modul-Generierung

Der `CodexEngine` in `codex_engine.py` generiert Python-Module via lokalem LLM:

```python
from codex_engine import CodexEngine
import asyncio

async def main():
    engine = CodexEngine()
    # Modul für spezifisches klinisches Problem generieren
    mod = await engine.generate_module(
        "Vitals-Tracker: RR, Puls, SpO2 mit Trendanalyse und Alarm bei P1-Werten"
    )
    print(f"Erstellt: {mod.file_path}")
    result = await engine.run_module(mod.name)
    print(result)

asyncio.run(main())
```

Generierte Module haben immer:
- `class Module:` mit `__init__(self, db)` und `run(*args) -> dict`
- Zugriff auf `self.db` (MedDB Instanz)
- Return: `{"status": "ok"|"error", "data": {...}}`

## Memory Palace (MedDB)

Hierarchische Wissensspeicherung in SQLite:

```python
from med_db import MedDB
import asyncio

async def main():
    db = MedDB()
    await db.init_schema()

    # Speichern: [[Palace:Wing:Room]]
    await db.palace_remember(
        palace="Neurologie",
        wing="Schlaganfall",
        room="Lyse-Protokoll",
        content="rtPA 0.9mg/kg, max 90mg, 10% als Bolus, Rest über 60min"
    )

    # Abrufen
    loci = await db.palace_recall("Neurologie", "Schlaganfall")
    for l in loci:
        print(f"[{l['wing']}:{l['room']}] {l['content']}")

asyncio.run(main())
```

## CompText Benchmarks

Aktuelle Messwerte (aus `codex_manager_cli.py --test-compression`):

| Szenario | Token-Reduktion |
|----------|----------------|
| Einzelkürzel (MAB+HS) | 65-70% gross |
| Triage-Notiz (P1-Fall) | 40-50% |
| Arztbrief-Abschnitt | 25-35% |
| Vollständiger Entlassbrief | 15-25% |
| Agent-Handoff (Kontext) | 64-73% |
| Amortisiert mit Overhead | ~30% netto |

## Verification

```bash
# Alle Tests laufen lassen
cd ~/comptext-termux
python -m pytest med_codex.py -v 2>/dev/null || python -c "
from med_codex import MedCodex
from med_db import MedDB
import asyncio

codex = MedCodex()
assert codex.count() >= 70
assert 'Blutung' in codex.expand_prompt('MAB')
assert codex.compress_prompt('Massive arterielle Blutung') != 'Massive arterielle Blutung'

async def test_db():
    db = MedDB()
    await db.init_schema()
    stats = await db.get_stats()
    assert 'total_cases' in stats

asyncio.run(test_db())
print('ALLE TESTS BESTANDEN')
print(f'Codex: {codex.count()} Einträge')
print(f'Komprimierung: {codex.top_used(3)}')
"
```

## Pitfalls & bekannte Einschränkungen

- llama-server muss auf :8080 laufen für comptrage.py und auto-fill offline
- Anthropic API als Fallback wenn kein lokaler Server erreichbar
- comptext-codex (PyPI) und comptext-termux sind getrennte Repos — Kürzel nicht automatisch synchron
- Memory Palace wird nicht automatisch gesichert — manueller JSON-Export nötig
- scrub() IMMER vor compress() im MedGemma-Kontext (Huxley-Gödel Pattern)
