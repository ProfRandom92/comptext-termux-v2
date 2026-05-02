#!/usr/bin/env python3
"""
MedDB – Async SQLite Datenbank-Layer für Triage-Daten
Termux-kompatibel, zero-config, kein Server nötig.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import aiosqlite


class TriageLevel(str, Enum):
    P1 = "P1_CRITICAL"
    P2 = "P2_URGENT"
    P3 = "P3_ACUTE"
    P4 = "P4_NORMAL"
    P5 = "P5_NONURGENT"
    UNK = "UNKNOWN"


@dataclass(slots=True)
class Patient:
    id: Optional[int] = None
    case_number: str = ""
    age: Optional[int] = None
    gender: Optional[str] = None  # M/F/D
    chief_complaint: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(slots=True)
class TriageRecord:
    id: Optional[int] = None
    patient_id: int = 0
    input_text: str = ""
    raw_llm_response: str = ""
    assigned_priority: str = TriageLevel.UNK
    confidence: float = 0.0
    latency_ms: int = 0
    model_name: str = "unknown"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MedDB:
    """
    Async SQLite Manager für Triage-Daten.
    Erstellt automatisch Tabellen beim ersten Start.
    """

    def __init__(
        self,
        db_path: str | Path = "~/comptext-termux/data/medtriage.db",
    ) -> None:
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def _connect(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(str(self.db_path))
        conn.row_factory = aiosqlite.Row
        return conn

    async def init_schema(self) -> None:
        """Erstellt alle Tabellen. Idempotent."""
        async with self._lock:
            async with await self._connect() as conn:
                await conn.executescript("""
                    PRAGMA journal_mode=WAL;

                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_number TEXT UNIQUE NOT NULL,
                        age INTEGER,
                        gender TEXT,
                        chief_complaint TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS triage_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER NOT NULL,
                        input_text TEXT NOT NULL,
                        raw_llm_response TEXT,
                        assigned_priority TEXT,
                        confidence REAL DEFAULT 0.0,
                        latency_ms INTEGER DEFAULT 0,
                        model_name TEXT DEFAULT 'unknown',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (patient_id) REFERENCES patients(id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_triage_time
                        ON triage_records(created_at);
                    CREATE INDEX IF NOT EXISTS idx_triage_prio
                        ON triage_records(assigned_priority);

                    CREATE TABLE IF NOT EXISTS memory_palace (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        palace TEXT NOT NULL,
                        wing TEXT NOT NULL,
                        room TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(palace, wing, room)
                    );

                    CREATE INDEX IF NOT EXISTS idx_palace
                        ON memory_palace(palace, wing);
                """)
                await conn.commit()

    # --- Patient CRUD ---

    async def create_patient(self, p: Patient) -> int:
        async with self._lock:
            async with await self._connect() as conn:
                cursor = await conn.execute(
                    """INSERT INTO patients (case_number, age, gender, chief_complaint)
                       VALUES (?, ?, ?, ?)""",
                    (p.case_number, p.age, p.gender, p.chief_complaint),
                )
                await conn.commit()
                return cursor.lastrowid  # type: ignore

    async def get_patient(self, patient_id: int) -> Patient | None:
        async with await self._connect() as conn:
            rows = await conn.execute_fetchall(
                "SELECT * FROM patients WHERE id = ?", (patient_id,)
            )
            if not rows:
                return None
            return Patient(**dict(rows[0]))

    # --- Triage CRUD ---

    async def save_triage(self, rec: TriageRecord) -> int:
        async with self._lock:
            async with await self._connect() as conn:
                cursor = await conn.execute(
                    """INSERT INTO triage_records
                        (patient_id, input_text, raw_llm_response, assigned_priority,
                        confidence, latency_ms, model_name)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        rec.patient_id, rec.input_text, rec.raw_llm_response,
                        rec.assigned_priority, rec.confidence, rec.latency_ms,
                        rec.model_name,
                    ),
                )
                await conn.commit()
                return cursor.lastrowid  # type: ignore

    async def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        async with await self._connect() as conn:
            rows = await conn.execute_fetchall(
                """SELECT
                    t.id, p.case_number, p.age, p.gender,
                    t.input_text, t.assigned_priority, t.confidence,
                    t.latency_ms, t.created_at
                   FROM triage_records t
                   JOIN patients p ON t.patient_id = p.id
                   ORDER BY t.created_at DESC
                   LIMIT ?""",
                (limit,),
            )
            return [dict(r) for r in rows]

    async def get_stats(self) -> dict[str, Any]:
        async with await self._connect() as conn:
            total = await conn.execute_fetchall(
                "SELECT COUNT(*) as c FROM triage_records"
            )
            p1_count = await conn.execute_fetchall(
                "SELECT COUNT(*) as c FROM triage_records WHERE assigned_priority = 'P1_CRITICAL'"
            )
            avg_latency = await conn.execute_fetchall(
                "SELECT AVG(latency_ms) as avg FROM triage_records"
            )
            today = await conn.execute_fetchall(
                """SELECT COUNT(*) as c FROM triage_records
                    WHERE date(created_at) = date('now')"""
            )
            return {
                "total_cases": total[0]["c"] if total else 0,
                "p1_cases": p1_count[0]["c"] if p1_count else 0,
                "avg_latency_ms": round(
                    avg_latency[0]["avg"], 1
                ) if avg_latency and avg_latency[0]["avg"] else 0,
                "today_cases": today[0]["c"] if today else 0,
            }

    # --- Memory Palace ---

    async def palace_remember(
        self, palace: str, wing: str, room: str, content: str
    ) -> None:
        """Speichert hierarchisch: [[Palace:Wing:Room]]"""
        async with self._lock:
            async with await self._connect() as conn:
                await conn.execute(
                    """INSERT OR REPLACE INTO memory_palace
                        (palace, wing, room, content)
                       VALUES (?, ?, ?, ?)""",
                    (palace, wing, room, content),
                )
                await conn.commit()

    async def palace_recall(
        self, palace: str, wing: str = "%", room: str = "%"
    ) -> list[dict[str, Any]]:
        """Ruft ab mit Wildcards."""
        async with await self._connect() as conn:
            rows = await conn.execute_fetchall(
                """SELECT palace, wing, room, content, created_at
                   FROM memory_palace
                   WHERE palace = ? AND wing LIKE ? AND room LIKE ?
                   ORDER BY created_at DESC""",
                (palace, wing, room),
            )
            return [dict(r) for r in rows]

    # --- Export ---

    async def export_json(self, path: str | Path) -> None:
        history = await self.get_history(limit=10000)
        out = Path(path).expanduser()
        out.write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )
