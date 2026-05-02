#!/usr/bin/env python3
"""
MedSpecialties – Fachbereich-Datenbank für den MedCodex
=========================================================
Automatisches Befüllen des Codex mit fachspezifischen Kürzeln.

Fachbereiche:
    NEU  – Neurologie
    RAD  – Radiologie
    KAR  – Kardiologie (erweitert)
    INT  – Intensivmedizin / ICU
    PÄD  – Pädiatrie
    CHI  – Chirurgie
    PSY  – Psychiatrie
    GYN  – Gynäkologie & Geburtshilfe
    UNF  – Unfallchirurgie / Traumatologie
    GAS  – Gastroenterologie
    PUL  – Pneumologie
    NEP  – Nephrologie

Verwendung:
    from med_specialties import SPECIALTY_MODULES, load_specialty
    load_specialty("NEU")  # Neurologie in Codex laden
"""
from __future__ import annotations

from typing import NamedTuple


class SpecEntry(NamedTuple):
    shorthand: str
    expansion: str
    category: str
    icd10: str | None
    priority_hint: str
    context: str | None


# ============================================================================
# NEUROLOGIE
# ============================================================================
NEUROLOGIE: list[SpecEntry] = [
    # Erkrankungen
    SpecEntry("APOPLEX",   "Ischämischer Schlaganfall / Apoplex",           "DIAGNOSE", "I63.9",  "P1", "FAST-Test, NIHSS, CT/MRT sofort, Lyse-Fenster 4.5h"),
    SpecEntry("TIA",       "Transitorische ischämische Attacke",             "DIAGNOSE", "G45.9",  "P2", "ABCD2-Score, Schlaganfall-Risiko nächste 48h hoch"),
    SpecEntry("SAB",       "Subarachnoidalblutung",                          "DIAGNOSE", "I60.9",  "P1", "Donnerschlagkopfschmerz, CT, Lumbalpunktion wenn CT negativ"),
    SpecEntry("ICB",       "Intrazerebrale Blutung",                         "DIAGNOSE", "I61.9",  "P1", "CT sofort, Neurochirurgie, RR-Kontrolle"),
    SpecEntry("SDH",       "Subduralhämatom",                                "DIAGNOSE", "S06.5",  "P1", "Akut vs. chronisch, CT, Neurochirurgie"),
    SpecEntry("EDH",       "Epiduralhämatom",                                "DIAGNOSE", "S06.4",  "P1", "Luzides Intervall, CT, sofortige OP"),
    SpecEntry("STATUS-EP", "Status epilepticus",                             "DIAGNOSE", "G41.9",  "P1", "Benzodiazepin i.v., Phenytoin, Intubation wenn refraktär"),
    SpecEntry("MENINGITIS","Meningitis / Meningoenzephalitis",               "DIAGNOSE", "G03.9",  "P1", "Lumbalpunktion nach CT, Antibiotika sofort, Dexamethason"),
    SpecEntry("GBS",       "Guillain-Barré-Syndrom",                         "DIAGNOSE", "G61.0",  "P2", "Atemfunktion überwachen, IVIG oder Plasmapherese"),
    SpecEntry("MYASTHENIE","Myasthenische Krise",                            "DIAGNOSE", "G70.01", "P1", "Ateminsuffizienz, Intensivstation, Cholinesterasehemmer"),
    SpecEntry("MS",        "Multiple Sklerose",                              "DIAGNOSE", "G35",    "P3", "Schub: Methylprednisolon 1g/d × 3–5d"),
    SpecEntry("DEMENZ",    "Demenz / Kognitive Einschränkung",               "DIAGNOSE", "F03",    "P4", "MMSE, Ursachensuche, Sicherheitsplanung"),
    SpecEntry("PNP",       "Polyneuropathie",                                "DIAGNOSE", "G62.9",  "P3", "Diabetes? Alkohol? Toxisch? EMG/NLG"),
    SpecEntry("PARK",      "Morbus Parkinson",                               "DIAGNOSE", "G20",    "P3", "Dopaminergika, Sturzrisiko"),
    # Scores / Tests
    SpecEntry("NIHSS",     "NIH Stroke Scale",                               "DIAGNOSE", "I63.9",  "P1", "0–42 Punkte, >8 = schwerer Schlaganfall"),
    SpecEntry("GCS",       "Glasgow Coma Scale",                             "DIAGNOSE", "R41.3",  "P1", "E+V+M, 15=wach, <8 = Intubation erwägen"),
    SpecEntry("MMSE",      "Mini Mental State Examination",                  "DIAGNOSE", "F03",    "P4", "0–30, <24 = kognitiver Defizit"),
    SpecEntry("EEG",       "Elektroenzephalogramm",                          "LABOR",    None,     "P2", "Epilepsie, Status epilepticus, Hirntoddiagnostik"),
    SpecEntry("EMG",       "Elektromyogramm",                                "LABOR",    None,     "P3", "Muskelerkrankungen, Polyneuropathie"),
    SpecEntry("NLG",       "Nervenleitgeschwindigkeit",                      "LABOR",    None,     "P3", "Axonal vs. demyelinisierend"),
    SpecEntry("LP",        "Lumbalpunktion / Liquoruntersuchung",            "LABOR",    None,     "P2", "Meningitis, SAB, MS, GBS"),
    # Symptome
    SpecEntry("HEMIP",     "Hemiplegie / Hemiparese",                        "SYMPTOM",  "G81.9",  "P1", "Kontralateral zur Läsion, APOPLEX?"),
    SpecEntry("APHASE",    "Aphasie / Sprachstörung",                        "SYMPTOM",  "R47.0",  "P1", "Motorisch, sensorisch, global – APOPLEX?"),
    SpecEntry("DYSARTH",   "Dysarthrie",                                     "SYMPTOM",  "R47.1",  "P2", "Schlaganfall, Kleinhirn, Hirnstamm"),
    SpecEntry("ATAXIE",    "Ataxie / Koordinationsstörung",                  "SYMPTOM",  "R27.0",  "P2", "Kleinhirn, Vestibularis, Neuropathie"),
    SpecEntry("NYSTAGM",   "Nystagmus",                                      "SYMPTOM",  "H55.0",  "P2", "Zentral vs. peripher, HINTS-Test"),
    SpecEntry("PLEGIE",    "Plegie / Vollständige Lähmung",                  "SYMPTOM",  "G83.9",  "P1", "Querschnitt? Schlaganfall?"),
    SpecEntry("FAZIAP",    "Fazialisparese / Gesichtslähmung",               "SYMPTOM",  "G51.0",  "P2", "Zentral vs. peripher, Bell's Parese vs. APOPLEX"),
    SpecEntry("ANISOK",    "Anisokorie / Ungleiche Pupillen",                "SYMPTOM",  "H57.0",  "P1", "Einklemmung? Okulomotoriusparese? Horner?"),
    SpecEntry("PAPILÖD",   "Papillenödem / Stauungspapille",                 "SYMPTOM",  "H47.1",  "P1", "Hirndruckerhöhung, sofort CT"),
]

