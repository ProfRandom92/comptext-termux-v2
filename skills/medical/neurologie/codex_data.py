"""
Neurologie – MedCodex Fachbereichs-Daten
==========================================
Spezialisierte Kürzel für Neurologie, Neurochirurgie und Neuroradiologie.
ePA-konform: ICD-10, LOINC, OPS integriert.

Kategorien:
  NEUROLOGIE  – fachspezifische Kürzel (eigene Kategorie für Filterung)
  BILDGEBUNG  – MRT, CT, Angiographie
  SCORE       – neurologische Scores
  MEDIKAMENT  – neurologische Therapeutika
"""
from __future__ import annotations

SPECIALTY = "Neurologie"
CATEGORY_TAG = "NEUROLOGIE"

# Format: (shorthand, expansion, category, icd10, priority_hint, context)
CODEX_ENTRIES: list[tuple] = [

    # =========================================================================
    # NOTFALL-NEUROLOGIE
    # =========================================================================
    ("APOPLEX",      "Schlaganfall / Ischämischer Zerebraler Insult",           "NEUROLOGIE", "I63.9",  "P1", "FAST-Test, CT nativ sofort, Lyse-Fenster 4.5h, Thrombektomie <6h"),
    ("SAB",          "Subarachnoidalblutung",                                    "NEUROLOGIE", "I60.9",  "P1", "Donnerschlag-Kopfschmerz, LP wenn CT neg, Neurochirurgie"),
    ("ICB",          "Intrazerebrale Blutung",                                   "NEUROLOGIE", "I61.9",  "P1", "CT sofort, RR-Kontrolle, Neurochirurgie, Antikoag-Antagonisierung"),
    ("SEB",          "Subdurale Blutung / Subdurales Hämatom",                   "NEUROLOGIE", "S06.5",  "P1", "CT, Neurochirurgie, Trepanation bei Raumforderung"),
    ("EPH",          "Epidurales Hämatom",                                       "NEUROLOGIE", "S06.4",  "P1", "Lucides Intervall nach SHT, CT, OP sofort"),
    ("SE",           "Status Epilepticus",                                       "NEUROLOGIE", "G41.9",  "P1", "Benzo IV, Levetiracetam, Phenytoin, Intubation wenn >5min"),
    ("TIA",          "Transitorische Ischämische Attacke",                       "NEUROLOGIE", "G45.9",  "P2", "ABCD2-Score, MRT DWI, ASS, Karotis-Doppler"),
    ("HSDH",         "Chronisch Subdurales Hämatom",                             "NEUROLOGIE", "S06.5",  "P2", "Ältere Patienten, Sturz, Trepanation"),
    ("GBS",          "Guillain-Barré-Syndrom",                                   "NEUROLOGIE", "G61.0",  "P2", "Aufsteigende Lähmung, IVIG, Plasmapherese, Beatmungsbereitschaft"),
    ("MYASTH-KRISE", "Myasthene Krise",                                          "NEUROLOGIE", "G70.0",  "P1", "Respiratorische Insuffizienz, Pyridostigmin, IVIG, Plasmapherese"),

    # =========================================================================
    # DIAGNOSEN
    # =========================================================================
    ("MS",           "Multiple Sklerose",                                        "NEUROLOGIE", "G35",    "P3", "MRT-Plaques, oligoklonale Banden, Schübe, DMT"),
    ("PD",           "Parkinson-Erkrankung",                                     "NEUROLOGIE", "G20",    "P3", "Rigor, Tremor, Bradykinese, L-DOPA"),
    ("ALS",          "Amyotrophe Lateralsklerose",                               "NEUROLOGIE", "G12.21", "P3", "Obere+untere MN, EMG, Riluzol"),
    ("DME",          "Demenz / Neurokognitive Störung",                          "NEUROLOGIE", "F03",    "P4", "MMSE, MoCA, Caregiver-Assessment"),
    ("AD",           "Alzheimer-Demenz",                                         "NEUROLOGIE", "G30.9",  "P4", "Amyloid PET, Liquor Tau/Aβ, Acetylcholinesterase-Hemmer"),
    ("MIGRÄNE",      "Migräne",                                                  "NEUROLOGIE", "G43.9",  "P3", "Aura?, Triptane, Prophylaxe, CGRP-AK"),
    ("EPILEPSIE",    "Epilepsie",                                                 "NEUROLOGIE", "G40.9",  "P3", "EEG, MRT, Antikonvulsiva"),
    ("HYDRO",        "Hydrozephalus",                                             "NEUROLOGIE", "G91.9",  "P2", "Ventrikelsystem MRT/CT, Shunt, Norman-Pressure-H."),
    ("MENINGITIS",   "Meningitis / Meningoenzephalitis",                         "NEUROLOGIE", "G03.9",  "P1", "Liquor sofort, Antibiotika bei bakt. V.a. sofort, CT vor LP"),
    ("ENZEPHALITIS", "Enzephalitis",                                              "NEUROLOGIE", "G04.9",  "P1", "MRT, Liquor PCR, HSV → Aciclovir sofort, AK-Status"),
    ("HIRNÖDEM",     "Zerebrales Ödem",                                           "NEUROLOGIE", "G93.6",  "P1", "Mannit, Oberkörperhochlagerung, ICP-Monitoring, Neurochirurgie"),
    ("NEURO-INFARKT","Zerebraler Infarkt",                                        "NEUROLOGIE", "I63.9",  "P1", "Lyse, Thrombektomie, ASS, Statin"),

    # =========================================================================
    # SYMPTOME / BEFUNDE
    # =========================================================================
    ("HEMIPLEG",     "Hemiparese / Hemiplegie",                                  "NEUROLOGIE", "G81.9",  "P2", "Kraftgrad 0-5, kontralaterale Hemisphäre"),
    ("DYSARTH",      "Dysarthrie / Sprechstörung",                               "NEUROLOGIE", "R47.1",  "P2", "Artikulation, Bulbärparalyse?"),
    ("APHASIE",      "Aphasie / Sprachstörung",                                  "NEUROLOGIE", "R47.0",  "P2", "Broca (motor) vs. Wernicke (sensor)"),
    ("DOPPELB",      "Diplopie / Doppelbilder",                                  "NEUROLOGIE", "H53.2",  "P2", "N.III, IV, VI? Hirnstamm?"),
    ("NYSTAGMUS",    "Nystagmus",                                                 "NEUROLOGIE", "H55.0",  "P3", "Spontan/provoziert, Richtung, peripher vs. zentral"),
    ("ATAXIE",       "Ataxie / Koordinationsstörung",                            "NEUROLOGIE", "G11.9",  "P2", "Kleinhirn? Romberg, Finger-Nase-Test"),
    ("PARÄSTHESIE",  "Parästhesie / Sensibilitätsstörung",                       "NEUROLOGIE", "R20.2",  "P3", "Dermatom, Nerv, Plexus?"),
    ("BEWUSSTLOS",   "Bewusstlosigkeit / Synkope neurologisch",                  "NEUROLOGIE", "R55",    "P2", "EEG, CT, Liquor, Herzrhythmus ausschließen"),
    ("TREMOR",       "Tremor",                                                    "NEUROLOGIE", "R25.1",  "P3", "Ruhe/Intention/Halte-Tremor, Parkinson?, ET?"),
    ("FAZIALISPAR",  "Fazialisparese",                                            "NEUROLOGIE", "G51.0",  "P2", "Zentral vs. peripher, Bell-Parese, ORL"),
    ("PUPIL-DIFF",   "Anisokorie / Pupillendifferenz",                           "NEUROLOGIE", "H57.0",  "P1", "Herniationzeichen? N.III-Parese? Horner?"),
    ("ICP↑",         "Erhöhter Intrakranieller Druck",                           "NEUROLOGIE", "G93.2",  "P1", "Papillenödem, Cushing-Reflex, CT, ICP-Sonde"),
    ("NACKENSTARRE", "Meningismus / Nackensteifigkeit",                          "NEUROLOGIE", "R29.1",  "P1", "Kernig/Brudzinski positiv → Liquor, Meningitis/SAB"),

    # =========================================================================
    # BILDGEBUNG (Neurologie-spezifisch)
    # =========================================================================
    ("MRT-ISCHÄMIE", "MRT-Befund: Ischämisches Infarktareal (DWI-Restriktion)",  "BILDGEBUNG", None,    "P1", "DWI hyperintens, ADC hypointens = frischer Infarkt"),
    ("MRT-PLAQUES",  "MRT-Befund: Demyelinisierungsplaques (MS-typisch)",        "BILDGEBUNG", None,    "P3", "Periventrikulär, juxtakortikal, Dawson-Finger"),
    ("CT-HYPO",      "CT-Befund: Hypodense Läsion (ischämisch oder Ödem)",       "BILDGEBUNG", None,    "P1", "Frühzeichen: Inselzeichen, Basalganglien"),
    ("CT-HYPERD",    "CT-Befund: Hyperdense Arterie (Thrombus)",                 "BILDGEBUNG", None,    "P1", "Hyperdenses MCA-Zeichen = Thrombus"),
    ("CT-SAB",       "CT-Befund: Subarachnoidalblutung (Stern-Muster)",          "BILDGEBUNG", None,    "P1", "Zisternen hyperdens, Fischer-Grad"),
    ("DSA",          "Digitale Subtraktionsangiographie",                         "BILDGEBUNG", None,    "P1", "Aneurysma, AVM, Stenose, Thrombektomie-Planung"),
    ("CTA-NEURO",    "CT-Angiographie zerebral/zervikal",                        "BILDGEBUNG", None,    "P1", "Stenose, Verschluss, Aneurysma"),
    ("MRA",          "Magnetresonanzangiographie",                                "BILDGEBUNG", None,    "P2", "Gefäßdarstellung ohne KM möglich"),
    ("EEG",          "Elektroenzephalogramm",                                     "BILDGEBUNG", None,    "P2", "Epilepsie, Enzephalopathie, Hirntodfeststellung"),
    ("LP",           "Lumbalpunktion / Liquordiagnostik",                        "BILDGEBUNG", None,    "P2", "Meningitis, SAB (xanthochrom), GBS, MS"),
    ("EMG",          "Elektromyographie",                                         "BILDGEBUNG", None,    "P3", "Periphere Nervenläsion, ALS, Myopathie"),
    ("NLG",          "Nervenleitgeschwindigkeit",                                 "BILDGEBUNG", None,    "P3", "Polyneuropathie, Karpaltunnelsyndrom"),
    ("PET-NEURO",    "Positronenemissionstomographie neurologisch",              "BILDGEBUNG", None,    "P3", "Amyloid-PET, FDG-PET bei Demenz/Epilepsie"),

    # =========================================================================
    # SCORES
    # =========================================================================
    ("NIHSS",        "National Institutes of Health Stroke Scale",               "SCORE",      None,    "P1", "0=normal, >25=schwer; ≥6 → Thrombektomie erwägen"),
    ("GCS",          "Glasgow Coma Scale",                                       "SCORE",      None,    "P1", "Augen+Motor+Verbal, max 15, <8 → Intubation erwägen"),
    ("MMSE",         "Mini-Mental-State-Examination",                            "SCORE",      None,    "P3", "Kognition 0-30, <24 = V.a. Demenz"),
    ("MOCA",         "Montreal Cognitive Assessment",                            "SCORE",      None,    "P3", "Kognition 0-30, sensitiver als MMSE für leichte Defizite"),
    ("ABCD2",        "ABCD2-Score für TIA-Schlaganfallrisiko",                   "SCORE",      None,    "P2", "Alter, BD, Klinisches Bild, Dauer, Diabetes; >4 = hohes Risiko"),
    ("mRS",          "Modified Rankin Scale (Behinderungsgrad)",                 "SCORE",      None,    "P3", "0=symptomfrei, 6=Tod; Outcome-Parameter Schlaganfall"),
    ("UPDRS",        "Unified Parkinson's Disease Rating Scale",                 "SCORE",      None,    "P3", "Parkinson-Schweregrad 0-199"),
    ("EDSS",         "Expanded Disability Status Scale (MS)",                    "SCORE",      None,    "P3", "MS-Behinderungsgrad 0-10"),
    ("FOUR-SCORE",   "Full Outline of Unresponsiveness Score",                   "SCORE",      None,    "P2", "Besser als GCS für intubierten Patienten"),

    # =========================================================================
    # MEDIKAMENTE NEUROLOGIE
    # =========================================================================
    ("tPA",          "Alteplase / rtPA / Thrombolyse IV",                        "MEDIKAMENT", None,    "P1", "0.9mg/kg (max 90mg), 10% Bolus, 90min Infusion, <4.5h"),
    ("LEVETIR",      "Levetiracetam / Keppra",                                   "MEDIKAMENT", None,    "P2", "Antikonvulsivum, IV oder oral, SE: 60mg/kg"),
    ("VALPROAT",     "Valproinsäure / Valproat",                                 "MEDIKAMENT", None,    "P2", "Antikonvulsivum, IV bei SE, Spiegelkontrolle"),
    ("L-DOPA",       "Levodopa / L-DOPA",                                        "MEDIKAMENT", None,    "P3", "Parkinson, immer mit Carbidopa/Benserazid"),
    ("MIDAZOLAM",    "Midazolam",                                                 "MEDIKAMENT", None,    "P1", "SE: 0.1mg/kg IV/buccal/nasal, Sedierung"),
    ("MANNITOL",     "Mannitol 20%",                                             "MEDIKAMENT", None,    "P1", "ICP↑: 0.5-1g/kg IV über 20min, Hirnödem"),
    ("ACICLOVIR",    "Aciclovir",                                                 "MEDIKAMENT", None,    "P1", "Enzephalitis (HSV): 10mg/kg alle 8h IV, 14-21 Tage"),
    ("IVIG",         "Intravenöse Immunglobuline",                               "MEDIKAMENT", None,    "P2", "GBS, Myasthenie: 2g/kg über 5 Tage"),
    ("AMANTADIN",    "Amantadin",                                                 "MEDIKAMENT", None,    "P3", "Parkinson, akinetische Krise"),
    ("SUMATRIP",     "Sumatriptan / Triptan",                                    "MEDIKAMENT", None,    "P3", "Migräne-Akuttherapie, Kontra: Basilarismigräne"),
]


def get_entries() -> list[tuple]:
    """Gibt alle Einträge für diesen Fachbereich zurück."""
    return CODEX_ENTRIES


def get_specialty() -> str:
    return SPECIALTY


def get_count() -> int:
    return len(CODEX_ENTRIES)
