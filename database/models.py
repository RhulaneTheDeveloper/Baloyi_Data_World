from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisSession:
    filename: str
    sheet_names: str
    row_count: int
    column_count: int
    overall_score: float


@dataclass
class RemediationAction:
    issue: str
    severity: str
    record_count: int
    recommendation: str
    status: str = "Open"


@dataclass
class ReadinessCheck:
    check_name: str
    passed: bool
    notes: Optional[str] = None