# ============================================================================
# RADIOLOGIE
# ============================================================================
RADIOLOGIE: list[SpecEntry] = [
    # Modalitäten
    SpecEntry("CCT",       "Kraniale Computertomographie / Schädel-CT",      "DIAGNOSE", None,     "P1", "Blutung? Ischämie (erst nach 4–6h sichtbar)? Fraktur?"),
    SpecEntry("cCT",       "Kraniale Computertomographie (Kleinschreibung)", "DIAGNOSE", None,     "P1", "Wie CCT"),
    SpecEntry("MRT",       "Magnetresonanztomographie",                      "DIAGNOSE", None,     "P2", "Weichteil, Ischämie früh (DWI), Rückenmark"),
    SpecEntry("MRI",       "Magnetic Resonance Imaging (englisch)",          "DIAGNOSE", None,     "P2", "Wie MRT"),
    SpecEntry("DWI",       "Diffusion Weighted Imaging (MRT-Sequenz)",       "DIAGNOSE", None,     "P1", "Akute Ischämie bereits Minuten nach Ereignis sichtbar"),
    SpecEntry("CTPA",      "CT-Pulmonalisangiographie",                      "DIAGNOSE", "I26.9",  "P1", "Lungenembolie-Nachweis, Kontrastmittel"),
    SpecEntry("CTA",       "CT-Angiographie",                                "DIAGNOSE", None,     "P1", "Gefäßdarstellung, Aneurysma, Stenose"),
    SpecEntry("MRA",       "MR-Angiographie",                                "DIAGNOSE", None,     "P2", "Gefäße ohne Kontrastmittel möglich"),
    SpecEntry("SONO",      "Sonographie / Ultraschall",                      "DIAGNOSE", None,     "P2", "Abdomen, Gefäße, FAST-Sonographie Trauma"),
    SpecEntry("ECHO",      "Echokardiographie",                              "DIAGNOSE", None,     "P1", "TTE oder TEE, Herzfunktion, Klappen, Perikard"),
    SpecEntry("TEE",       "Transösophageale Echokardiographie",             "DIAGNOSE", None,     "P2", "Bessere Bildqualität, Aortendissektion, Thrombus"),
    SpecEntry("TTE",       "Transthorakale Echokardiographie",               "DIAGNOSE", None,     "P2", "Bettseitig möglich, Screening"),
    SpecEntry("RTG",       "Röntgen / Röntgenaufnahme",                      "DIAGNOSE", None,     "P3", "Thorax, Extremitäten, Abdomenübersicht"),
    SpecEntry("RÖNTGEN",   "Röntgenaufnahme",                                "DIAGNOSE", None,     "P3", "Wie RTG"),
    SpecEntry("ANGIO",     "Angiographie (invasiv)",                         "DIAGNOSE", None,     "P1", "Herzkatheter, Hirngefäße, Beckengefäße"),
    SpecEntry("PET",       "Positronenemissionstomographie",                 "DIAGNOSE", None,     "P3", "Tumordiagnostik, Demenz-Differenzierung"),
    SpecEntry("SZINTI",    "Szintigraphie / Nuklearmedizin",                 "DIAGNOSE", None,     "P3", "Schilddrüse, Knochen, Perfusion"),
    # Befunde
    SpecEntry("FRAKTUR",   "Fraktur / Knochenbruch",                        "DIAGNOSE", "S00-S99", "P2", "Disloziert? Gelenkbeteiligung? OP?"),
    SpecEntry("PNEUMO",    "Pneumothorax",                                   "DIAGNOSE", "J93.9",  "P1", "Spannungspneumo? Entlastungspunktion sofort"),
    SpecEntry("HÄMAPL",    "Hämatopneumothorax",                             "DIAGNOSE", "J94.2",  "P1", "Drainage, Volumen"),
    SpecEntry("PLEURAERG", "Pleuraerguss",                                   "DIAGNOSE", "J90",    "P3", "Punktion wenn symptomatisch, Ursache klären"),
    SpecEntry("ATELEKT",   "Atelektase / Lungenatelektase",                  "DIAGNOSE", "J98.1",  "P3", "Mobilisation, Physiotherapie, bronchoskopie"),
    SpecEntry("AORTDISS",  "Aortendissektion",                               "DIAGNOSE", "I71.0",  "P1", "Stanford A/B, CT, Herzchirurgie sofort bei Typ A"),
    SpecEntry("KM",        "Kontrastmittel (iodhaltig)",                     "ADMIN",    None,     "P3", "Allergie? Nierenfunktion (eGFR)? Metformin pausieren"),
    SpecEntry("EGFR",      "Glomeruläre Filtrationsrate (estimated)",        "LABOR",    None,     "P3", "Nierenfunktion, KM-Gabe <30 = kontraindiziert"),
    # Strahlung / Dosis
    SpecEntry("DLP",       "Dosislängenprodukt (CT-Strahlendosis)",          "ADMIN",    None,     "P4", "mGy·cm, Strahlenschutz"),
    SpecEntry("MSCT",      "Mehrschicht-CT / Multi-Slice-CT",                "DIAGNOSE", None,     "P2", "Modernes CT mit vielen Detektorreihen"),
]

