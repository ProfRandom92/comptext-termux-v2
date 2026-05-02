"""
Kardiologie – MedCodex Fachbereichs-Daten
"""
from __future__ import annotations

SPECIALTY = "Kardiologie"
CATEGORY_TAG = "KARDIOLOGIE"

CODEX_ENTRIES: list[tuple] = [
    # Notfälle
    ("STEMI-ANT",    "Anteriorer STEMI (LAD-Verschluss)",                        "KARDIOLOGIE","I21.0",  "P1", "V1-V6 Hebungen, Herzkatheter sofort"),
    ("STEMI-INF",    "Inferiorer STEMI (RCA-Verschluss)",                        "KARDIOLOGIE","I21.1",  "P1", "II, III, aVF Hebungen, RV-Infarkt?"),
    ("LBBB-NEU",     "Neu aufgetretener Linksschenkelblock",                     "KARDIOLOGIE","I44.7",  "P1", "STEMI-Äquivalent, Herzkatheter"),
    ("AORTDISS",     "Aortendissektion (Kardiologie)",                           "KARDIOLOGIE","I71.0",  "P1", "Stanford A → CardioChir, B → RR-Senkung"),
    ("TACHYA",       "Tachyarrhythmie",                                          "KARDIOLOGIE","I49.9",  "P1", "EKG 12-Kanal, Vagusmanöver, Adenosin, Kardioversion"),
    ("VORHOFFLIMM",  "Vorhofflimmern",                                           "KARDIOLOGIE","I48.9",  "P2", "Frequenz, Dauer? <48h → Kardioversion erwägen, Antikoag"),
    ("HERZINSUFF",   "Herzinsuffizienz / Dekompensierte HI",                    "KARDIOLOGIE","I50.9",  "P2", "EF, NYHA, BNP, Diuretika, CPAP"),
    ("TAMPONADE",    "Perikardtamponade",                                        "KARDIOLOGIE","I31.9",  "P1", "Beck-Trias, Echo, Perikardpunktion"),
    ("EF↓",          "Reduzierte Ejektionsfraktion (<40%)",                     "KARDIOLOGIE","I50.9",  "P2", "HFrEF, ACE-Hemmer, Beta-Blocker, MRA, SGLT2"),

    # Diagnostik
    ("EKG-12",       "12-Kanal-EKG",                                            "KARDIOLOGIE", None,    "P2", "Rhythmus, Achse, PQ, QRS, QTc, ST, T"),
    ("TROPONIN",     "Troponin-T/I hochsensitiv (hsTnT/hsTnI)",                "KARDIOLOGIE","R94.3",  "P1", "0h/1h/2h-Algorithmus, Delta-Troponin"),
    ("BNP",          "Brain Natriuretisches Peptid",                            "KARDIOLOGIE","R79.8",  "P2", "Herzinsuffizienz-Marker, >400pg/ml = schwere HI"),
    ("NT-PROBNP",    "NT-proBNP",                                               "KARDIOLOGIE","R79.8",  "P2", "HI-Marker, altersabhängige Cut-offs"),
    ("ECHO-TTE",     "Transthorakale Echokardiographie",                        "KARDIOLOGIE", None,    "P2", "EF, Wandbewegung, Klappen, Perikard, IVC"),
    ("ECHO-TEE",     "Transösophageale Echokardiographie",                      "KARDIOLOGIE", None,    "P2", "LAA-Thrombus, Klappen, Endokarditis, Aorta"),
    ("HERZKATHO",    "Herzkatheteruntersuchung (Koronarangiographie)",           "KARDIOLOGIE", None,    "P1", "PCI, PTCA, Stent; LVEF, Koronarmorphologie"),
    ("ICD",          "Implantierbarer Kardioverter-Defibrillator",              "KARDIOLOGIE", None,    "P2", "Primär-/Sekundärprophylaxe plötzl. Herztod"),
    ("CRT",          "Kardiale Resynchronisationstherapie",                     "KARDIOLOGIE", None,    "P3", "HFrEF + LBBB + QRS>150ms"),
    ("LZEK",         "Langzeit-EKG / Holter-EKG",                              "KARDIOLOGIE", None,    "P3", "24-72h, paroxysmales VHF, Synkopen-Abklärung"),
    ("KIPPTISCH",    "Kipptischuntersuchung",                                   "KARDIOLOGIE", None,    "P3", "Synkopen-Abklärung, vasovagal"),

    # Medikamente
    ("BETA-BLOCK",   "Beta-Blocker",                                            "MEDIKAMENT",  None,    "P2", "HI: Metoprolol/Bisoprolol/Carvedilol; ACS: Metoprolol"),
    ("ACE-HEMMER",   "ACE-Hemmer",                                              "MEDIKAMENT",  None,    "P2", "HI: Ramipril/Lisinopril; RR; Niere+Kalium kontrollieren"),
    ("ARB",          "Angiotensin-Rezeptorblocker (Sartane)",                   "MEDIKAMENT",  None,    "P2", "Alternative ACE-Hemmer, Valsartan, Candesartan"),
    ("SGLT2I",       "SGLT-2-Inhibitor (Gliflozine)",                           "MEDIKAMENT",  None,    "P2", "HFrEF: Empagliflozin/Dapagliflozin, Prognoseverbesserung"),
    ("MRA",          "Mineralokortikoid-Antagonist",                            "MEDIKAMENT",  None,    "P2", "HFrEF: Spironolacton/Eplerenon, Kalium-Kontrolle"),
    ("STATIN",       "HMG-CoA-Reduktase-Inhibitor (Statin)",                    "MEDIKAMENT",  None,    "P2", "Atorvastatin/Rosuvastatin, LDL-Ziel <55 bei ACS"),
    ("P2Y12",        "P2Y12-Inhibitor (Thienopyridin/Prasugrel/Ticagrelor)",    "MEDIKAMENT",  None,    "P1", "DAPT nach PCI: ASS+Ticagrelor oder ASS+Clopidogrel"),
    ("AMIOD-ORAL",   "Amiodaron oral",                                          "MEDIKAMENT",  None,    "P3", "VHF-Erhaltungstherapie, Schilddrüse+Lunge kontrollieren"),
    ("DIGOXIN",      "Digoxin",                                                 "MEDIKAMENT",  None,    "P3", "VHF-Frequenzkontrolle, enger therapeutischer Bereich"),

    # Scores
    ("EUROSCORE",    "EuroSCORE II (Herzchirurgie-Risiko)",                     "SCORE",       None,    "P2", "OP-Mortalitätsrisiko bei Herzoperationen"),
    ("GRACE",        "GRACE-Score (ACS-Risiko)",                                "SCORE",       None,    "P2", "In-Hospital + 6-Monats-Mortalität bei NSTEMI"),
    ("TIMI",         "TIMI-Score",                                              "SCORE",       None,    "P2", "STEMI: Fibrinolyse-Outcome; NSTEMI: Risikostratifizierung"),
    ("CHA2DS2",      "CHA2DS2-VASc-Score (Schlaganfallrisiko bei VHF)",         "SCORE",       None,    "P2", "≥2 Punkte → Antikoagulation; Frauen +1"),
    ("HASBLED",      "HAS-BLED-Score (Blutungsrisiko unter OAK)",               "SCORE",       None,    "P2", "≥3 = hohes Blutungsrisiko"),
    ("NYHA",         "NYHA-Klassifikation Herzinsuffizienz",                    "SCORE",       None,    "P3", "I-IV, Belastbarkeit"),
]

def get_entries() -> list[tuple]:
    return CODEX_ENTRIES
def get_specialty() -> str:
    return SPECIALTY
def get_count() -> int:
    return len(CODEX_ENTRIES)
