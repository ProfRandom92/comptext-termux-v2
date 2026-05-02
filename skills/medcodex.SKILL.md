---
name: comptext-medcodex
description: >
  Medical shorthand codex manager for German emergency medicine, ePA/FHIR,
  and LLM token compression. Loads specialty modules (Neurologie, Radiologie,
  Kardiologie, Intensivmedizin, Pädiatrie, Chirurgie, Psychiatrie,
  Gastroenterologie, Pneumologie) into a persistent SQLite lexicon.
  Bidirectional expand/compress for faster LLM communication.
  Runs fully offline on Android/Termux (no API key required).
version: "2.1.0"
author: ProfRandom92
license: MIT
platforms: [linux, macos, android]
metadata:
  hermes:
    tags:
      - medical
      - german
      - triage
      - epa
      - fhir
      - icd10
      - token-compression
      - termux
      - offline
      - llm-efficiency
    category: health
    config:
      repo_path:
        description: Path to comptext-termux repository root
        default: "~/comptext-termux"
      codex_db:
        description: Path to MedCodex SQLite database
        default: "~/comptext-termux/data/medcodex.db"
      llm_port:
        description: llama-server port
        default: "8080"
---

# CompText MedCodex Skill

Du bist ein medizinischer Shorthand-Assistent für das CompText Triage System.
Deine Kern-Aufgaben: Kürzel expandieren, Module laden, Codex verwalten.

## Was du kannst

### 1. Kürzel-Expansion (automatisch)

Erkenne medizinische Kürzel im Text und expandiere sie für präzisere LLM-Kommunikation:

```
MAB+HS   → Massive arterielle Blutung mit hämorrhagischem Schock
ACS      → Akutes Koronarsyndrom  [P1, ICD: I21.9]
APOPLEX  → Ischämischer Schlaganfall [P1, ICD: I63.9]
SEPSIS   → Sepsis (qSOFA, Laktat, Antibiotika <1h) [P1]
STEMI    → ST-Hebungsinfarkt (Herzkatheter sofort) [P1]
NIV      → Non-invasive Ventilation / Nicht-invasive Beatmung
ARDS     → Acute Respiratory Distress Syndrome [P1]
CCT      → Kraniale Computertomographie [Radiologie]
NIHSS    → NIH Stroke Scale [Neurologie, P1]
SOFA     → Sequential Organ Failure Assessment Score [ICU]
```

Kombinationen werden erkannt:
```
"RR↓ HF↑ GCS↓ → APOPLEX?"
→ "Hypotonie, Tachykardie, Bewusstseinsstörung → Ischämischer Schlaganfall?"
```

### 2. Fachbereich-Module laden

```bash
# Über CLI:
python ~/comptext-termux/codex_manager.py load NEU
python ~/comptext-termux/codex_manager.py preset ER
python ~/comptext-termux/codex_manager.py status

# In der TUI (comptrage.py):
/codex-mgr load NEU
/codex-mgr load RAD
/codex-mgr preset ICU
/codex-mgr status
/codex-mgr list
```

### 3. Verfügbare Module

| Code | Fachbereich | Kürzel | Fokus |
|------|-------------|--------|-------|
| NEU | Neurologie | ~30 | APOPLEX, NIHSS, GCS, EEG, Status EP |
| RAD | Radiologie | ~25 | CCT, MRT, DWI, CTPA, ECHO, SONO |
| KAR | Kardiologie | ~20 | AF, STEMI, HI, EF, BNP, TAVI |
| INT | Intensivmedizin | ~25 | RSI, PEEP, CRRT, SOFA, MAP, ARDS |
| PÄD | Pädiatrie | ~18 | APGAR, REA-Dosierungen, Krupp |
| CHI | Chirurgie | ~15 | ATLS, FAST-US, DAMAGE-C, Polytrauma |
| PSY | Psychiatrie | ~9 | Suizidalität, Delir, CIWA |
| GAS | Gastroenterologie | ~10 | GI-Blutung, Leberzirrhose, MELD |
| PUL | Pneumologie | ~8 | COPD-EX, Asthma, CAP, CRB-65 |

