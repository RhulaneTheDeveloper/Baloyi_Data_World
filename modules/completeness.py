"""
modules/completeness.py
Mandatory field completeness calculations.
Treats NaN, empty strings, and whitespace-only values as missing.
"""
from __future__ import annotations

from typing import Dict, List

import pandas as pd


def _is_empty(series: pd.Series) -> pd.Series:
    """Return boolean mask: True where a value is considered empty/missing."""
    null_mask = series.isna()
    str_mask  = series.astype(str).str.strip().isin(["", "nan", "NaN", "None", "none"])
    return null_mask | str_mask


def calculate_missingness(
    df: pd.DataFrame,
    mandatory_fields: List[str],
) -> Dict[str, Dict]:
    """
    Calculate missingness for each mandatory field.

    Returns a dict keyed by field name:
        {
            "missing_count": int,
            "missing_pct":   float,
            "present_count": int,
            "found":         bool,
            "actual_field":  str   # only when found=True
        }
    """
    results: Dict[str, Dict] = {}
    total_rows = len(df)

    for field in mandatory_fields:
        # Case-insensitive column match
        matches = [col for col in df.columns if col.strip().lower() == field.strip().lower()]
        if not matches:
            results[field] = {
                "missing_count": total_rows,
                "missing_pct":   100.0,
                "present_count": 0,
                "found":         False,
            }
            continue

        actual_field  = matches[0]
        empty_mask    = _is_empty(df[actual_field])
        missing_count = int(empty_mask.sum())
        present_count = total_rows - missing_count
        missing_pct   = round((missing_count / total_rows) * 100, 2) if total_rows else 0.0

        results[field] = {
            "missing_count": missing_count,
            "missing_pct":   missing_pct,
            "present_count": present_count,
            "found":         True,
            "actual_field":  actual_field,
        }

    return results


def calculate_completeness_score(
    df: pd.DataFrame,
    mandatory_fields: List[str],
) -> float:
    """
    Overall completeness as a percentage across all mandatory fields.
    Returns 100.0 for empty DataFrames or empty mandatory_fields lists.
    """
    if df.empty or not mandatory_fields:
        return 100.0

    missingness = calculate_missingness(df, mandatory_fields)
    total_expected = len(df) * len(mandatory_fields)
    total_missing  = sum(info.get("missing_count", 0) for info in missingness.values())
    score = 100.0 - (total_missing / total_expected) * 100.0
    return round(max(0.0, score), 2)
