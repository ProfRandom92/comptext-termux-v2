---
name: comptext-epa
description: >
  CompText ePA – Elektronische Patientenakte Dokumentationsworkflow für das deutsche
  Gesundheitssystem. Aktiviere diesen Skill IMMER wenn:
  - ePA, FHIR, Telematikinfrastruktur (TI), Gematik erwähnt werden
  - FHIR R4 Ressourcen erstellt oder validiert werden sollen (Patient, Observation, Condition, MedicationStatement)
  - ICD-10-GM, OPS, LOINC, SNOMED Codes gefragt werden
  - Arztbriefe, Entlassungsbriefe, Pflegeberichte für die ePA strukturiert werden sollen
  - §341 SGB V, KIM, MIO, KVDT, eAU erwähnt werden
  - medizinische Dokumente in FHIR-konforme Strukturen umgewandelt werden sollen
  - PHI-Scrubbing / Anonymisierung für Patientendaten gefragt wird
  Eng verwandt mit comptext-codex: Kürzel erst expandieren, dann ePA-Struktur anwenden.
version: 2.1.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [epa, fhir, gematik, icd10, medizin, comptext, ti, dokumentation]
    category: medizin
    requires_toolsets: []
---

# CompText ePA – Elektronische Patientenakte

## Übersicht

Workflow für ePA-konforme Dokumentation im CompText Ökosystem.
Grundprinzip: CompText-Kürzel expandieren → strukturieren → FHIR-Ressource → ePA.

```
Klinischer Text (Kürzel)
        ↓ expand_prompt()
    Volltext
        ↓ PHI-Scrubbing (de_core_news_sm + Regex)
  Anonymisierter Text
        ↓ FHIR-Mapping
   FHIR R4 Ressource
        ↓ §341 SGB V
       ePA Upload
```

## FHIR R4 Ressourcen-Mapping

### Patient

```json
{
  "resourceType": "Patient",
  "id": "pat-001",
  "meta": { "profile": ["https://fhir.kbv.de/StructureDefinition/KBV_PR_Base_Patient"] },
  "identifier": [{ "system": "http://fhir.de/sid/gkv/kvid-10", "value": "A123456789" }],
  "name": [{ "use": "official", "family": "ANONYMISIERT", "given": ["ANONYMISIERT"] }],
  "birthDate": "YYYY-MM-DD",
  "gender": "male|female|other|unknown"
}
```

### Condition (Diagnose mit ICD-10-GM)

```json
{
  "resourceType": "Condition",
  "clinicalStatus": { "coding": [{ "code": "active" }] },
  "code": {
    "coding": [{
      "system": "http://fhir.de/CodeSystem/dimdi/icd-10-gm",
      "code": "I21.3",
      "display": "Akuter transmuraler Myokardinfarkt der Vorderwand"
    }]
  },
  "severity": { "coding": [{ "code": "24484000", "display": "Severe" }] },
  "subject": { "reference": "Patient/pat-001" },
  "recordedDate": "2026-05-01"
}
```

### Observation (Vitalzeichen mit LOINC)

Häufig verwendete LOINC-Codes:

| Parameter | LOINC | Einheit |
|-----------|-------|---------|
| Herzfrequenz | 8867-4 | /min |
| Blutdruck systolisch | 8480-6 | mmHg |
| Blutdruck diastolisch | 8462-4 | mmHg |
| Sauerstoffsättigung | 59408-5 | % |
| Körpertemperatur | 8310-5 | °C |
| GCS gesamt | 9269-2 | Score |
| Troponin | 6598-7 | ng/L |
| Laktat | 2519-9 | mmol/L |

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": { "coding": [{ "system": "http://loinc.org", "code": "8867-4", "display": "Herzfrequenz" }] },
  "subject": { "reference": "Patient/pat-001" },
  "effectiveDateTime": "2026-05-01T10:30:00+02:00",
  "valueQuantity": { "value": 110, "unit": "/min", "system": "http://unitsofmeasure.org", "code": "/min" }
}
```

## PHI-Scrubbing Workflow

Pflicht vor ePA-Upload: personenbezogene Daten entfernen.

**Reihenfolge (MedGemma × CompText Architektur):**
1. Regex zuerst (vor NER) → verhindert Fehlklassifikation medizinischer Terme als Namen
2. NER (spaCy `de_core_news_sm`) für verbleibende Entitäten
3. Manuelle Prüfung kritischer Felder

**Regex-Muster (Deutsch):**
```python
PHI_PATTERNS = {
    "kvnr":        r"\b[A-Z]\d{9}\b",
    "geburtsdatum":r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",
    "telefon":     r"\b(\+49|0)\s?[\d\s\-\/]{7,15}\b",
    "email":       r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "name_vor_geb":r"(?i)(geb(?:oren)?\.?\s+am|patient(?:in)?:?)\s+([A-ZÄÖÜ][a-zäöüß]+ [A-ZÄÖÜ][a-zäöüß]+)",
    "strasse":     r"\b[A-ZÄÖÜ][a-zäöüß]+(?:strasse|straße|str\.|weg|gasse|platz)\s+\d+\b",
    "plz":         r"\b[0-9]{5}\s+[A-ZÄÖÜ][a-zäöüß]+\b",
}
```

**Huxley-Gödel Sicherheitsmuster** (aus MedGemma × CompText):
```python
def scrub_then_compress(text: str) -> str:
    """NIEMALS compress() vor scrub() aufrufen."""
    scrubbed = scrub(text)      # PHI entfernen
    compressed = compress(scrubbed)  # DANN komprimieren
    return compressed
