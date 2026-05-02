"""
Radiologie – MedCodex Fachbereichs-Daten
==========================================
Spezialisierte Kürzel für diagnostische und interventionelle Radiologie.
Bildgebungsmodalitäten, Befundkürzel, Kontrastmittel, BIRADS/TIRADS.
"""
from __future__ import annotations

SPECIALTY = "Radiologie"
CATEGORY_TAG = "RADIOLOGIE"

CODEX_ENTRIES: list[tuple] = [

    # =========================================================================
    # MODALITÄTEN
    # =========================================================================
    ("CT-NATIV",     "Computertomographie ohne Kontrastmittel",                  "BILDGEBUNG", None,    "P2", "Kein KM, schnell, Blutung/Fraktur/Pneumothorax"),
    ("CT-KM",        "Computertomographie mit Kontrastmittel",                   "BILDGEBUNG", None,    "P2", "Jodhaltig, Nierenfunktion prüfen, Allergie?"),
    ("CT-ANGIO",     "CT-Angiographie",                                          "BILDGEBUNG", None,    "P2", "Arterien: AAS, PE, Karotis, Mesenterial"),
    ("CXR",          "Röntgen-Thorax (Chest X-Ray)",                             "BILDGEBUNG", None,    "P3", "p.a. + lat, Pneumonie, Pneumothorax, Herzgröße"),
    ("MRT-KM",       "MRT mit Kontrastmittel (Gadolinium)",                      "BILDGEBUNG", None,    "P2", "Gadolinium, NSF-Risiko bei Niereninsuffizienz"),
    ("MRT-DWI",      "MRT Diffusionswichtung",                                   "BILDGEBUNG", None,    "P1", "Frischer Infarkt, Abszess, Tumordifferenzierung"),
    ("MRT-T1",       "MRT T1-Wichtung",                                          "BILDGEBUNG", None,    "P3", "Anatomie, Fett hyperintens, Blut (subakut)"),
    ("MRT-T2",       "MRT T2-Wichtung",                                          "BILDGEBUNG", None,    "P3", "Flüssigkeit hyperintens, Ödeme, Entzündung"),
    ("MRT-FLAIR",    "MRT FLAIR-Sequenz",                                        "BILDGEBUNG", None,    "P3", "T2 mit Liquor-Unterdrückung, MS-Plaques, perivask."),
    ("SONO",         "Sonographie / Ultraschall",                                "BILDGEBUNG", None,    "P3", "B-Bild, Doppler, keine Strahlung, bettseitig"),
    ("SONO-DUPLEX",  "Duplex-Sonographie (B-Bild + Doppler)",                    "BILDGEBUNG", None,    "P3", "Karotis, Vertebralarterien, Venen, Leberportal"),
    ("SONO-ECHO",    "Echokardiographie (Cardiac Echo)",                         "BILDGEBUNG", None,    "P2", "TTE/TEE, Klappen, EF, Perikard, Thrombus"),
    ("RÖNTGEN",      "Konventionelle Röntgenaufnahme",                           "BILDGEBUNG", None,    "P3", "Knochen, Gelenk, Thorax, Abdomenübersicht"),
    ("FLUORO",       "Fluoroskopie / Durchleuchtung",                            "BILDGEBUNG", None,    "P3", "Schluckakt, GI-Passage, Intervention"),
    ("MAMMOG",       "Mammographie",                                              "BILDGEBUNG", None,    "P3", "Screening + Diagnostik Mamma"),
    ("SZINTI",       "Szintigraphie",                                            "BILDGEBUNG", None,    "P3", "Knochen-, Schilddrüsen-, Lungen-, Herzszinti"),
    ("PET-CT",       "Positronenemissionstomographie-CT",                        "BILDGEBUNG", None,    "P3", "Onkologie, FDG, PSMA, DOTATATE"),
    ("DEXA",         "DEXA-Knochendichtemessung",                                "BILDGEBUNG", None,    "P4", "Osteoporose-Screening, T-Score"),
    ("INTERV",       "Interventionelle Radiologie",                              "BILDGEBUNG", None,    "P2", "TACE, TIPSS, Embolisation, Stent, Drainagen"),

    # =========================================================================
    # BEFUNDE / BEFUNDKÜRZEL
    # =========================================================================
    ("PNEUMO",       "Pneumothorax",                                             "DIAGNOSE",  "J93.9",  "P1", "CXR: Fehlende Lungenzeichnung, Spannungs-PT? Nadel!"),
    ("PLERG",        "Pleuraerguss",                                             "DIAGNOSE",  "J90",    "P3", "Sono/CXR, Ursache, Punktion?"),
    ("PNEU-RADIO",   "Pneumonie (radiologischer Befund)",                        "DIAGNOSE",  "J18.9",  "P2", "CXR: Infiltrat, Verschattung, Segment?"),
    ("ATELEKT",      "Atelektase",                                               "DIAGNOSE",  "J98.1",  "P3", "Plattenatelektase vs. Lappenatelektase"),
    ("LUNGENÖDEM-R", "Lungenödem (radiologisch)",                               "DIAGNOSE",  "J81.0",  "P1", "CXR: Schmetterlingsform, Kerley-B-Linien, Cephalisierung"),
    ("KARDINEG",     "Kardiale Negativbefund / normales Herzsilhouette",        "DIAGNOSE",  None,     "P4", "CTR <0.5 p.a."),
    ("FRAKTUR-R",    "Fraktur (radiologisch gesichert)",                        "DIAGNOSE",  "S00-S99","P2", "Kortikalisunterbrechung, Versatz, Dislokation"),
    ("OSTEOLYSE",    "Osteolyse / Knochendestruktion",                           "DIAGNOSE",  None,     "P2", "Metastase? Myelom? Osteomyelitis?"),
    ("VERKALK",      "Verkalkung / Kalzifikation",                               "DIAGNOSE",  None,     "P4", "Lokation: Koronar, Aortal, Weichteile"),
    ("LYMPHADENOP",  "Lymphadenopathie (CT/MRT)",                               "DIAGNOSE",  "R59.1",  "P2", "Kurzachse >10mm mediastinal, >15mm retroperitoneal"),
    ("RAUMFORD",     "Raumforderung / Läsion (unspezifisch)",                   "DIAGNOSE",  None,     "P2", "Größe, KM-Verhalten, Rand, Diffusion, Dignität?"),
    ("KONTRASTMITTELSCHADEN", "Kontrastmittel-induzierte Nephropathie",        "DIAGNOSE",  "N14.1",  "P2", "Kreatinin +25% oder >0.5mg/dl in 48h, Hydrierung"),

    # =========================================================================
    # GEFÄSS / VASKULÄR
    # =========================================================================
    ("AAS",          "Aortales Akutes Syndrom / Aortendissektion",               "DIAGNOSE",  "I71.0",  "P1", "CT-Angio Thorax+Abdomen, Stanford A → Chirurgie, B → med."),
    ("AAA",          "Abdominales Aortenaneurysma",                              "DIAGNOSE",  "I71.4",  "P2", ">3cm, Ruptur-Risiko >5.5cm, EVAR/offen"),
    ("TVT",          "Tiefe Venenthrombose",                                     "DIAGNOSE",  "I82.9",  "P2", "Kompression-Sono, D-Dimer, Heparin"),
    ("LAE",          "Lungenarterienembolie",                                    "DIAGNOSE",  "I26.9",  "P1", "CT-Pulmonalisangio (CTPA), Heparin, Lyse bei massiver PE"),
    ("MESISCHÄMIE",  "Mesenteriale Ischämie",                                    "DIAGNOSE",  "K55.0",  "P1", "CT-Angio A.mesenterica, Chirurgie"),

    # =========================================================================
    # KLASSIFIKATIONEN / SCORES
    # =========================================================================
    ("BIRADS",       "Breast Imaging Reporting and Data System (Mammographie)",  "SCORE",     None,     "P3", "0=unvollständig, 1=negativ, 4=suspekt, 5=malignitätsverdächtig"),
    ("TIRADS",       "Thyroid Imaging Reporting and Data System (Sono)",         "SCORE",     None,     "P3", "ACR-TIRADS: 1-5, Empfehlung zur FNB"),
    ("LI-RADS",      "Liver Imaging Reporting and Data System (HCC)",            "SCORE",     None,     "P3", "LR-1 bis LR-5, HCC-Wahrscheinlichkeit"),
    ("PI-RADS",      "Prostate Imaging Reporting and Data System (mpMRT)",       "SCORE",     None,     "P3", "1-5, klinisch signifikantes Karzinom"),
    ("LUNG-RADS",    "Lung CT Screening Reporting System",                       "SCORE",     None,     "P3", "Lungenkarzinom-Screening LDCT"),
    ("ASPECTS",      "Alberta Stroke Program Early CT Score",                   "SCORE",     None,     "P1", "10=normal, <6 → schlechteres Thrombolyse-Outcome"),
    ("FISCHER",      "Fischer-Grad (SAB CT)",                                   "SCORE",     None,     "P1", "I-IV SAB-Menge, Vasospasmusprädiktor"),

    # =========================================================================
    # KONTRASTMITTEL / SICHERHEIT
    # =========================================================================
    ("KM-JODHALTIG", "Iodhaltiges Kontrastmittel (CT)",                         "MEDIKAMENT", None,    "P3", "Cave: Allergie, Niereninsuffizienz, Metformin, Thyreotoxikose"),
    ("KM-GADOLIN",   "Gadolinium-haltiges Kontrastmittel (MRT)",                "MEDIKAMENT", None,    "P3", "Cave: NSF bei GFR<30, Schwangerschaft"),
    ("PRÄMED-KM",    "KM-Prämedikation (Allergie-Prophylaxe)",                  "MEDIKAMENT", None,    "P3", "Kortison + Antihistaminikum, 12h vor KM-Gabe"),
    ("N-ACC",        "N-Acetylcystein (KM-Nephropathie-Prophylaxe)",            "MEDIKAMENT", None,    "P3", "600mg 2x/d, Tag vor + Tag KM-Gabe, umstritten"),
]


def get_entries() -> list[tuple]:
    return CODEX_ENTRIES

def get_specialty() -> str:
    return SPECIALTY

def get_count() -> int:
    return len(CODEX_ENTRIES)
