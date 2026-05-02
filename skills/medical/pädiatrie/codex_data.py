"""
Pädiatrie – MedCodex Fachbereichs-Daten
"""
from __future__ import annotations

SPECIALTY = "Pädiatrie"
CATEGORY_TAG = "PÄDIATRIE"

CODEX_ENTRIES: list[tuple] = [
    # Notfälle Kinder
    ("KRAMPF-KIND",  "Krampfanfall beim Kind / Pädiatrischer Anfall",           "PÄDIATRIE", "G40.3",  "P1", "Dauer, Benzo buccal/nasal, Fieberkrampf?"),
    ("FEBR-KRAMPF",  "Fieberkrampf",                                            "PÄDIATRIE", "R56.0",  "P2", "6M-5J, Temp↑, einfach vs. komplex, EEG?"),
    ("KRUPP",        "Krupp-Syndrom / Stenosierende Laryngitis",                "PÄDIATRIE", "J05.0",  "P2", "Bellender Husten, inspiratorischer Stridor, Steroide/Epinephrin"),
    ("EPIGLOTTITIS-K","Epiglottitis beim Kind",                                 "PÄDIATRIE", "J05.1",  "P1", "HiB, kein Rachenspatel! Intubation vorbereiten"),
    ("BRONCHIOL",    "Bronchiolitis (RSV)",                                     "PÄDIATRIE", "J21.0",  "P2", "Säugling <2J, RSV, supportiv, O2, Nahrsonde"),
    ("DKA-KIND",     "Diabetische Ketoazidose bei Kindern",                     "PÄDIATRIE", "E10.1",  "P1", "pH, BE, Volumengabe langsam (Hirnödem-Risiko!)"),
    ("SEPSIS-KIND",  "Pädiatrische Sepsis",                                     "PÄDIATRIE", "R65.2",  "P1", "SIRS-Kriterien kinderspez., Bolus 10ml/kg, Antibiotika"),
    ("MENINGITIS-K", "Meningitis beim Kind",                                    "PÄDIATRIE", "G00.9",  "P1", "Fontanelle, Meningismus, LP, Cefotaxim/Amoxicillin"),
    ("ANAPHYL-KIND", "Anaphylaxie beim Kind",                                   "PÄDIATRIE", "T78.2",  "P1", "Adrenalin 0.01mg/kg i.m. (max 0.5mg), auto-injektor"),
    ("ERTRINKEN",    "Fast-Ertrinken / Beinahe-Ertrinken",                      "PÄDIATRIE", "T75.1",  "P1", "Hypothermie, Hypoxie, REA, Wärmen"),

    # Neonatologie
    ("NEONAT-ADAPT", "Neonatale Adaptation / APGAR-Bewertung",                  "PÄDIATRIE", "Z38.0",  "P2", "APGAR 1/5/10min, Abtrocknen, Wärmen, Atemstimulation"),
    ("APGAR",        "APGAR-Score (Neugeborenen-Bewertung)",                    "SCORE",     None,     "P2", "Farbe, Herzrate, Reflexe, Tonus, Atmung; 0-10"),
    ("NEO-REA",      "Neonatale Reanimation",                                   "PÄDIATRIE", "P21.0",  "P1", "Wärmen, Stimulieren, O2, PPV, Herzdruckmassage, Adrenalin"),
    ("FRÜHGEB",      "Frühgeburt (<37. SSW)",                                   "PÄDIATRIE", "P07.3",  "P2", "Atemnotsyndrom, Surfactant, Wärme, Infektprophylaxe"),
    ("SURFACTANT",   "Surfactant-Therapie",                                     "MEDIKAMENT", None,    "P1", "Atemnotsyndrom, INSURE-Technik, Poractant alpha"),
    ("IKTERUS-NEO",  "Neonataler Ikterus",                                      "PÄDIATRIE", "P59.9",  "P3", "Bilirubinwert, Phototherapie, Austauschtransfusion"),
    ("NEC",          "Nekrotisierende Enterokolitis",                           "PÄDIATRIE", "P77.9",  "P1", "Frühgeburt, Blähbauch, Bell-Staging, OP?"),

    # Allgemeine Pädiatrie
    ("FUO-KIND",     "Fieber unklarer Ursache beim Kind",                       "PÄDIATRIE", "R50.9",  "P3", "Fokussuche, Alter, Dauer, Exposition"),
    ("EXANTHEM",     "Exanthem beim Kind",                                      "PÄDIATRIE", "R21",    "P3", "Masern, Röteln, Scharlach, Varizellen, Ringelröteln"),
    ("OTITIS-MEDIA", "Akute Otitis Media",                                      "PÄDIATRIE", "H66.0",  "P3", "Fieber, Ohrenschmerz, Parazentese, Antibiotika ≥2J"),
    ("TONSILLITIS",  "Tonsillitis / Streptokokken-Angina",                      "PÄDIATRIE", "J03.9",  "P3", "CENTOR-Score, Strep-Schnelltest, Penicillin V"),
    ("APPENDIZITIS", "Appendizitis",                                            "PÄDIATRIE", "K37",    "P2", "Pedriatic Appendicitis Score, Sono, CT, Appendektomie"),
    ("INTUSSUS",     "Invagination / Ileokolische Invagination",               "PÄDIATRIE", "K56.1",  "P1", "6M-3J, kolikartige Schmerzen, Himbeergelee-Stuhl, Sono"),
    ("PYLORUS",      "Hypertrophe Pylorusstenose",                              "PÄDIATRIE", "Q40.0",  "P2", "3-8 Wochen, schwallartig Erbrechen, Sono, Pyloromyotomie"),

    # Gewicht / Dosierung (pädiatrisch)
    ("KG-KIND",      "Körpergewicht pädiatrisch (geschätzt)",                   "PÄDIATRIE", None,     "P2", "Broselow-Band, Formel: (Alter+4)×2 = KG in kg (2-10J)"),
    ("ETT-GRÖSSE",   "Tubusgröße pädiatrisch",                                 "PÄDIATRIE", None,     "P1", "ID (mm) = Alter/4 + 4 (ohne Cuff), Länge = Alter/2 + 12"),
    ("ADREN-KIND",   "Adrenalin pädiatrisch",                                   "MEDIKAMENT", None,    "P1", "REA: 0.01mg/kg IV, Anaphylaxie: 0.01mg/kg i.m. (max 0.5mg)"),
    ("MIDAZ-KIND",   "Midazolam pädiatrisch",                                   "MEDIKAMENT", None,    "P1", "Krampf: 0.3mg/kg buccal, 0.1mg/kg IV"),
    ("IBUPROFEN-K",  "Ibuprofen pädiatrisch",                                   "MEDIKAMENT", None,    "P3", "10mg/kg alle 6-8h, max 40mg/kg/d, >3 Monate"),
    ("PARACETAMOL-K","Paracetamol pädiatrisch",                                 "MEDIKAMENT", None,    "P3", "15mg/kg alle 4-6h, max 60mg/kg/d"),

    # Scores Pädiatrie
    ("PEDS-GCS",     "Pädiatrische GCS (modifiziert)",                         "SCORE",     None,     "P1", "Modifizierte Verbal-Skala für Kinder <5J"),
    ("PEWS",         "Paediatric Early Warning Score",                          "SCORE",     None,     "P2", "Frühwarnsystem Pädiatrie, ≥3 Punkte = Eskalation"),
    ("BRONCHIOL-SCORE","Bronchiolitis Schweregrad-Score",                       "SCORE",     None,     "P2", "Wang-Score: Wheezing, Einziehungen, Atemfrequenz, SpO2"),
    ("PECARN",       "PECARN (SHT-Entscheidungsregel Kinder)",                  "SCORE",     None,     "P2", "CT-Entscheidung bei pädiatrischem SHT"),
]

def get_entries() -> list[tuple]:
    return CODEX_ENTRIES
def get_specialty() -> str:
    return SPECIALTY
def get_count() -> int:
    return len(CODEX_ENTRIES)
