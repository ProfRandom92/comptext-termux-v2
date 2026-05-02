#!/usr/bin/env python3
"""
MedCodex – Medizinisches Token-Kompressions-Lexikon
====================================================
Kern des CompText-Konzepts: Kürzel → Expansion → schnellere LLM-Kommunikation.

Vorteile:
- Weniger Tokens = schnellere Inferenz auf ARM-CPU (Termux/A33)
- ePA-kompatibel: ICD-10, LOINC, OPS-Codes integriert
- Bidirektional: compress_prompt() + expand_prompt()
- SQLite-persistiert: Nutzungsstatistiken, erweiterbar

Prinzip:
    Eingabe: "MAB+HS, RR↓, HF↑ → ACS?"
    expand:  "Massive arterielle Blutung mit hämorrhagischem Schock, ..."
    → LLM bekommt Volltext, antwortet präziser
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class CodexEntry:
    shorthand: str           # z.B. "MAB+HS"
    expansion: str           # "Massive arterielle Blutung mit hämorrhagischem Schock"
    category: str            # "NOTFALL" | "SYMPTOM" | "DIAGNOSE" | "MEDIKAMENT" | "EPA" | "LABOR" | "ADMIN"
    icd10: Optional[str]     # "S35.9", "I21.9" – None wenn nicht anwendbar
    priority_hint: str       # "P1" – "P5"
    context: Optional[str]   # Klinische Zusatzinfo für den LLM


class MedCodex:
    """
    SQLite-basiertes Lexikon für medizinische Kurzformen.
    Wird transparent in den LLM-Prompt-Fluss eingebettet.
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS codex (
        shorthand TEXT PRIMARY KEY,
        expansion TEXT NOT NULL,
        category TEXT DEFAULT 'SYMPTOM',
        icd10 TEXT,
        priority_hint TEXT DEFAULT 'P4',
        context TEXT,
        usage_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_codex_cat  ON codex(category);
    CREATE INDEX IF NOT EXISTS idx_codex_prio ON codex(priority_hint);
    """

    # =========================================================================
    # DEFAULT CODEX – Deutsche Notfallmedizin + ePA/FHIR-Standards
    # =========================================================================
    DEFAULT_CODEX: list[tuple] = [

        # NOTFÄLLE – P1
        ("MAB",        "Massive arterielle Blutung",                        "NOTFALL", "S35.9",  "P1", "Hämorrhagischer Schock möglich – Volumengabe, Massivtransfusion"),
        ("MAB+HS",     "Massive arterielle Blutung mit hämorrhagischem Schock", "NOTFALL", "S35.9", "P1", "Volumengabe, Massivtransfusionsprotokoll, Chirurgie-Alert"),
        ("ACS",        "Akutes Koronarsyndrom",                              "NOTFALL", "I21.9",  "P1", "STEMI/NSTEMI, 12-Kanal-EKG, Troponin, Herzkatheter"),
        ("STEMI",      "ST-Hebungsinfarkt",                                  "DIAGNOSE","I21.3",  "P1", "Herzkatheter sofort, Lyse wenn kein Kath verfügbar"),
        ("NSTEMI",     "Non-ST-Hebungsinfarkt",                              "DIAGNOSE","I21.4",  "P2", "Troponin-Verlauf, Herzkatheter elektiv"),
        ("AP",         "Anaphylaxie / Anaphylaktischer Schock",              "NOTFALL", "T78.2",  "P1", "Adrenalin 0.3-0.5mg i.m., Volumen, Kortison, Antihistaminikum"),
        ("REA",        "Reanimation / kardiopulmonale Reanimation (CPR)",    "NOTFALL", "I46.9",  "P1", "30:2, Adrenalin 1mg alle 3-5min, Amiodaron bei VF/VT"),
        ("PÄD-REA",    "Pädiatrische Reanimation",                           "NOTFALL", "I46.9",  "P1", "15:2, 100-120/min, Adrenalin 0.01mg/kg, Volumen 10ml/kg"),
        ("RAU",        "Rauchgasinhalation",                                 "NOTFALL", "T59.8",  "P2", "CO-Hb, HNO-Ödem, 100% O2, bronchoskopie"),
        ("SHT",        "Schädel-Hirn-Trauma",                                "NOTFALL", "S06.9",  "P2", "GCS, CCT, Hämatom?, Neurochirurgie"),
        ("SEPSIS",     "Sepsis",                                             "DIAGNOSE","R65.2",  "P1", "qSOFA, Laktat, Blutkulturen, Antibiotika <1h, Volumen 30ml/kg"),
        ("SEP-SCHOCK", "Septischer Schock",                                  "DIAGNOSE","R65.21", "P1", "RR <90 trotz Volumen, Norad, ICU"),
        ("PE",         "Lungenembolie",                                      "DIAGNOSE","I26.9",  "P1", "D-Dimer, CTPA, Heparin, Lyse bei Massiv-PE"),
        ("APO",        "Akutes Lungenödem / Akute Linksherzdekompensation",  "DIAGNOSE","J81.0",  "P1", "CPAP, Nitro, Furosemid i.v., O2"),
        ("APOPLEX",    "Schlaganfall / Apoplex / Ischämischer Insult",       "DIAGNOSE","I63.9",  "P1", "FAST-Test, CT sofort, Lyse-Zeitfenster 4.5h"),
        ("STROKE",     "Schlaganfall (englische Variante)",                  "DIAGNOSE","I63.9",  "P1", "Wie APOPLEX"),
        ("KKS",        "Kreislaufstillstand",                                "NOTFALL", "I46.9",  "P1", "Sofort REA, AED, 112"),
        ("VF",         "Kammerflimmern",                                     "DIAGNOSE","I49.01", "P1", "Defibrillation sofort, Adrenalin"),
        ("VT",         "Ventrikuläre Tachykardie",                           "DIAGNOSE","I47.2",  "P1", "Amiodaron, Kardioversion wenn instabil"),

        # SYMPTOME
        ("THX",        "Thoraxschmerz",                                      "SYMPTOM", "R07.4",  "P2", "Druck, Ausstrahlung, Dyspnoe? → ACS ausschließen"),
        ("DYSP",       "Dyspnoe / Atemnot",                                  "SYMPTOM", "R06.0",  "P2", "SpO2, Auskultation, Lungenödem? PE?"),
        ("SYNK",       "Synkope / Bewusstlosigkeit",                         "SYMPTOM", "R55",    "P2", "Kreislauf? Arrhythmie? EEG?"),
        ("FAEB",       "Fieber unklarer Genese",                             "SYMPTOM", "R50.9",  "P3", "Infekt? Sepsis? Blutkulturen"),
        ("ABD-SCHM",   "Abdomineller Schmerz",                               "SYMPTOM", "R10.4",  "P3", "Peritonitis? Ileus? Appendizitis?"),
        ("ÜBELK",      "Übelkeit und Erbrechen",                             "SYMPTOM", "R11.2",  "P4", "Ursache klären"),
        ("SCHWIN",     "Schwindel / Vertigo",                                "SYMPTOM", "R42",    "P3", "Zentral vs. peripher, HINTS-Test"),
        ("KOPFSCHM",   "Kopfschmerzen",                                      "SYMPTOM", "R51",    "P3", "Donnerschlag? SAB ausschließen"),
        ("KRS-INST",   "Kreislaufinstabilität / Hämodynamische Instabilität","SYMPTOM", "R57.9",  "P1", "RR, HF, Ursachensuche"),

        # VITALZEICHEN (Abkürzungen für Notizen)
        ("RR↓",        "Hypotonie / niedriger Blutdruck",                    "SYMPTOM", "I95.9",  "P2", "RR <90/60 mmHg"),
        ("RR↑",        "Hypertonie / erhöhter Blutdruck",                    "SYMPTOM", "I10",    "P3", "RR >180/110 mmHg = hypertensiver Notfall"),
        ("HF↑",        "Tachykardie / erhöhte Herzfrequenz",                 "SYMPTOM", "R00.0",  "P2", "HF >100/min"),
        ("HF↓",        "Bradykardie / niedrige Herzfrequenz",                "SYMPTOM", "R00.1",  "P2", "HF <60/min, ggf. Atropin"),
        ("SpO2↓",      "Sauerstoffsättigung erniedrigt / Hypoxämie",         "SYMPTOM", "J96.0",  "P1", "SpO2 <90% → O2 sofort"),
        ("GCS↓",       "Glasgow Coma Scale vermindert / Bewusstseinsstörung","SYMPTOM", "R41.3",  "P2", "GCS <15 → Neurologie"),
        ("TEMP↑",      "Erhöhte Körpertemperatur / Fieber",                  "SYMPTOM", "R50.9",  "P3", ">38.5°C"),

        # MEDIKAMENTE / MAßNAHMEN
        ("ADREN",      "Adrenalin / Epinephrin",                             "MEDIKAMENT", None,  "P1", "Anaphylaxie 0.3mg i.m., REA 1mg i.v. alle 3-5min"),
        ("AMIO",       "Amiodaron",                                          "MEDIKAMENT", None,  "P1", "VF/VT 300mg i.v. Bolus, dann 150mg"),
        ("NORAD",      "Noradrenalin / Norepinephrin",                       "MEDIKAMENT", None,  "P1", "Vasopressor, Sepsis-Schock"),
        ("CPAP",       "Continous Positive Airway Pressure",                 "MEDIKAMENT", None,  "P1", "Akutes Lungenödem, COPD-Exazerbation"),
        ("NITRO",      "Nitroglycerin / Glyceroltrinitrat",                  "MEDIKAMENT", None,  "P1", "Lungenödem, ACS – cave: RR-Abfall"),
        ("HEPARIN",    "Heparin",                                            "MEDIKAMENT", None,  "P2", "PE, ACS – unfraktioniertes oder NMH"),
        ("ASS",        "Acetylsalicylsäure / Aspirin",                       "MEDIKAMENT", None,  "P2", "ACS: 300mg p.o. kauen"),
        ("ATROPIN",    "Atropin",                                            "MEDIKAMENT", None,  "P1", "Bradykardie 0.5mg i.v., Vergiftung"),
        ("DIAZEPAM",   "Diazepam / Benzodiazepin",                           "MEDIKAMENT", None,  "P2", "Krampfanfall, Anxiolyse"),
        ("MORPH",      "Morphin / Opioid-Analgesie",                         "MEDIKAMENT", None,  "P2", "Starke Schmerzen, Lungenödem"),

        # LABOR / DIAGNOSTIK
        ("TMP",        "Troponin",                                           "LABOR",   "R94.3",  "P1", "Hochsensitiv, ACS-Marker"),
        ("LAKTAT",     "Laktat / Blutlaktat",                                "LABOR",   "R79.8",  "P1", ">2mmol/L = Hypoperfusion, Sepsis"),
        ("BGA",        "Blutgasanalyse",                                     "LABOR",   "R79.8",  "P1", "pH, pO2, pCO2, Bikarbonat"),
        ("DDIM",       "D-Dimere",                                           "LABOR",   "R79.8",  "P2", "PE/TVT-Ausschluss, erhöht bei Infektion"),
        ("CREAT",      "Kreatinin / Nierenwert",                             "LABOR",   "R79.8",  "P3", "Nierenfunktion, GFR"),
        ("CRP",        "C-Reaktives Protein",                                "LABOR",   "R79.8",  "P3", "Entzündungsmarker, Infekt"),
        ("PCT",        "Procalcitonin",                                      "LABOR",   "R79.8",  "P2", "Bakterielle Infekt-Marker, Sepsis"),
        ("CO-HB",      "Carboxyhämoglobin",                                  "LABOR",   "R79.8",  "P1", "Rauchgasinhalation, CO-Vergiftung"),

        # ePA / DOKUMENTATION / STANDARDS
        ("ePA",        "Elektronische Patientenakte",                        "EPA",     None,     "P4", "Gematik, §341 SGB V, FHIR R4"),
        ("FHIR",       "Fast Healthcare Interoperability Resources",         "EPA",     None,     "P4", "HL7 FHIR R4, REST-API, JSON"),
        ("ICD10",      "Internationale Klassifikation der Krankheiten",      "EPA",     None,     "P4", "Diagnoseschlüssel, Version 10"),
        ("LOINC",      "Logical Observation Identifiers Names and Codes",    "EPA",     None,     "P4", "Labor-Identifikationsstandard"),
        ("OPS",        "Operationen- und Prozedurenschlüssel",               "EPA",     None,     "P4", "Prozedurencodierung DRG"),
        ("KIM",        "Kommunikation im Medizinwesen",                      "EPA",     None,     "P4", "TI-konforme Nachrichtenübertragung"),
        ("TI",         "Telematik-Infrastruktur",                            "EPA",     None,     "P4", "Gematik-Infrastruktur"),
        ("MIO",        "Medizinische Informationsobjekte",                   "EPA",     None,     "P4", "FHIR-Ressourcen in der ePA"),
        ("KAS",        "Krankenhaus-Aufnahme-System",                        "ADMIN",   None,     "P4", "SAP IS-H, Orbis, etc."),

        # SCORES / SCREENING
        ("QSOFA",      "quick Sequential Organ Failure Assessment",          "DIAGNOSE","R65.2",  "P1", "Sepsis-Screening: RR≤100, AF≥22, GCS<15"),
        ("GCS",        "Glasgow Coma Scale",                                 "DIAGNOSE","R41.3",  "P1", "15 = wach, <8 = Intubation erwägen"),
        ("FAST",       "FAST-Test für Schlaganfall",                         "DIAGNOSE","I63.9",  "P1", "Face-Arm-Speech-Time"),
        ("NEWS2",      "National Early Warning Score 2",                     "DIAGNOSE","R00-R99", "P2", "Frühwarnsystem Verschlechterung"),
        ("CURB65",     "CURB-65 Pneumonie-Schweregrad",                      "DIAGNOSE","J18.9",  "P2", "Confusion, Urea, RR, BPM, >65"),

        # TRANSPORT / LOGISTIK
        ("NAW",        "Notarztwagen",                                       "ADMIN",   None,     "P1", "Mit NEF/Notarzt"),
        ("RTW",        "Rettungswagen",                                      "ADMIN",   None,     "P2", "Ohne Notarzt"),
        ("ITW",        "Intensivtransportwagen",                             "ADMIN",   None,     "P1", "Für ICU-Patienten"),
        ("HELI",       "Rettungshubschrauber / Helikopter",                  "ADMIN",   None,     "P1", "Christoph, DRF"),
    ]

    def __init__(
        self,
        db_path: str | Path = "~/comptext-termux/data/medcodex.db",
    ) -> None:
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.executescript(self.SCHEMA)
            cur = conn.execute("SELECT COUNT(*) FROM codex")
            if cur.fetchone()[0] == 0:
                self._seed_defaults(conn)
            conn.commit()

    def _seed_defaults(self, conn: sqlite3.Connection) -> None:
        conn.executemany(
            """INSERT OR IGNORE INTO codex
                (shorthand, expansion, category, icd10, priority_hint, context)
               VALUES (?,?,?,?,?,?)""",
            self.DEFAULT_CODEX,
        )

    # --- CRUD ---

    def add(self, entry: CodexEntry) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO codex
                    (shorthand, expansion, category, icd10, priority_hint, context)
                   VALUES (?,?,?,?,?,?)""",
                (entry.shorthand, entry.expansion, entry.category,
                 entry.icd10, entry.priority_hint, entry.context),
            )
            conn.commit()

    def get(self, shorthand: str) -> CodexEntry | None:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT shorthand, expansion, category, icd10, priority_hint, context "
                "FROM codex WHERE shorthand = ?",
                (shorthand,),
            ).fetchone()
            return CodexEntry(*row) if row else None

    def search(self, query: str, limit: int = 20) -> list[CodexEntry]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                """SELECT shorthand, expansion, category, icd10, priority_hint, context
                   FROM codex
                   WHERE shorthand LIKE ? OR expansion LIKE ? OR icd10 LIKE ?
                   ORDER BY usage_count DESC
                   LIMIT ?""",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
            return [CodexEntry(*r) for r in rows]

    def list_by_category(self, category: str) -> list[CodexEntry]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, expansion, category, icd10, priority_hint, context "
                "FROM codex WHERE category = ? ORDER BY shorthand",
                (category,),
            ).fetchall()
            return [CodexEntry(*r) for r in rows]

    def count(self) -> int:
        with sqlite3.connect(str(self.db_path)) as conn:
            return conn.execute("SELECT COUNT(*) FROM codex").fetchone()[0]

    def increment_usage(self, shorthand: str) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "UPDATE codex SET usage_count = usage_count + 1 WHERE shorthand = ?",
                (shorthand,),
            )
            conn.commit()

    # --- Kern-Funktionen: Kompression / Expansion ---

    def expand_prompt(self, compressed: str) -> str:
        """
        Kürzel → Volltext für LLM-Eingabe.
        Längste Matches zuerst (z.B. MAB+HS vor MAB).

        Beispiel:
            "MAB+HS, RR↓, HF↑ → ACS?"
            → "Massive arterielle Blutung mit hämorrhagischem Schock,
               Hypotonie, Tachykardie → Akutes Koronarsyndrom?"
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, expansion FROM codex ORDER BY LENGTH(shorthand) DESC"
            ).fetchall()

        result = compressed
        for shorthand, expansion in rows:
            # Kürzel erkennen, auch in Kombinationen wie MAB+HS
            pattern = r"(?<![A-ZÄÖÜ0-9\+\-])" + re.escape(shorthand) + r"(?![A-ZÄÖÜ0-9\+\-])"
            if re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, expansion, result, flags=re.IGNORECASE)
                self.increment_usage(shorthand)
        return result

    def compress_prompt(self, long_text: str) -> str:
        """
        Volltext → Kürzel (für Dokumentation/Export).
        Längste Expansionen zuerst.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, expansion FROM codex ORDER BY LENGTH(expansion) DESC"
            ).fetchall()

        result = long_text
        for shorthand, expansion in rows:
            if expansion.lower() in result.lower():
                result = re.sub(
                    re.escape(expansion), shorthand, result, flags=re.IGNORECASE
                )
        return result

    def build_system_context(self, categories: list[str] | None = None) -> str:
        """
        Erzeugt einen kompakten System-Prompt-Prefix mit dem Codex-Wissen.
        Kann dem LLM als System-Prompt übergeben werden, damit er Kürzel kennt.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            if categories:
                placeholders = ",".join("?" * len(categories))
                rows = conn.execute(
                    f"SELECT shorthand, expansion, priority_hint FROM codex "
                    f"WHERE category IN ({placeholders}) ORDER BY priority_hint, shorthand",
                    categories,
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT shorthand, expansion, priority_hint FROM codex "
                    "WHERE category IN ('NOTFALL', 'DIAGNOSE', 'SYMPTOM') "
                    "ORDER BY priority_hint, shorthand"
                ).fetchall()

        lines = ["MEDIZINISCHER KURZFORM-CODEX (verwende diese Kürzel beim Dokumentieren):"]
        for shorthand, expansion, prio in rows:
            lines.append(f"  {shorthand}: {expansion} [{prio}]")
        lines.append("")
        return "\n".join(lines)

    def top_used(self, limit: int = 10) -> list[tuple[str, int]]:
        """Die am häufigsten verwendeten Kürzel."""
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT shorthand, usage_count FROM codex "
                "ORDER BY usage_count DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [(r[0], r[1]) for r in rows]