```

## §341 SGB V Compliance Checkliste

Vor ePA-Upload prüfen:
- [ ] Patienteneinwilligung vorhanden (informed consent)
- [ ] PHI vollständig gescrubbt
- [ ] FHIR R4 Ressourcen valide (HAPI FHIR Validator)
- [ ] KIM-Transport für Übermittlung (nicht E-Mail)
- [ ] Zugriffsprotokoll erstellt
- [ ] Datenschutzbeauftragter informiert bei >500 Datensätzen

## MIO (Medizinische Informationsobjekte)

Strukturierte FHIR-Profile der Gematik für spezifische Anwendungsfälle:

| MIO | Beschreibung | Status |
|-----|-------------|--------|
| KBV_MIO_Vaccination | Impfpass | Produktiv |
| KBV_MIO_ZAEB | Zahnärztliches Bonusheft | Produktiv |
| KBV_MIO_MutterPass | Mutterpass | Produktiv |
| KBV_MIO_ULike | U-Heft Kinder | Produktiv |
| KBV_MIO_NFDxDPE | Notfalldaten | Produktiv |
| KBV_MIO_KHEntlassbrief | Krankenhausentlassbrief | In Entwicklung |

Referenz: `references/fhir_profiles.md`

## Arztbrief → ePA Workflow

```
1. Text einlesen (Kürzel expandieren via comptext-codex)
2. Abschnitte erkennen:
   - Diagnosen → Condition Ressourcen
   - Medikamente → MedicationStatement
   - Vitalzeichen → Observation
   - Prozeduren → Procedure (OPS-Code)
   - Allergien → AllergyIntolerance
3. PHI scrubben (Regex → NER)
4. FHIR Bundle erstellen
5. Validieren (HAPI Validator oder simplifier.net)
6. Upload via KIM oder ePA-Konnektor
```

## CompText Termux Integration

```python
# In med_codex.py – ePA-Kategorien
epa_entries = codex.list_by_category("EPA")
# Gibt zurück: ePA, FHIR, ICD10, LOINC, OPS, KIM, TI, MIO

# In codex_manager_cli.py:
# python codex_manager_cli.py --auto-fill epa --count 20
# python codex_manager_cli.py --generate-skills --output ~/.hermes/skills
```

## Verification

```python
import json
# FHIR Condition Struktur prüfen
condition = {
    "resourceType": "Condition",
    "code": {"coding": [{"system": "http://fhir.de/CodeSystem/dimdi/icd-10-gm", "code": "I63.9"}]},
    "subject": {"reference": "Patient/test-001"}
}
assert condition["resourceType"] == "Condition"
assert "I63.9" in json.dumps(condition)
print("FHIR Struktur OK")
```

## Pitfalls

- scrub() IMMER vor compress() — niemals umgekehrt (PHI könnte komprimiert werden)
- ICD-10-GM für Deutschland, nicht ICD-10-WHO international
- FHIR R4, nicht STU3 (Gematik-Vorgabe seit 2024)
- KIM für TI-Transport, nicht E-Mail oder normale API-Calls
- Validierung gegen KBV-Profile pflicht vor Produktivbetrieb