# ============================================================================
# KARDIOLOGIE (erweitert)
# ============================================================================
KARDIOLOGIE: list[SpecEntry] = [
    SpecEntry("HI",        "Herzinsuffizienz",                               "DIAGNOSE", "I50.9",  "P2", "EF? NYHA? BNP/NT-proBNP"),
    SpecEntry("EF",        "Ejektionsfraktion",                              "LABOR",    None,     "P2", "Normal >55%, HFrEF <40%, HFmrEF 40-49%"),
    SpecEntry("BNP",       "B-Typ natriuretisches Peptid",                   "LABOR",    None,     "P2", "Herzinsuffizienz-Marker, erhöht bei Dyspnoe"),
    SpecEntry("NTBNP",     "NT-proBNP",                                      "LABOR",    None,     "P2", "Altersabhängige Grenzwerte, Herzinsuffizienz"),
    SpecEntry("AF",        "Vorhofflimmern / Atrial Fibrillation",           "DIAGNOSE", "I48.9",  "P2", "Antikoagulation, Frequenz- oder Rhythmuskontrolle"),
    SpecEntry("AFL",       "Vorhofflattern",                                 "DIAGNOSE", "I48.4",  "P2", "Katheterablation empfohlen"),
    SpecEntry("AV-BLOCK",  "AV-Block",                                       "DIAGNOSE", "I44.3",  "P2", "Grad I-III, Grad III = Schrittmacher"),
    SpecEntry("LBBB",      "Linksschenkelblock",                             "DIAGNOSE", "I44.7",  "P2", "Neuer LBBB = STEMI-Äquivalent behandeln"),
    SpecEntry("RBBB",      "Rechtsschenkelblock",                            "DIAGNOSE", "I45.1",  "P3", "Bei PE: neue Rechtsherzbelastung"),
    SpecEntry("KMP",       "Kardiomyopathie",                                "DIAGNOSE", "I42.9",  "P2", "Dilatatativ, hypertrophisch, restriktiv"),
    SpecEntry("ENDOK",     "Endokarditis",                                   "DIAGNOSE", "I33.0",  "P1", "Duke-Kriterien, Blutkulturen × 3, Echo"),
    SpecEntry("PERICARD",  "Perikarditis / Perikarderguss",                  "DIAGNOSE", "I30.9",  "P2", "Tamponade? Beckmanzeichen? Punktion"),
    SpecEntry("TAMPON",    "Herztamponade",                                  "DIAGNOSE", "I31.9",  "P1", "Beck-Trias, Perikardpunktion sofort"),
    SpecEntry("AORTS",     "Aortenstenose",                                  "DIAGNOSE", "I35.0",  "P2", "Gradient, Klappe Area, TAVI vs. SAVR"),
    SpecEntry("MIINS",     "Mitralklappeninsuffizienz",                      "DIAGNOSE", "I34.0",  "P2", "Grad I-IV, Echo"),
    SpecEntry("TAVI",      "Transkatheter-Aortenklappenimplantation",        "DIAGNOSE", None,     "P3", "Interventionell, hoch-Risiko Patienten"),
    SpecEntry("ICD",       "Implantierbarer Kardioverter-Defibrillator",     "ADMIN",    None,     "P2", "SCD-Prophylaxe, EF <35%, VF/VT"),
    SpecEntry("CRT",       "Kardiale Resynchronisationstherapie",            "ADMIN",    None,     "P3", "HI mit LBBB, QRS >150ms"),
    SpecEntry("PTCA",      "Perkutane transluminale Koronarangioplastie",    "DIAGNOSE", None,     "P1", "Ballondilatation bei ACS"),
    SpecEntry("CABG",      "Koronararterien-Bypass-Operation",               "DIAGNOSE", None,     "P2", "Bypass-OP, Dreigefäßerkrankung"),
    SpecEntry("NYHA",      "New York Heart Association Klassifikation",      "DIAGNOSE", None,     "P2", "I=asymptomatisch, IV=Ruhedyspnoe"),
    SpecEntry("CCS",       "Canadian Cardiovascular Society Angina-Grade",   "DIAGNOSE", None,     "P2", "I-IV, Angina pectoris Schweregrad"),
]

