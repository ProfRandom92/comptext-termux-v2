"""
Intensivmedizin – MedCodex Fachbereichs-Daten
"""
from __future__ import annotations

SPECIALTY = "Intensivmedizin"
CATEGORY_TAG = "INTENSIV"

CODEX_ENTRIES: list[tuple] = [
    # Monitoring
    ("ZVK",          "Zentralvenöser Katheter",                                  "INTENSIV",  None,     "P1", "V.jug./subclavia/femoralis, ZVD, Medikamente"),
    ("ART-KATHETER", "Arterieller Katheter / Arterielle Blutdruckmessung",      "INTENSIV",  None,     "P1", "A.radialis/femoralis, invasive RR-Messung, Blutgas"),
    ("PAK",          "Pulmonalarterienkatheter (Swan-Ganz)",                     "INTENSIV",  None,     "P2", "PCWP, HZV, PVR, seltener verwendet"),
    ("PICCO",        "Pulskontur-Herzzeitvolumenmessung",                       "INTENSIV",  None,     "P2", "HZV, ITBV, EVLW, Vorlast-Assessment"),
    ("ICP-SONDE",    "Intrakranielle Drucksonde",                               "INTENSIV",  None,     "P1", "Normal <15mmHg, CPP=MAP-ICP >60mmHg"),
    ("ZVD",          "Zentralvenöser Druck",                                    "INTENSIV",  None,     "P2", "Normal 2-8mmHg, Volumenstatus-Hinweis (unzuverlässig)"),
    ("SVO2",         "Gemischtvenöse Sauerstoffsättigung",                      "INTENSIV",  None,     "P2", ">65% = ausreichendes HZV/O2-Angebot"),
    ("SCVO2",        "Zentralvenöse Sauerstoffsättigung",                       "INTENSIV",  None,     "P2", ">70% angestrebt, Surrogat SVO2"),

    # Beatmung
    ("INTUB",        "Orotracheale Intubation",                                  "INTENSIV",  None,     "P1", "RSI, Videolaryngoskop, Cuff-Druck 20-30cmH2O"),
    ("RSI",          "Rapid Sequence Induction (Blitzintubation)",              "INTENSIV",  None,     "P1", "Etomidat + Succinylcholin oder Rocuronium, Krikoiddruck"),
    ("BEATMUNG",     "Invasive mechanische Beatmung",                            "INTENSIV",  None,     "P1", "Tidalvolumen 6ml/kg IBW, PEEP, FiO2"),
    ("PEEP",         "Positiver Endexspiratorischer Druck",                     "INTENSIV",  None,     "P1", "ARDS: 8-15cmH2O; Oxygenierung + Rekrutierung"),
    ("ARDS",         "Akutes Respiratory Distress Syndrome",                    "INTENSIV",  "J80",    "P1", "Berlin-Def: P/F <300, bilat. Infiltrate, 6ml/kg, Bauchlage"),
    ("NIV",          "Nicht-invasive Beatmung (CPAP/BiPAP)",                    "INTENSIV",  None,     "P2", "Lungenödem, COPD-Exazerbation, Immunsupprimierte"),
    ("BAUCHLAGE",    "Bauchlagerung bei ARDS",                                  "INTENSIV",  None,     "P1", "P/F <150, ≥16h/Tag, Oxygenierungsverbesserung"),
    ("HFNO",         "High-Flow Nasal Oxygen",                                  "INTENSIV",  None,     "P2", "Bis 60L/min, FiO2 bis 100%, Hypoxämie ohne Hyperkapnie"),
    ("TRACH",        "Tracheotomie / Perkutane Dilatationstracheotomie",        "INTENSIV",  None,     "P2", "Prolongierte Beatmung >7-10 Tage, Weaning-Vorbereitung"),
    ("WEANING",      "Beatmungsentwöhnung",                                     "INTENSIV",  None,     "P2", "SBT, RSBI <105, Extubationskriterien"),

    # Hämodynamik / Schock
    ("SEP-BUNDLE",   "Sepsis-Bundle (1h-Bundle)",                               "INTENSIV",  "R65.2",  "P1", "BK, Laktat, Antibiotika, 30ml/kg NaCl, Vasopressor"),
    ("VASOPRESSOR",  "Vasopressor-Therapie",                                    "INTENSIV",  None,     "P1", "Noradrenalin first-line, MAP-Ziel ≥65mmHg"),
    ("IABP",         "Intraaortale Ballonpumpe",                                "INTENSIV",  None,     "P1", "Kardiogener Schock, Counterpulsation"),
    ("IMPELLA",      "Impella Herzunterstützungssystem",                        "INTENSIV",  None,     "P1", "Kardiogener Schock, Axialfluss bis 5.5L/min"),
    ("ECMO-VV",      "Veno-venöse ECMO (pulmonales Versagen)",                  "INTENSIV",  None,     "P1", "Schwerstes ARDS, P/F <80, 6ml/kg nicht möglich"),
    ("ECMO-VA",      "Veno-arterielle ECMO (Herzversagen)",                     "INTENSIV",  None,     "P1", "Kardiogener Schock, Reanimation (ECPR)"),
    ("MAP",          "Mittlerer Arterieller Druck",                             "INTENSIV",  None,     "P1", "Ziel ≥65mmHg (Sepsis), ≥80mmHg bei SHT/Rückenmark"),

    # Nierenersatz
    ("CVVHDF",       "Kontinuierliche Veno-Venöse Hämodiafiltration",          "INTENSIV",  None,     "P2", "Akutes Nierenversagen, hämodynamisch instabil"),
    ("HD-INTER",     "Intermittierende Hämodialyse",                            "INTENSIV",  None,     "P2", "AKI, hämodynamisch stabil"),
    ("ANV",          "Akutes Nierenversagen",                                   "INTENSIV",  "N17.9",  "P2", "KDIGO-Kriterien: Kreatinin +0.3mg/dl oder Oligurie"),
    ("OLIGURIE",     "Oligurie (<0.5ml/kg/h für >6h)",                          "INTENSIV",  "R34",    "P2", "Volumenstatus, RR, KM?, ANV?"),

    # Scores ICU
    ("SOFA",         "Sequential Organ Failure Assessment Score",               "SCORE",     None,     "P1", "Organdysfunktion, ≥2 Punkte = Sepsis, Prognose"),
    ("APACHE2",      "Acute Physiology And Chronic Health Evaluation II",       "SCORE",     None,     "P2", "ICU-Mortalitätsprädiktion, 0-71 Punkte"),
    ("SAPS2",        "Simplified Acute Physiology Score II",                    "SCORE",     None,     "P2", "ICU-Score, 17 Variablen, 0-163 Punkte"),
    ("RASS",         "Richmond Agitation-Sedation Scale",                       "SCORE",     None,     "P2", "-5 (unerregbar) bis +4 (aggressiv), Ziel -1 bis 0"),
    ("SAS",          "Sedation-Agitation Scale",                                "SCORE",     None,     "P2", "1-7, Sedierungstiefe ICU"),
    ("CAM-ICU",      "Confusion Assessment Method for ICU (Delir)",            "SCORE",     None,     "P2", "Delir-Screening ICU, ABCDEF-Bundle"),
    ("CPOT",         "Critical-Care Pain Observation Tool",                     "SCORE",     None,     "P2", "Schmerzerfassung beim nicht-kommunikativen Pat."),

    # Medikamente ICU
    ("PROPOFOL",     "Propofol",                                                "MEDIKAMENT", None,    "P2", "Sedierung, PRIS-Risiko >4mg/kg/h, kurze Halbwertzeit"),
    ("MIDAZOLAM-ICU","Midazolam (ICU-Sedierung)",                              "MEDIKAMENT", None,    "P2", "Sedierung, Kumulation, verlängerte Aufwachzeit"),
    ("FENTANYL",     "Fentanyl",                                                "MEDIKAMENT", None,    "P1", "Analgesie ICU, Titrierbar, Kumulation"),
    ("KETAMIN",      "Ketamin",                                                  "MEDIKAMENT", None,    "P2", "Analgosedierung, Bronchodilatation, Asthma-Status"),
    ("DEXMEDET",     "Dexmedetomidin",                                          "MEDIKAMENT", None,    "P2", "Alpha-2-Agonist, weniger Delir, kooperative Sedierung"),
    ("SUCCINYL",     "Succinylcholin",                                          "MEDIKAMENT", None,    "P1", "RSI 1.5mg/kg, depolarisierend, cave: Hyperkaliämie"),
    ("ROCURONIUM",   "Rocuronium",                                              "MEDIKAMENT", None,    "P1", "RSI 1.2mg/kg, nicht-depolarisierend, Sugammadex-Antagonist"),
    ("SUGAMMADEX",   "Sugammadex",                                              "MEDIKAMENT", None,    "P1", "Rocuronium-Antagonist, 16mg/kg bei sofortiger Umkehr"),
    ("NORADR-ICU",   "Noradrenalin (ICU-Dosierung)",                           "MEDIKAMENT", None,    "P1", "0.01-3µg/kg/min, Vasopressor, MAP-Ziel"),
    ("VASOPRESSIN",  "Vasopressin",                                             "MEDIKAMENT", None,    "P1", "0.03-0.04E/min, Katecholamin-sparend im sep. Schock"),
    ("HYDROKORT",    "Hydrokortison (ICU)",                                     "MEDIKAMENT", None,    "P2", "Sep. Schock: 200mg/d, ARDS: 1-2mg/kg, Nebenniereninsuff."),
    ("INSULIN-ICU",  "Insulin-Infusion (ICU Blutzuckerkontrolle)",             "MEDIKAMENT", None,    "P2", "BZ-Ziel 140-180mg/dl (8-10mmol/L) auf ICU"),
]

def get_entries() -> list[tuple]:
    return CODEX_ENTRIES
def get_specialty() -> str:
    return SPECIALTY
def get_count() -> int:
    return len(CODEX_ENTRIES)
