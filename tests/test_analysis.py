"""
tests/test_analysis.py
Automated tests for Baloyi Data World – Milestone 1.
Run with: .venv\\Scripts\\python -m pytest tests/ -v
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.excel_import import (
    load_workbook,
    match_column,
    normalize_column_name,
)
from modules.completeness import calculate_missingness, calculate_completeness_score
from modules.duplicate_detection import (
    find_duplicate_rows,
    find_duplicate_count,
    identify_duplicate_ids,
)
from modules.consistency import (
    flag_invalid_emails,
    flag_invalid_phones,
    flag_invalid_dates,
    evaluate_consistency,
)
from modules.cleansing import build_cleansing_plan
from modules.readiness import assess_readiness
from database.db import init_db, get_connection


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "learner_id":  ["L001", "L002", "L003", "L001", ""],
        "first_name":  ["Alice", "Bob", "Carol", "Alice", "Dave"],
        "surname":     ["Smith", "Jones", "", "Smith", "Brown"],
        "email":       ["alice@test.com", "bad-email", "carol@test.com", "alice@test.com", ""],
        "department":  ["IT", "HR", "IT", "IT", "Finance"],
        "status":      ["Active", "ACTIVE", "active", "Active", "Inactive"],
        "start_date":  ["2024-01-15", "not-a-date", "2024-03-01", "2024-01-15", ""],
    })


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame({
        "learner_id": ["L001", "L002", "L003"],
        "first_name": ["Alice", "Bob", "Carol"],
        "email":      ["alice@test.com", "bob@test.com", "carol@test.com"],
        "status":     ["Active", "Active", "Inactive"],
    })


@pytest.fixture
def empty_df() -> pd.DataFrame:
    return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# Column normalisation tests
# ─────────────────────────────────────────────────────────────

class TestNormaliseColumnName:
    def test_basic_normalisation(self):
        assert normalize_column_name("Learner ID") == "learner_id"

    def test_email_address(self):
        assert normalize_column_name("Email Address") == "email_address"

    def test_mixed_case(self):
        assert normalize_column_name("FIRST_NAME") == "first_name"

    def test_special_characters(self):
        assert normalize_column_name("Date-of-Birth") == "date_of_birth"

    def test_none_input(self):
        assert normalize_column_name(None) == ""

    def test_empty_string(self):
        assert normalize_column_name("") == ""

    def test_leading_trailing_spaces(self):
        assert normalize_column_name("  Department  ") == "department"


class TestMatchColumn:
    def test_exact_match(self):
        cols = ["Learner ID", "First Name", "Email"]
        result = match_column(cols, ["learner_id"])
        assert result == "Learner ID"

    def test_no_match(self):
        cols = ["Name", "Department"]
        result = match_column(cols, ["phone", "mobile"])
        assert result == ""

    def test_partial_match(self):
        cols = ["Student Email Address"]
        result = match_column(cols, ["email_address"])
        assert result == "Student Email Address"


# ─────────────────────────────────────────────────────────────
# Excel import tests
# ─────────────────────────────────────────────────────────────

class TestLoadWorkbook:
    def test_load_from_dict(self, clean_df):
        result = load_workbook({"Sheet1": clean_df})
        assert result["sheet_count"] == 1
        assert result["row_count"] == 3
        assert result["column_count"] == 4

    def test_multiple_sheets(self, clean_df, sample_df):
        result = load_workbook({"Sheet1": clean_df, "Sheet2": sample_df})
        assert result["sheet_count"] == 2
        assert result["row_count"] == len(clean_df) + len(sample_df)

    def test_empty_sheet(self, empty_df):
        result = load_workbook({"Empty": empty_df})
        assert result["row_count"] == 0

    def test_records_per_sheet(self, clean_df, sample_df):
        result = load_workbook({"A": clean_df, "B": sample_df})
        assert result["records_per_sheet"]["A"] == len(clean_df)
        assert result["records_per_sheet"]["B"] == len(sample_df)

    def test_column_names_stripped(self):
        df = pd.DataFrame({"  Learner ID  ": ["L001"], " Email ": ["a@b.com"]})
        result = load_workbook({"S": df})
        cols = result["column_names"]
        assert "Learner ID" in cols
        assert "Email" in cols

    def test_identifier_field_detected(self, clean_df):
        result = load_workbook({"S": clean_df})
        assert result["identifier_field"] == "learner_id"

    def test_email_field_detected(self, clean_df):
        result = load_workbook({"S": clean_df})
        assert result["email_field"] == "email"


# ─────────────────────────────────────────────────────────────
# Completeness tests
# ─────────────────────────────────────────────────────────────

class TestCalculateMissingness:
    def test_missing_null(self, sample_df):
        result = calculate_missingness(sample_df, ["email"])
        assert result["email"]["missing_count"] == 1

    def test_field_not_present(self, sample_df):
        result = calculate_missingness(sample_df, ["phone"])
        assert result["phone"]["found"] is False
        assert result["phone"]["missing_count"] == len(sample_df)

    def test_all_present(self, clean_df):
        result = calculate_missingness(clean_df, ["learner_id"])
        assert result["learner_id"]["missing_count"] == 0
        assert result["learner_id"]["missing_pct"] == 0.0

    def test_completeness_pct_calculation(self, sample_df):
        result = calculate_missingness(sample_df, ["learner_id"])
        # sample_df has 1 empty learner_id -> 1/5 = 20%
        assert result["learner_id"]["missing_pct"] == 20.0

    def test_empty_dataframe(self, empty_df):
        result = calculate_missingness(empty_df, ["learner_id"])
        # Empty df: field not found
        assert result["learner_id"]["found"] is False


class TestCompletenessScore:
    def test_perfect_score(self, clean_df):
        score = calculate_completeness_score(clean_df, ["learner_id", "email"])
        assert score == 100.0

    def test_partial_score(self, sample_df):
        score = calculate_completeness_score(sample_df, ["learner_id", "email", "surname"])
        assert 0 < score < 100

    def test_empty_df_returns_100(self, empty_df):
        score = calculate_completeness_score(empty_df, ["learner_id"])
        assert score == 100.0

    def test_no_mandatory_fields(self, clean_df):
        score = calculate_completeness_score(clean_df, [])
        assert score == 100.0


# ─────────────────────────────────────────────────────────────
# Duplicate detection tests
# ─────────────────────────────────────────────────────────────

class TestDuplicateDetection:
    def test_finds_duplicate_rows(self, sample_df):
        dups = find_duplicate_rows(sample_df, "learner_id")
        # L001 appears twice
        assert len(dups) == 2

    def test_no_duplicates(self, clean_df):
        dups = find_duplicate_rows(clean_df, "learner_id")
        assert len(dups) == 0

    def test_missing_key_field(self, sample_df):
        dups = find_duplicate_rows(sample_df, "nonexistent_column")
        assert len(dups) == 0

    def test_duplicate_count(self, sample_df):
        count = find_duplicate_count(sample_df, "learner_id")
        assert count == 2

    def test_identify_duplicate_ids(self, sample_df):
        ids = identify_duplicate_ids(sample_df, "learner_id")
        assert "L001" in ids

    def test_exact_duplicates(self):
        df = pd.DataFrame({
            "id": ["A", "A", "B"],
            "name": ["X", "X", "Y"],
        })
        dups = find_duplicate_rows(df, "id")
        assert len(dups) == 2


# ─────────────────────────────────────────────────────────────
# Consistency / validation tests
# ─────────────────────────────────────────────────────────────

class TestEmailValidation:
    def test_valid_email(self):
        df = pd.DataFrame({"email": ["valid@test.com", "another@domain.co.za"]})
        assert flag_invalid_emails(df, "email") == 0

    def test_invalid_email(self):
        df = pd.DataFrame({"email": ["valid@test.com", "not-an-email", "also bad"]})
        assert flag_invalid_emails(df, "email") == 2

    def test_empty_email_ignored(self):
        df = pd.DataFrame({"email": ["valid@test.com", "", None]})
        assert flag_invalid_emails(df, "email") == 0

    def test_missing_field(self):
        df = pd.DataFrame({"name": ["Alice"]})
        assert flag_invalid_emails(df, "email") == 0

    def test_mixed_case_email(self):
        df = pd.DataFrame({"email": ["Valid@TEST.COM"]})
        assert flag_invalid_emails(df, "email") == 0


class TestPhoneValidation:
    def test_valid_sa_phone(self):
        df = pd.DataFrame({"phone": ["0821234567", "+27821234567"]})
        assert flag_invalid_phones(df, "phone") == 0

    def test_invalid_phone(self):
        df = pd.DataFrame({"phone": ["12345", "not-a-phone"]})
        assert flag_invalid_phones(df, "phone") == 2

    def test_empty_phone_ignored(self):
        df = pd.DataFrame({"phone": ["0821234567", ""]})
        assert flag_invalid_phones(df, "phone") == 0


class TestDateValidation:
    def test_valid_dates(self):
        df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-06-15"])})
        assert flag_invalid_dates(df, "date") == 0

    def test_invalid_string_dates(self):
        df = pd.DataFrame({"date": ["not-a-date", "also-bad"]})
        assert flag_invalid_dates(df, "date") == 2

    def test_mixed_dates(self):
        df = pd.DataFrame({"date": ["2024-01-01", "not-a-date", ""]})
        assert flag_invalid_dates(df, "date") == 1


class TestEvaluateConsistency:
    def test_returns_dict(self, sample_df):
        result = evaluate_consistency(sample_df)
        assert "invalid_emails" in result
        assert "invalid_phones" in result
        assert "invalid_dates"  in result

    def test_counts_invalid_emails(self, sample_df):
        result = evaluate_consistency(sample_df)
        assert result["invalid_emails"] >= 1  # "bad-email" is invalid


# ─────────────────────────────────────────────────────────────
# Cleansing plan tests
# ─────────────────────────────────────────────────────────────

class TestBuildCleansingPlan:
    def test_missing_fields_flagged(self, sample_df):
        from modules.completeness import calculate_missingness
        from modules.duplicate_detection import find_duplicate_rows
        missingness = calculate_missingness(sample_df, ["email", "surname"])
        dups = find_duplicate_rows(sample_df, "learner_id")
        plan = build_cleansing_plan(sample_df, missingness, dups)
        assert len(plan) > 0
        issues = [a["issue"] for a in plan]
        assert any("Missing" in i or "Duplicate" in i for i in issues)

    def test_no_issues_returns_low_plan(self, clean_df):
        from modules.completeness import calculate_missingness
        from modules.duplicate_detection import find_duplicate_rows
        missingness = calculate_missingness(clean_df, ["learner_id", "email"])
        dups = find_duplicate_rows(clean_df, "learner_id")
        plan = build_cleansing_plan(clean_df, missingness, dups)
        assert len(plan) >= 1  # at least the "no material issues" entry


# ─────────────────────────────────────────────────────────────
# Readiness assessment tests
# ─────────────────────────────────────────────────────────────

class TestReadinessAssessment:
    def test_high_score_ready(self):
        result = assess_readiness({
            "quality_score": 90, "row_count": 100,
            "mandatory_fields_found": 5, "duplicate_count": 0, "issue_count": 0
        })
        assert result["status"] == "Ready for operational use"

    def test_medium_score_needs_remediation(self):
        result = assess_readiness({
            "quality_score": 75, "row_count": 100,
            "mandatory_fields_found": 3, "duplicate_count": 2, "issue_count": 5
        })
        assert "remediation" in result["status"].lower()

    def test_low_score_not_ready(self):
        result = assess_readiness({
            "quality_score": 45, "row_count": 50,
            "mandatory_fields_found": 1, "duplicate_count": 10, "issue_count": 30
        })
        assert "Not ready" in result["status"]

    def test_checks_returned(self):
        result = assess_readiness({
            "quality_score": 80, "row_count": 100,
            "mandatory_fields_found": 5, "duplicate_count": 0, "issue_count": 2
        })
        assert isinstance(result["checks"], list)
        assert len(result["checks"]) > 0


# ─────────────────────────────────────────────────────────────
# Database tests
# ─────────────────────────────────────────────────────────────

class TestDatabase:
    def test_init_db_creates_tables(self, tmp_path, monkeypatch):
        """init_db should create tables without raising."""
        import database.db as db_module
        test_db = tmp_path / "test.db"
        monkeypatch.setattr(db_module, "DB_PATH", test_db)
        db_module.init_db()
        conn = db_module.get_connection()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        conn.close()
        assert "analysis_sessions" in table_names
        assert "quality_issues" in table_names
        assert "remediation_actions" in table_names

    def test_store_and_fetch_remediation(self, tmp_path, monkeypatch):
        import database.db as db_module
        test_db = tmp_path / "test.db"
        monkeypatch.setattr(db_module, "DB_PATH", test_db)
        db_module.init_db()
        db_module.store_remediation_issue(
            "Missing learner ID", "High", 5, "Request data owner to provide IDs"
        )
        issues = db_module.fetch_remediation_issues()
        assert len(issues) == 1
        assert issues[0]["issue"] == "Missing learner ID"
        assert issues[0]["severity"] == "High"