# ============================================================================
# INTENSIVMEDIZIN / ICU
# ============================================================================
INTENSIVMEDIZIN: list[SpecEntry] = [
    # Beatmung
    SpecEntry("INTUB",     "Endotracheale Intubation",                       "MEDIKAMENT", None,  "P1", "RSI: Fentanyl+Propofol+Rocuronium, Cuffed-Tubus"),
    SpecEntry("RSI",       "Rapid Sequence Induction / Blitzintubation",     "MEDIKAMENT", None,  "P1", "Fentanyl 2µg/kg, Propofol 2mg/kg, Rocuronium 1.2mg/kg"),
    SpecEntry("BEATM",     "Mechanische Beatmung / Ventilation",             "MEDIKAMENT", None,  "P1", "VC-AC oder PC-AC, Tidalvolumen 6ml/kg IBW"),
    SpecEntry("PEEP",      "Positiver endexspiratorischer Druck",            "MEDIKAMENT", None,  "P1", "Alveolar-Recruitment, ARDS: höherer PEEP"),
    SpecEntry("CPAP",      "Continous Positive Airway Pressure",             "MEDIKAMENT", None,  "P1", "Non-invasiv, Lungenödem, COPD-Exaz."),
    SpecEntry("NIV",       "Non-invasive Ventilation / Nicht-invasive Beatmung", "MEDIKAMENT", None, "P2", "BiPAP/CPAP, vermeidet Intubation"),
    SpecEntry("BIPAP",     "Bilevel Positive Airway Pressure",               "MEDIKAMENT", None,  "P2", "Inspiratorisch (IPAP) und exspiratorisch (EPAP)"),
    SpecEntry("HFNC",      "High-Flow Nasal Cannula / Hochfluss-Sauerstoff", "MEDIKAMENT", None,  "P2", "Bis 60 L/min, Preoxygenierung, COVID"),
    SpecEntry("ARDS",      "Acute Respiratory Distress Syndrome",            "DIAGNOSE", "J80",   "P1", "Berlin-Definition, P/F-Ratio, Bauchlage bei schwer"),
    SpecEntry("PRONE",     "Bauchlage / Prone Positioning",                  "MEDIKAMENT", None,  "P1", "ARDS P/F <150, 16h/Tag"),
    # Kreislauf / Monitoring
    SpecEntry("MAP",       "Mittlerer arterieller Druck",                    "LABOR",    None,     "P1", "Ziel >65 mmHg, Sepsis, nach Reanimation"),
    SpecEntry("ZVK",       "Zentralvenöser Katheter",                        "ADMIN",    None,     "P1", "V. jug. int., V. subclavia, ZVD-Messung, Vasopressoren"),
    SpecEntry("ZVD",       "Zentralvenöser Druck",                           "LABOR",    None,     "P2", "Volumensteuerung, 8–12 mmHg Ziel bei Sepsis"),
    SpecEntry("PICC",      "Peripherally Inserted Central Catheter",         "ADMIN",    None,     "P3", "Langzeitkatheter, Chemotherapie"),
    SpecEntry("PICCO",     "Pulse Contour Cardiac Output",                   "ADMIN",    None,     "P2", "Herzzeitvolumen, ITBV, EVLW – erweitert Monitoring"),
    SpecEntry("SG-KATH",   "Swan-Ganz-Katheter / Pulmonaliskatheter",        "ADMIN",    None,     "P2", "PCWP, HZV, gemischt-venöse Sättigung"),
    SpecEntry("HZV",       "Herzzeitvolumen",                                "LABOR",    None,     "P2", "Normal 4–8 L/min, CI >2.2 L/min/m²"),
    SpecEntry("SCVO2",     "Zentralvenöse Sauerstoffsättigung",              "LABOR",    None,     "P1", "Ziel >70% bei Sepsis, <65% = kritisch"),
    # Nierenersatz
    SpecEntry("CRRT",      "Kontinuierliche Nierenersatztherapie",           "MEDIKAMENT", None,  "P1", "CVVHF, CVVHD, CVVHDF – bei AKI auf ICU"),
    SpecEntry("AKI",       "Akutes Nierenversagen / Acute Kidney Injury",    "DIAGNOSE", "N17.9", "P1", "KDIGO-Kriterien, Ursache, Nierenschutz"),
    SpecEntry("KDIGO",     "Kidney Disease Improving Global Outcomes (Score)","DIAGNOSE", None,   "P2", "AKI-Staging I-III nach Kreatinin/Urin"),
    # Ernährung
    SpecEntry("PEG",       "Perkutane endoskopische Gastrostomie",           "ADMIN",    None,     "P3", "Langzeit-Ernährung, Schluckstörung"),
    SpecEntry("TPN",       "Totale parenterale Ernährung",                   "MEDIKAMENT", None,  "P2", "Wenn enteral nicht möglich >3 Tage"),
    SpecEntry("EN",        "Enterale Ernährung (Sonde)",                     "MEDIKAMENT", None,  "P2", "Bevorzugt parenteral, frühzeitig starten"),
    # Scores ICU
    SpecEntry("SOFA",      "Sequential Organ Failure Assessment Score",      "DIAGNOSE", None,     "P1", "0–24, Sepsis-Diagnose, Mortalitätsprediktor"),
    SpecEntry("APACHE",    "APACHE II Score",                                "DIAGNOSE", None,     "P1", "ICU-Mortalitäts-Score, 0–71"),
    SpecEntry("SAPS2",     "Simplified Acute Physiology Score 2",            "DIAGNOSE", None,     "P2", "ICU Mortalitäts-Score"),
]

