---
name: medcodex-filler
description: Befüllt MedCodex-Fachbereichs-Module automatisch mit medizinischen Kürzeln. Lädt Neurologie, Radiologie, Kardiologie etc. in die SQLite-DB. Nutze diesen Skill wenn du einen neuen Fachbereich zum Codex hinzufügen willst oder bestehende Module erweitern möchtest.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [medical, codex, termux, comptext, sqlite, nlp]
    category: medical
    requires_toolsets: [terminal]
---

# MedCodex Filler – Fachbereichs-Module automatisch befüllen

## Was dieser Skill tut

Lädt medizinische Fachbereichs-Kürzel automatisch in die MedCodex SQLite-Datenbank.
Jeder Fachbereich hat sein eigenes Modul mit spezialisierten Kürzeln für:
- Symptome und Befunde des Fachbereichs
- ICD-10/LOINC/OPS-Codes
- Spezifische Medikamente und Maßnahmen
- Radiologische/diagnostische Kürzel
- ePA-konforme Dokumentationskürzel

## Verfügbare Fachbereiche

| Modul | Datei | Status |
|-------|-------|--------|
| Neurologie | skills/medical/neurologie/codex_data.py | ✅ |
| Radiologie | skills/medical/radiologie/codex_data.py | ✅ |
| Kardiologie | skills/medical/kardiologie/codex_data.py | ✅ |
| Intensivmedizin | skills/medical/intensivmedizin/codex_data.py | ✅ |
| Pädiatrie | skills/medical/pädiatrie/codex_data.py | ✅ |

## Procedure

### 1. Fachbereich identifizieren
Der User nennt einen Fachbereich (z.B. "lade Neurologie" oder "füge Radiologie hinzu").

### 2. Modul laden und ausführen
```bash
cd ~/comptext-termux
python codex_manager.py fill --specialty neurologie
# oder alle auf einmal:
python codex_manager.py fill --all
```

### 3. Verifikation
```bash
python codex_manager.py stats
python codex_manager.py search "MRT"
```

### 4. Im Triage-System testen
In der TUI: `/expand MRT-ISCHÄMIE` → sollte Volltext zurückgeben

## Interface starten

```bash
python codex_manager.py ui
```
Öffnet das Textual-Interface für Fachbereichs-Verwaltung.

## Neuen Fachbereich erstellen

```bash
python codex_manager.py new --name "Gastroenterologie"
# Agent füllt automatisch via lokalem LLM
```

## Pitfalls

- Kürzel müssen UNIQUE sein (shorthand ist PRIMARY KEY)
- Duplikate werden mit `INSERT OR REPLACE` behandelt (neuerer Eintrag gewinnt)
- Kategorien: NOTFALL | SYMPTOM | DIAGNOSE | MEDIKAMENT | EPA | LABOR | ADMIN | BILDGEBUNG | SCORE
- ICD-10 Format: "G35" nicht "G035" (kein führendes Null-Padding bei zweistelligen Codes)

## Verification

```bash
python -c "
from med_codex import MedCodex
c = MedCodex()
print(f'Total: {c.count()} Einträge')
neuro = c.list_by_category('NEUROLOGIE')
print(f'Neurologie: {len(neuro)} Einträge')
print(c.expand_prompt('MRT-ISCHÄMIE, NIHSS, tPA'))
"
```
