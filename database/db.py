"""
database/db.py
SQLite database initialisation and connection management.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent / "hosi_analysis.db"


def get_connection() -> sqlite3.Connection:
    """Return a database connection with row_factory set."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all required tables if they do not already exist."""
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at      TEXT NOT NULL,
            filename        TEXT,
            sheet_names     TEXT,
            row_count       INTEGER,
            column_count    INTEGER,
            overall_score   REAL,
            completeness    REAL,
            duplicate_count INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS field_profiles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES analysis_sessions(id),
            created_at      TEXT NOT NULL,
            field_name      TEXT NOT NULL,
            std_field_name  TEXT,
            data_type       TEXT,
            populated       INTEGER,
            missing         INTEGER,
            unique_values   INTEGER,
            completeness_pct REAL,
            is_mandatory    INTEGER DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS quality_issues (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES analysis_sessions(id),
            created_at      TEXT NOT NULL,
            issue           TEXT NOT NULL,
            severity        TEXT,
            field_name      TEXT,
            original_value  TEXT,
            status          TEXT DEFAULT 'Open',
            assigned_to     TEXT,
            notes           TEXT,
            updated_at      TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS remediation_actions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES analysis_sessions(id),
            created_at      TEXT NOT NULL,
            issue           TEXT NOT NULL,
            severity        TEXT,
            record_count    INTEGER,
            recommendation  TEXT,
            proposed_correction TEXT,
            approved_correction TEXT,
            status          TEXT DEFAULT 'Open',
            assigned_to     TEXT,
            resolution_notes TEXT,
            verification_date TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS business_clarifications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at      TEXT NOT NULL,
            question        TEXT NOT NULL,
            affected_field  TEXT,
            affected_record TEXT,
            responsible_dept TEXT,
            assigned_to     TEXT,
            date_raised     TEXT,
            response        TEXT,
            business_decision TEXT,
            approval_status TEXT DEFAULT 'Pending',
            updated_at      TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS readiness_checks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES analysis_sessions(id),
            created_at      TEXT NOT NULL,
            check_name      TEXT NOT NULL,
            passed          INTEGER,
            evidence        TEXT,
            responsible_person TEXT,
            notes           TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS report_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES analysis_sessions(id),
            created_at      TEXT NOT NULL,
            report_type     TEXT NOT NULL,
            filename        TEXT,
            generated_by    TEXT
        )
        """,
    ]

    try:
        with get_connection() as conn:
            for stmt in ddl_statements:
                conn.execute(stmt)
            conn.commit()
        logger.info("Database initialised at %s", DB_PATH)
    except Exception as exc:
        logger.error("Database initialisation failed: %s", exc)
        raise


def save_analysis_session(filename: str, sheet_names: list[str], row_count: int,
                           column_count: int, overall_score: float,
                           completeness: float, duplicate_count: int) -> int:
    """Insert an analysis session and return its ID."""
    from datetime import datetime
    created_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_sessions
                (created_at, filename, sheet_names, row_count, column_count,
                 overall_score, completeness, duplicate_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, filename, ",".join(sheet_names), row_count, column_count,
             overall_score, completeness, duplicate_count),
        )
        conn.commit()
        return int(cursor.lastrowid)


def fetch_analysis_sessions() -> list[dict]:
    """Return all analysis sessions ordered by most recent."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analysis_sessions ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def store_remediation_issue(issue: str, severity: str, record_count: int,
                             recommendation: str, status: str = "Open",
                             session_id: int | None = None) -> None:
    """Store a remediation action."""
    from datetime import datetime
    created_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO remediation_actions
                (session_id, created_at, issue, severity, record_count, recommendation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, created_at, issue, severity, record_count, recommendation, status),
        )
        conn.commit()


def fetch_remediation_issues(session_id: int | None = None) -> list[dict]:
    """Fetch remediation actions, optionally filtered by session."""
    with get_connection() as conn:
        if session_id:
            rows = conn.execute(
                "SELECT * FROM remediation_actions WHERE session_id=? ORDER BY created_at DESC",
                (session_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM remediation_actions ORDER BY created_at DESC"
            ).fetchall()
    return [dict(row) for row in rows]
