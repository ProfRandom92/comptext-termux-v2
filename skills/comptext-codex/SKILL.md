---
name: comptext-codex
description: >
  CompText Codex – token-effiziente Kommunikation mit medizinischen Kürzeln für das
  CompText Termux Triage-System. Aktiviere diesen Skill IMMER wenn:
  - medizinische Kürzel wie MAB, ACS, APOPLEX, SEPSIS, SHT, REA vorkommen
  - Triage-Bewertungen oder Notfall-Klassifikationen (P1-P5, MTS) erstellt werden sollen
  - compress_prompt() oder expand_prompt() aufgerufen werden soll
  - Fragen zu CompText, MedCodex, oder Kürzel-Expansion auftauchen
  - der Nutzer nach ICD-10-Codes im klinischen Kontext fragt
  - Pflegedokumentation oder ärztliche Briefe komprimiert werden sollen
  Kern-Prinzip: Kürzel → expand_prompt() → LLM → compress_prompt() → Dokumentation
version: 2.1.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [medizin, comptext, kuerzel, triage, notfall, ipa, komprimierung]
    category: medizin
    requires_toolsets: []
---

# CompText Codex

## Kern-Prinzip

CompText reduziert Token-Overhead durch bidirektionale Kürzel-Expansion:

```
Eingabe:  "MAB+HS, RR↓, HF↑ → ACS?"
expand:   "Massive arterielle Blutung mit hämorrhagischem Schock, Hypotonie,
           Tachykardie → Akutes Koronarsyndrom?"
compress: Antwort-Text → zurück in Kürzel für Dokumentation
```

Ziel: 30–70% Token-Reduktion je nach Fachgebiet. Besonders effektiv bei
wiederholenden Notfall-Szenarien und Triage-Kommunikation.

## Kürzel verwenden

**Bei eingehenden Nachrichten:**
1. Text auf bekannte Kürzel scannen (Großbuchstaben, oft mit + oder ↑↓)
2. `expand_prompt(text)` gedanklich anwenden → vollständigen medizinischen Kontext erschließen
3. Mit dem Volltext antworten und analysieren

**Bei ausgehenden Dokumentationen:**
1. Antwort formulieren
2. `compress_prompt(text)` anwenden wo sinnvoll
3. ICD-10 Codes ergänzen wenn angegeben

## Notfall-Kürzel Referenz (Kern-Set)

Vollständige Referenz → `references/codex_full.md`

### P1 – Kritisch (sofortiger Handlungsbedarf)

| Kürzel | Expansion | ICD-10 | Kontext |
|--------|-----------|--------|---------|
| MAB | Massive arterielle Blutung | S35.9 | Massivtransfusion, Chirurgie |
| MAB+HS | Massive arterielle Blutung + hämorrhagischer Schock | S35.9 | Volumen, MTP |
| ACS | Akutes Koronarsyndrom | I21.9 | EKG, Troponin, Katheter |
| STEMI | ST-Hebungsinfarkt | I21.3 | Katheter sofort |
| AP | Anaphylaxie | T78.2 | Adrenalin 0.3mg i.m. |
| REA | Reanimation / CPR | I46.9 | 30:2, Adrenalin alle 3-5min |
| PAED-REA | Pädiatrische Reanimation | I46.9 | 15:2, 0.01mg/kg Adrenalin |
| SEPSIS | Sepsis | R65.2 | qSOFA, Laktat, ABx <1h |
| SEP-SCHOCK | Septischer Schock | R65.21 | Norad, ICU, RR <90 |
| PE | Lungenembolie | I26.9 | CTPA, Heparin, Lyse bei Massiv-PE |
| APO | Akutes Lungenödem | J81.0 | CPAP, Nitro, Furosemid |
| APOPLEX | Ischämischer Schlaganfall | I63.9 | FAST, CT sofort, Lyse ≤4.5h |
| SHT | Schädel-Hirn-Trauma | S06.9 | GCS, CCT, Neurochirurgie |
| SAB | Subarachnoidalblutung | I60.9 | Donnerschlag-KS, CT/LP |
| ICP↑ | Erhöhter intrakranieller Druck | G93.2 | Mannitol, 30° Lagerung |
| EPL | Epileptischer Anfall / Status epilepticus | G40.9 | Diazepam, Lorazepam |
| KKS | Kreislaufstillstand | I46.9 | Sofort-REA, AED |

### P2 – Dringend

| Kürzel | Expansion | ICD-10 |
|--------|-----------|--------|
| TIA | Transiente ischämische Attacke | G45.9 |
| NSTEMI | Non-ST-Hebungsinfarkt | I21.4 |
| VHFLIMM | Vorhofflimmern | I48.0 |
| AVB3 | AV-Block III° | I44.2 |
| GBS | Guillain-Barré-Syndrom | G61.0 |
| AORTENDISS | Aortendissektion | I71.0 |
| PERIK | Perikarditis / -erguss | I30.9 |

### Symptome & Vitalzeichen

| Kürzel | Bedeutung |
|--------|-----------|
| THX | Thoraxschmerz |
| DYSP | Dyspnoe / Atemnot |
| SYNK | Synkope |
| RR↓ | Hypotonie (<90/60 mmHg) |
| RR↑ | Hypertonie (>180/110 mmHg) |
| HF↑ | Tachykardie (>100/min) |
| HF↓ | Bradykardie (<60/min) |
| SpO2↓ | Hypoxämie (<90%) |
| GCS↓ | Bewusstseinsstörung |
| TEMP↑ | Fieber (>38.5°C) |

## Triage-Klassifikation (Manchester Triage System)

Wenn Triage-Bewertung gefragt:
- **P1 KRITISCH** → sofort, <0 min (REA, STEMI, SAB, Anaphylaxie, Atemwegsobstruktion)
- **P2 SEHR DRINGEND** → 10 min (SHT schwer, APOPLEX, Sepsis, AVB3)
- **P3 DRINGEND** → 30 min (moderate Schmerzen, stabile Vitalzeichen)
- **P4 NORMAL** → 60 min (chronische Beschwerden ohne Akutverschlechterung)
- **P5 NICHT DRINGEND** → 120 min (Bagatellerkrankungen)

Format: `PRIO: [P1-P5] | BEGRÜNDUNG: [kurz] | MASSNAHMEN: [nächste Schritte]`

## CompText Termux Integration

```bash
# In comptrage.py TUI:
/expand MAB+HS          # Kürzel → Volltext
/gen Vitals-Tracker     # Neues Modul via LLM
/list                   # Alle Module anzeigen

# CLI:
python codex_manager_cli.py --status
python codex_manager_cli.py --test-compression
python codex_manager_cli.py --auto-fill neurologie --count 20
python codex_manager_cli.py --generate-skills
```

## Verification

```python
from med_codex import MedCodex
codex = MedCodex()
assert codex.count() >= 70, "Codex zu klein"
exp = codex.expand_prompt("MAB+HS, RR↓")
assert "Blutung" in exp, "Expansion fehlgeschlagen"
comp = codex.compress_prompt("Massive arterielle Blutung")
assert comp != "Massive arterielle Blutung", "Komprimierung fehlgeschlagen"
print(f"OK: {codex.count()} Einträge, Expansion: {exp[:50]}")
```

## Pitfalls

- Kürzel sind case-sensitiv: `APOPLEX` funktioniert, `apoplex` nicht
- Kombinationen wie `MAB+HS` vor Teilkürzeln `MAB` matchen
- ICD-10 Codes nur als Referenz, keine offizielle Diagnosekodierung
- Bei Offline-Betrieb (Termux ohne Internet): nur lokaler llama-server
