# comptext-termux

Medizinisches Triage-System für Android/Termux mit lokalem LLM.  
Offline-first, ePA-kompatibel, Touch-optimiert (Galaxy A33).

## Architektur

```
┌─────────────────────────────────────────────────────┐
│              Textual TUI (comptrage.py)              │
│  Quick-Events │ Freitext │ Codex-Befehle            │
└────────┬───────────┬──────────────┬─────────────────┘
         │           │              │
    ┌────▼────┐ ┌────▼────┐  ┌─────▼──────┐
    │MedCodex │ │ MedDB   │  │CodexEngine │
    │Lexikon  │ │SQLite   │  │Modul-Gen   │
    │compress/│ │Triage   │  │LLM→.py     │
    │expand   │ │History  │  │dynamisch   │
    └────┬────┘ │Palace   │  └─────┬──────┘
         │      └─────────┘        │
         └──────────────┬──────────┘
                        │
              ┌─────────▼──────────┐
              │  llama-server      │
              │  :8080 (lokal)     │
              │  MedGemma 4B GGUF  │
              └────────────────────┘
```

## Kern-Konzept: MedCodex Token-Kompression

Statt dem LLM jedes Mal "Massive arterielle Blutung mit hämorrhagischem Schock" zu schicken:

```
Eingabe:  "MAB+HS, RR↓, HF↑ → ACS?"
Expanded: "Massive arterielle Blutung mit hämorrhagischem Schock, 
           Hypotonie, Tachykardie → Akutes Koronarsyndrom?"
```

**Vorteile:**
- Weniger Tokens = schnellere Inferenz auf ARM-CPU
- ePA-kompatibel: ICD-10, LOINC, OPS integriert
- 70+ medizinische Kürzel vorinstalliert

## Setup (Ein-Kommando)

```bash
bash setup_termux.sh
```

**Manuell:**
```bash
# 1. Pakete
pkg install tur-repo && pkg update && pkg install llama-cpp
pip install textual httpx aiosqlite

# 2. MedGemma laden
cd ~/comptext-termux/models
wget https://huggingface.co/unsloth/medgemma-1.5-4b-it-GGUF/resolve/main/medgemma-1.5-4b-it-Q4_K_M.gguf

# 3. Tab 1 – Server
llama-server -m models/*.gguf --port 8080 -c 2048 -t 4

# 4. Tab 2 – App
python comptrage.py
```

## Verwendung

### Quick-Events (Hotkeys)
| Hotkey | Event |
|--------|-------|
| `B` | P1: Massivblutung |
| `H` | P1: ACS/Herzinfarkt |
| `A` | P1: Anaphylaxie |
| `S` | P1: Sepsis |
| `T` | P2: SHT/Sturz |
| `K` | P1: REA Kind |

### Codex-Befehle (im Eingabefeld)
```
/expand MAB+HS         → Kürzel aufschlüsseln
/gen Vitals-Tracker    → Neues Modul via LLM generieren
/list                  → Alle generierten Module
/run vitals_tracker    → Modul ausführen
/help                  → Alle Befehle
```

### Kürzel-Beispiele
```
MAB+HS    → Massive arterielle Blutung mit hämorrhagischem Schock
ACS       → Akutes Koronarsyndrom
SEPSIS    → Sepsis (qSOFA, Antibiotika <1h)
STEMI     → ST-Hebungsinfarkt (Herzkatheter sofort)
PÄD-REA   → Pädiatrische Reanimation (15:2)
RR↓ HF↑   → Hypotonie + Tachykardie
SpO2↓     → Hypoxämie (O2 sofort)
```

## Backend-Optionen

| Option | Setup | MedGemma | Stabilität |
|--------|-------|----------|------------|
| **A: tur-repo** (Default) | 30 Sek | ✅ | ⭐⭐⭐⭐⭐ |
| B: MediaPipe | pip install | ❌ Standard-Gemma | ⭐⭐⭐ |
| C: Build from Source | ~10 Min | ✅ | ⭐⭐⭐⭐ |

## Repo-Struktur

```
comptext-termux/
├── comptrage.py          # Haupt-TUI (Textual, Touch-optimiert)
├── med_db.py             # Async SQLite Layer + Memory Palace
├── med_codex.py          # Token-Kompressions-Lexikon (70+ Einträge)
├── codex_engine.py       # LLM-basierter Modul-Generator
├── mediapipe_server.py   # Option B: Google MediaPipe Backend
├── setup_termux.sh       # Ein-Kommando-Setup
├── docs/
│   ├── architecture.md   # Detaillierte Architektur
│   └── codex_reference.md# Alle Codex-Einträge
├── modules/              # Generierte Module (via /gen)
├── models/               # GGUF-Modelle (nicht in Git)
└── data/                 # SQLite-Datenbanken (nicht in Git)
```

## Datenbank-Backup

```bash
# JSON-Export
python -c "
import asyncio
from med_db import MedDB
db = MedDB()
asyncio.run(db.export_json('~/backup_$(date +%Y%m%d).json'))
"
```

## Zusammenhang mit CompText Codex

Dieses Repo ist der **Termux/Mobile-Zweig** des CompText-Ökosystems:

| Repo | Zweck |
|------|-------|
| [comptext-codex](https://github.com/ProfRandom92/comptext-codex) | Python DSL, PyPI, MCP-Server, CI/CD |
| **comptext-termux** | Android/Termux, lokal, Triage-UI |
| [Medgemma-CompText](https://github.com/ProfRandom92/Medgemma-CompText) | Kaggle Hackathon, ePA/FHIR |

---
*Generated: 2026-05-01 | CompText Ecosystem | ProfRandom92*