# ============================================================================
# PÄDIATRIE
# ============================================================================
PÄDIATRIE: list[SpecEntry] = [
    SpecEntry("NG",        "Neugeborenes / Neonates (0–28 Tage)",            "ADMIN",    None,     "P1", "Anpassung, Vitalzeichen: HF 100–160, AF 40–60"),
    SpecEntry("SG",        "Säugling (29 Tage – 12 Monate)",                "ADMIN",    None,     "P2", "Besondere Pharmakokinetik, Gewichtsbasiert"),
    SpecEntry("KK",        "Kleinkind (1–3 Jahre)",                          "ADMIN",    None,     "P3", ""),
    SpecEntry("APGAR",     "Apgar-Score (Neugeborenen-Beurteilung)",         "DIAGNOSE", None,     "P1", "5+5+5+5+5=10, <7 nach 5min = Maßnahmen"),
    SpecEntry("BW-KG",     "Körpergewicht Schätzformel Kind",                "ADMIN",    None,     "P2", "2–10 Jahre: (Alter × 2) + 8 = kg"),
    SpecEntry("FIEB-KR",   "Fieberkrampf",                                   "DIAGNOSE", "R56.0",  "P1", "Einfach vs. komplex, Diazepam rektal, Basisdiag."),
    SpecEntry("KRUPPSY",   "Krupp-Syndrom / Laryngotracheitis",              "DIAGNOSE", "J05.0",  "P2", "Bellender Husten, Dexamethason, Adrenalin inh."),
    SpecEntry("BRONCH",    "Bronchiolitis (RSV)",                            "DIAGNOSE", "J21.9",  "P2", "Unter 2 Jahre, supportiv, HFNC wenn nötig"),
    SpecEntry("EPIGL",     "Epiglottitis",                                   "DIAGNOSE", "J05.1",  "P1", "HiB, sofort ORL + Anästhesie, nicht manipulieren"),
    SpecEntry("INTU-PÄD",  "Pädiatrische Intubation",                       "MEDIKAMENT", None,   "P1", "Tubusgröße: (Alter/4)+4, unkalibriert <8J"),
    SpecEntry("VOLU-PÄD",  "Kindlicher Volumenbolus",                        "MEDIKAMENT", None,   "P1", "10–20 ml/kg NaCl 0.9%, max 3× dann kolloidale"),
    SpecEntry("DOSA-PÄD",  "Pädiatrische Dosierung Adrenalin",              "MEDIKAMENT", None,   "P1", "0.01 mg/kg i.v. bei REA"),
    SpecEntry("DEFI-PÄD",  "Pädiatrische Defibrillation",                   "MEDIKAMENT", None,   "P1", "4 J/kg"),
    SpecEntry("RSV",       "Respiratorisches Synzytialvirus",                "DIAGNOSE", "J21.0",  "P2", "Säuglinge, Bronchiolitis, Nirsevimab-Prophylaxe"),
    SpecEntry("KAWA",      "Kawasaki-Syndrom",                               "DIAGNOSE", "M30.3",  "P2", "5 Tage Fieber + 4 Kriterien, IVIG + ASS"),
    SpecEntry("MIS-C",     "Multisystem Inflammatory Syndrome in Children",  "DIAGNOSE", "M35.8",  "P1", "Post-COVID, Schock-ähnlich, IVIG"),
    SpecEntry("NEC",       "Nekrotisierende Enterokolitis",                  "DIAGNOSE", "P77.9",  "P1", "Frühgeborene, Abdomenschmerz, Pneumatosis intestinalis"),
    SpecEntry("SEPSIS-NG", "Neonatale Sepsis",                               "DIAGNOSE", "P36.9",  "P1", "Early-onset vs. Late-onset, Ampicillin+Gentamicin"),
]

