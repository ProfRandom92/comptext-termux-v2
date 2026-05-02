# MedCodex – Vollständige Referenz

Alle 70+ Kürzel des medizinischen Token-Kompressions-Lexikons.

## NOTFÄLLE (P1/P2)

| Kürzel | Expansion | ICD-10 | Prio |
|--------|-----------|--------|------|
| MAB | Massive arterielle Blutung | S35.9 | P1 |
| MAB+HS | Massive arterielle Blutung mit hämorrhagischem Schock | S35.9 | P1 |
| ACS | Akutes Koronarsyndrom | I21.9 | P1 |
| AP | Anaphylaxie / Anaphylaktischer Schock | T78.2 | P1 |
| REA | Reanimation / CPR | I46.9 | P1 |
| PÄD-REA | Pädiatrische Reanimation | I46.9 | P1 |
| KKS | Kreislaufstillstand | I46.9 | P1 |
| RAU | Rauchgasinhalation | T59.8 | P2 |
| SHT | Schädel-Hirn-Trauma | S06.9 | P2 |
| SEPSIS | Sepsis | R65.2 | P1 |
| SEP-SCHOCK | Septischer Schock | R65.21 | P1 |
| PE | Lungenembolie | I26.9 | P1 |
| APO | Akutes Lungenödem | J81.0 | P1 |
| APOPLEX | Schlaganfall | I63.9 | P1 |

## DIAGNOSEN

| Kürzel | Expansion | ICD-10 | Prio |
|--------|-----------|--------|------|
| STEMI | ST-Hebungsinfarkt | I21.3 | P1 |
| NSTEMI | Non-ST-Hebungsinfarkt | I21.4 | P2 |
| VF | Kammerflimmern | I49.01 | P1 |
| VT | Ventrikuläre Tachykardie | I47.2 | P1 |

## SYMPTOME

| Kürzel | Expansion | ICD-10 | Prio |
|--------|-----------|--------|------|
| THX | Thoraxschmerz | R07.4 | P2 |
| DYSP | Dyspnoe / Atemnot | R06.0 | P2 |
| SYNK | Synkope | R55 | P2 |
| FAEB | Fieber unklarer Genese | R50.9 | P3 |
| ABD-SCHM | Abdomineller Schmerz | R10.4 | P3 |
| SCHWIN | Schwindel | R42 | P3 |
| KOPFSCHM | Kopfschmerzen | R51 | P3 |
| KRS-INST | Kreislaufinstabilität | R57.9 | P1 |

## VITALZEICHEN

| Kürzel | Bedeutung |
|--------|-----------|
| RR↓ | Hypotonie (<90/60 mmHg) |
| RR↑ | Hypertonie (>180/110 mmHg) |
| HF↑ | Tachykardie (>100/min) |
| HF↓ | Bradykardie (<60/min) |
| SpO2↓ | Hypoxämie (<90%) |
| GCS↓ | Bewusstseinsstörung |
| TEMP↑ | Fieber (>38.5°C) |

## MEDIKAMENTE

| Kürzel | Präparat | Indikation |
|--------|----------|------------|
| ADREN | Adrenalin | Anaphylaxie, REA |
| AMIO | Amiodaron | VF/VT |
| NORAD | Noradrenalin | Sepsis-Schock |
| CPAP | CPAP | Lungenödem, COPD |
| NITRO | Nitroglycerin | Lungenödem, ACS |
| HEPARIN | Heparin | PE, ACS |
| ASS | Acetylsalicylsäure | ACS 300mg |
| ATROPIN | Atropin | Bradykardie |
| MORPH | Morphin | Schmerz, Lungenödem |

## LABOR

| Kürzel | Parameter |
|--------|-----------|
| TMP | Troponin |
| LAKTAT | Blutlaktat |
| BGA | Blutgasanalyse |
| DDIM | D-Dimere |
| CREAT | Kreatinin |
| CRP | C-Reaktives Protein |
| PCT | Procalcitonin |
| CO-HB | Carboxyhämoglobin |

## SCORES

| Kürzel | Score |
|--------|-------|
| QSOFA | quick SOFA (Sepsis) |
| GCS | Glasgow Coma Scale |
| FAST | Schlaganfall-Screening |
| NEWS2 | National Early Warning Score 2 |
| CURB65 | Pneumonie-Schweregrad |

## ePA / STANDARDS

| Kürzel | Bedeutung |
|--------|-----------|
| ePA | Elektronische Patientenakte |
| FHIR | Fast Healthcare Interoperability Resources |
| ICD10 | Internationale Klassifikation der Krankheiten |
| LOINC | Labor-Identifikationsstandard |
| OPS | Operationen- und Prozedurenschlüssel |
| KIM | Kommunikation im Medizinwesen |
| TI | Telematik-Infrastruktur |

## Transport

| Kürzel | Fahrzeug |
|--------|----------|
| NAW | Notarztwagen (mit Arzt) |
| RTW | Rettungswagen |
| ITW | Intensivtransportwagen |
| HELI | Rettungshubschrauber |

## Eigene Kürzel hinzufügen

```python
from med_codex import MedCodex, CodexEntry

codex = MedCodex()
codex.add(CodexEntry(
    shorthand="MEIN-KÜRZEL",
    expansion="Volltext-Expansion",
    category="SYMPTOM",  # NOTFALL|SYMPTOM|DIAGNOSE|MEDIKAMENT|EPA|LABOR|ADMIN
    icd10="R00.0",       # oder None
    priority_hint="P2",
    context="Klinische Zusatzinfo"
))
```
