"""
modules/remediation.py
Remediation issue storage and retrieval via SQLite.
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from database.db import get_connection


def store_remediation_issue(
    issue: str,
    severity: str,
    record_count: int,
    recommendation: str,
    status: str = "Open",
    session_id: int | None = None,
) -> None:
    """Persist a remediation issue to the database."""
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


def fetch_remediation_issues(session_id: int | None = None) -> List[dict]:
    """Return all remediation actions, optionally filtered by session."""
    with get_connection() as conn:
        if session_id:
            rows = conn.execute(
                "SELECT * FROM remediation_actions WHERE session_id=? ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM remediation_actions ORDER BY created_at DESC"
            ).fetchall()
    return [dict(row) for row in rows]


def update_remediation_status(issue_id: int, status: str, notes: str = "", assigned_to: str = "") -> None:
    """Update the status and notes of an existing remediation action."""
    updated_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE remediation_actions
            SET status=?, resolution_notes=?, assigned_to=?, verification_date=?
            WHERE id=?
            """,
            (status, notes, assigned_to, updated_at, issue_id),
        )
        conn.commit()