# ============================================================================
# CHIRURGIE / UNFALLCHIRURGIE
# ============================================================================
CHIRURGIE: list[SpecEntry] = [
    SpecEntry("POLYTR",    "Polytrauma",                                     "DIAGNOSE", "T00-T07", "P1", "ABCDE, Damage Control, ATLS"),
    SpecEntry("ATLS",      "Advanced Trauma Life Support",                   "DIAGNOSE", None,      "P1", "ABCDE-Schema, Primary/Secondary Survey"),
    SpecEntry("DAMAGE-C",  "Damage Control Surgery / Chirurgie",             "DIAGNOSE", None,      "P1", "Blutung stoppen, Kontamination, Intensivstation, Reop"),
    SpecEntry("FAST-US",   "Focused Assessment Sonography in Trauma",        "DIAGNOSE", None,      "P1", "Freie Flüssigkeit: Perikardbeutel, Morison, Splenorenal"),
    SpecEntry("BECKENF",   "Beckenfraktur",                                  "DIAGNOSE", "S32.9",   "P1", "Instabil → Beckengurt, Damage Control, IR"),
    SpecEntry("FEMURFR",   "Femurfraktur",                                   "DIAGNOSE", "S72.9",   "P2", "Blutverlust 1–2L, Schienung, OP"),
    SpecEntry("RIPPENFR",  "Rippenfraktur",                                  "DIAGNOSE", "S22.3",   "P2", "≥3 Rippen = instabiler Thorax, Epidural"),
    SpecEntry("MILZRUP",   "Milzruptur",                                     "DIAGNOSE", "S36.0",   "P1", "Trauma, freie Flüssigkeit, FAST, Milzembolisation vs. OP"),
    SpecEntry("LEBERRUP",  "Leberruptur",                                    "DIAGNOSE", "S36.1",   "P1", "AAST-Grading, IR oder OP"),
    SpecEntry("ILEUS",     "Ileus / Darmverschluss",                         "DIAGNOSE", "K56.7",   "P1", "Mechanisch vs. paralytisch, CT, OP wenn mechanisch"),
    SpecEntry("APPENDIX",  "Appendizitis",                                   "DIAGNOSE", "K37",     "P2", "Alvarado-Score, CT/Sono, Appendektomie"),
    SpecEntry("PERFORAT",  "Perforation (Hohlorgan)",                        "DIAGNOSE", "K63.1",   "P1", "Freie Luft, Peritonismus, sofort OP"),
    SpecEntry("ABD-AORT",  "Abdominelles Aortenaneurysma",                   "DIAGNOSE", "I71.4",   "P1", "Ruptur = sofort OP/EVAR, Schock"),
    SpecEntry("PERITON",   "Peritonitis",                                    "DIAGNOSE", "K65.9",   "P1", "Ursache OP, Antibiotika breit"),
    SpecEntry("KOMPART",   "Kompartmentsyndrom",                             "DIAGNOSE", "T79.6",   "P1", "5P, Fasziotomie sofort"),
]