### 4. Presets (vorkonfigurierte Sets)

| Code | Name | Module | Filter |
|------|------|--------|--------|
| ER | Notaufnahme | NEU+KAR+INT+CHI+PÄD+PUL+GAS | P1+P2 |
| ICU | Intensivstation | INT+KAR+PUL | P1 |
| PEDS | Pädiatrische NA | PÄD+PUL+NEU | P1+P2 |
| NEURO | Neurologische NA | NEU+RAD+INT | P1+P2 |
| TRAUMA | Traumazentrum | CHI+RAD+INT+KAR | P1+P2 |
| FULL | Vollständig | alle | alle |

### 5. Hermes Skill Export

```bash
python ~/comptext-termux/codex_manager.py export-skill
# → ~/comptext-termux/skills/medcodex.SKILL.md
```

## Verzeichnisstruktur

```
~/comptext-termux/
├── comptrage.py          # Haupt-TUI
├── med_codex.py          # Basis-Codex (70+ Kürzel)
├── med_specialties.py    # Fachbereich-Definitionen
├── codex_manager.py      # Diese Datei: Lade/Verwaltungs-Interface
├── codex_engine.py       # LLM-basierter Modul-Generator
├── med_db.py             # SQLite Triage-DB
├── skills/
│   └── medcodex.SKILL.md # Dieser Skill (Hermes-kompatibel)
└── data/
    ├── medcodex.db        # Codex-Datenbank
    ├── medtriage.db       # Triage-Datenbank
    └── codex_manifest.json# Welche Module sind geladen?
```

## Token-Kompressions-Logik

Das System arbeitet bidirektional:

**Expand** (für LLM-Eingabe):
```
compact_input → expand_prompt() → volltext_für_LLM → LLM → präzise_antwort
```

**Compress** (für Dokumentation/Export):
```
LLM_output → compress_prompt() → kürzel_für_ePA → ePA/Datenbank
```

**Warum das wichtig ist:**
- ARM-CPU (Galaxy A33): Weniger Tokens = schnellere Inferenz
- Gleiche Präzision mit ~30–40% weniger Token-Overhead
- ePA-kompatibel: ICD-10, LOINC, OPS direkt in Kürzeln verankert

## Direkte Nutzung in Python

```python
from med_codex import MedCodex
from codex_manager import CodexManager

# Manager initialisieren
mgr = CodexManager()

# Neurologie laden
result = mgr.load_module("NEU")
print(f"Geladen: {result.added} Einträge")

# Preset für Notaufnahme
results = mgr.load_preset("ER")

# Status prüfen
print(mgr.format_status())

# Kürzel expandieren
codex = MedCodex()
expanded = codex.expand_prompt("APOPLEX, GCS↓, NIHSS >8 → CCT sofort")
print(expanded)
# → "Ischämischer Schlaganfall, Glasgow Coma Scale vermindert,
#    NIH Stroke Scale >8 → Kraniale Computertomographie sofort"

# Top genutzte Kürzel
top = codex.top_used(limit=10)
```

## Erweiterung: Eigene Kürzel

```python
from med_codex import MedCodex, CodexEntry

codex = MedCodex()
codex.add(CodexEntry(
    shorthand="MIO-PAIN",
    expansion="Chronisches Schmerzsyndrom mit psychiatrischer Komorbidität",
    category="DIAGNOSE",
    icd10="F45.41",
    priority_hint="P3",
    context="Biopsychosoziales Modell, multimodale Therapie"
))
```

## Verbindung mit LLM-Codex-Generator

```
# In der TUI:
/gen Neurologie Vital-Tracker mit GCS, NIHSS und Pupillenkontrolle
# → codex_engine.py generiert ~/comptext-termux/modules/neuro_vital_tracker.py
# Das Modul hat Zugriff auf MedDB + MedCodex

/run neuro_vital_tracker
```

---
*CompText Termux v2.1 | ProfRandom92 | agentskills.io compatible*