# ============================================================================
# PSYCHIATRIE
# ============================================================================
PSYCHIATRIE: list[SpecEntry] = [
    SpecEntry("SUIZIP",    "Suizidgedanken / Suizidalität",                  "DIAGNOSE", "R45.8",  "P1", "Risikoeinschätzung, Sicherheitsplanung, stationär?"),
    SpecEntry("PSYCH-NOF", "Psychiatrischer Notfall",                        "DIAGNOSE", "F99",    "P1", "Eigen- oder Fremdgefährdung, Sicherheit"),
    SpecEntry("AGIT",      "Agitation / Erregungszustand",                   "SYMPTOM",  "F41.9",  "P2", "De-Eskalation, Lorazepam, Haloperidol"),
    SpecEntry("DELIR",     "Delir / Akute Verwirrtheit",                     "DIAGNOSE", "F05.9",  "P2", "Ursache (Infekt? Entzug? Medikament?), Haloperidol"),
    SpecEntry("ALKOHOL-E", "Alkoholentzug / Delirium tremens",               "DIAGNOSE", "F10.3",  "P1", "Benzodiazepin, CIWA-Score, Intensiv wenn schwer"),
    SpecEntry("CIWA",      "CIWA-Ar Score (Alkoholentzug)",                  "DIAGNOSE", None,     "P1", "0–67, >15 = schwerer Entzug, Benzodiazepin"),
    SpecEntry("MANIE",     "Manie / Manische Episode",                       "DIAGNOSE", "F30.9",  "P2", "Lithium, Valproat, Antipsychotika"),
    SpecEntry("PSYCH",     "Psychose / Schizophrenie",                       "DIAGNOSE", "F29",    "P2", "Antipsychotika, Olanzapin, Haloperidol"),
    SpecEntry("DEPR",      "Depression / Depressive Episode",                "DIAGNOSE", "F32.9",  "P3", "SSRI, Psychotherapie, bei Suizidalität stationär"),
]

# ============================================================================
# GASTROENTEROLOGIE
# ============================================================================
GASTROENTEROLOGIE: list[SpecEntry] = [
    SpecEntry("GI-BLUT",   "Gastrointestinale Blutung",                     "DIAGNOSE", "K92.2",  "P1", "Obere vs. untere, Endoskopie, Volumen"),
    SpecEntry("OGIB",      "Obere GI-Blutung",                              "DIAGNOSE", "K92.1",  "P1", "Hämatemesis, ÖGD, PPI i.v., Terlipressin bei Varizen"),
    SpecEntry("UGIB",      "Untere GI-Blutung",                             "DIAGNOSE", "K92.1",  "P2", "Hämatochezie, Koloskopie, IR"),
    SpecEntry("VARIZENBL", "Ösophagusvarizen-Blutung",                      "DIAGNOSE", "I85.0",  "P1", "Terlipressin, Somatostatin, endoskopische Ligatur"),
    SpecEntry("LEBERZ",    "Leberzirrhose",                                  "DIAGNOSE", "K74.6",  "P2", "Child-Pugh, MELD, Komplikationen"),
    SpecEntry("MELD",      "Model for End-Stage Liver Disease",              "DIAGNOSE", None,     "P2", "Transplantationspriorität, 6–40 Punkte"),
    SpecEntry("ASZITES",   "Aszites / Bauchwasser",                         "DIAGNOSE", "R18",    "P3", "Ursache, Punktion wenn symptomatisch, SBP-Ausschluss"),
    SpecEntry("SBP",       "Spontan bakterielle Peritonitis",                "DIAGNOSE", "K65.2",  "P1", "PMN >250/µL Aszites, Cefotaxim"),
    SpecEntry("PANKREAT",  "Akute Pankreatitis",                            "DIAGNOSE", "K85.9",  "P2", "Ranson, CT bei unklarer Prognose, Volumen"),
    SpecEntry("CHOLANGIT", "Cholangitis",                                    "DIAGNOSE", "K83.0",  "P1", "Charcot-Trias, ERCP + Antibiotika"),
]

# ============================================================================
# PNEUMOLOGIE
# ============================================================================
PNEUMOLOGIE: list[SpecEntry] = [
    SpecEntry("COPD-EX",   "COPD-Exazerbation",                             "DIAGNOSE", "J44.1",  "P2", "O2 (Ziel SpO2 88–92%), NIV, Bronchodilatator, Kortison"),
    SpecEntry("ASTHMA",    "Asthma bronchiale / Asthmaanfall",              "DIAGNOSE", "J45.9",  "P2", "Beta-2-Mimetika, Kortison, Mg, NIV, Intubation als Last"),
    SpecEntry("PNEUMONIE", "Pneumonie / Lungenentzündung",                   "DIAGNOSE", "J18.9",  "P2", "CRB-65, Antibiotika, O2"),
    SpecEntry("CAP",       "Community-acquired Pneumonia (ambulant)",        "DIAGNOSE", "J18.9",  "P2", "CRB-65, Amoxicillin ± Makrolid"),
    SpecEntry("HAP",       "Hospital-acquired Pneumonia (nosokomial)",       "DIAGNOSE", "J18.9",  "P1", "Breit antibiotisch, MRSA decken"),
    SpecEntry("CRB65",     "CRB-65 Score (Pneumonie-Schwere)",              "DIAGNOSE", None,     "P2", "Confusion, RR, Alter, 0=ambulant, ≥3=ICU"),
    SpecEntry("PLEURITIS", "Pleuritis",                                      "DIAGNOSE", "R09.1",  "P3", "Atemabhängig, Reibegeräusch, Ursache"),
    SpecEntry("FIBRPUL",   "Lungenfibrose / Interstitielle Lungenerkrankung","DIAGNOSE", "J84.1",  "P3", "HRCT, Antifibrotika, Transplantation"),
]

# ============================================================================
# MASTER-REGISTRY: Alle Fachbereiche
# ============================================================================
SPECIALTY_MODULES: dict[str, dict] = {
    "NEU": {
        "name": "Neurologie",
        "description": "Schlaganfall, Epilepsie, Bewusstseinsstörungen, Scores",
        "icon": "🧠",
        "entries": NEUROLOGIE,
        "priority_focus": ["P1", "P2"],
    },
    "RAD": {
        "name": "Radiologie",
        "description": "Bildgebungsmodalitäten, Befunde, Kontrastmittel",
        "icon": "🔬",
        "entries": RADIOLOGIE,
        "priority_focus": ["P1", "P2", "P3"],
    },
    "KAR": {
        "name": "Kardiologie",
        "description": "Herzrhythmus, Herzinsuffizienz, Klappen, Interventionen",
        "icon": "❤️",
        "entries": KARDIOLOGIE,
        "priority_focus": ["P1", "P2"],
    },
    "INT": {
        "name": "Intensivmedizin",
        "description": "Beatmung, Monitoring, Nierenersatz, ICU-Scores",
        "icon": "🏥",
        "entries": INTENSIVMEDIZIN,
        "priority_focus": ["P1"],
    },
    "PÄD": {
        "name": "Pädiatrie",
        "description": "Kindliche Notfälle, Dosierungen, Entwicklung",
        "icon": "👶",
        "entries": PÄDIATRIE,
        "priority_focus": ["P1", "P2"],
    },
    "CHI": {
        "name": "Chirurgie / Traumatologie",
        "description": "Polytrauma, ATLS, abdominelle Notfälle",
        "icon": "🔪",
        "entries": CHIRURGIE,
        "priority_focus": ["P1", "P2"],
    },
    "PSY": {
        "name": "Psychiatrie",
        "description": "Suizidalität, Delir, Psychose, Erregungszustände",
        "icon": "🧩",
        "entries": PSYCHIATRIE,
        "priority_focus": ["P1", "P2"],
    },
    "GAS": {
        "name": "Gastroenterologie",
        "description": "GI-Blutung, Lebererkrankungen, Pankreatitis",
        "icon": "🫀",
        "entries": GASTROENTEROLOGIE,
        "priority_focus": ["P1", "P2"],
    },
    "PUL": {
        "name": "Pneumologie",
        "description": "COPD, Asthma, Pneumonie, Pleura",
        "icon": "🫁",
        "entries": PNEUMOLOGIE,
        "priority_focus": ["P1", "P2"],
    },
}


def get_all_entries() -> list[SpecEntry]:
    """Alle Einträge aller Fachbereiche zusammengeführt."""
    all_entries: list[SpecEntry] = []
    for spec in SPECIALTY_MODULES.values():
        all_entries.extend(spec["entries"])
    return all_entries


def get_by_priority(priority: str) -> list[SpecEntry]:
    """Alle Einträge einer bestimmten Priorität über alle Fachbereiche."""
    return [e for e in get_all_entries() if e.priority_hint == priority]
