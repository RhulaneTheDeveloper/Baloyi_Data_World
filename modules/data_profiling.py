"""
modules/data_profiling.py
DataFrame profiling, field dictionary, and structure analysis.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def _safe_sample(series: pd.Series, n: int = 5) -> List[str]:
    """Return up to n non-null sample values as strings — no PII in logs."""
    return series.dropna().astype(str).head(n).tolist()


def _field_type_label(dtype) -> str:
    if pd.api.types.is_numeric_dtype(dtype):
        return "Numeric"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "Date / Time"
    if pd.api.types.is_bool_dtype(dtype):
        return "Boolean"
    return "Text"


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Return a high-level profile of a DataFrame."""
    if df.empty:
        return {
            "row_count":      0,
            "column_count":   0,
            "empty_rows":     0,
            "empty_columns":  0,
            "exact_duplicates": 0,
            "date_coverage":  {"min": None, "max": None},
            "columns":        [],
            "column_profiles": [],
        }

    empty_rows    = int(df.isna().all(axis=1).sum())
    empty_columns = int(df.isna().all(axis=0).sum())
    exact_dups    = int(df.duplicated().sum())

    column_profiles: List[Dict[str, Any]] = []
    for col in df.columns:
        series = df[col]
        filled = int(series.notna().sum())
        total  = len(df)
        pct    = round((filled / total) * 100, 1) if total else 0.0
        column_profiles.append({
            "name":         col,
            "dtype":        str(series.dtype),
            "type_label":   _field_type_label(series.dtype),
            "non_null":     filled,
            "null_count":   total - filled,
            "unique_count": int(series.nunique(dropna=True)),
            "completeness": pct,
            "sample":       _safe_sample(series),
        })

    # Date coverage from datetime columns
    dt_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns
    date_min = date_max = None
    if len(dt_cols):
        date_min = str(df[dt_cols].min().min())
        date_max = str(df[dt_cols].max().max())

    return {
        "row_count":       int(len(df)),
        "column_count":    int(len(df.columns)),
        "empty_rows":      empty_rows,
        "empty_columns":   empty_columns,
        "exact_duplicates": exact_dups,
        "date_coverage":   {"min": date_min, "max": date_max},
        "columns":         list(df.columns),
        "column_profiles": column_profiles,
    }


def build_field_dictionary(
    df: pd.DataFrame,
    column_mapping: Dict[str, str] | None = None,
    mandatory_fields: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate a full data dictionary entry for every column.

    Args:
        df:               Source DataFrame.
        column_mapping:   {standardised_field: source_column} mapping.
        mandatory_fields: List of standardised field names that are mandatory.

    Returns:
        List of dicts, one per column.
    """
    reverse_map   = {v: k for k, v in (column_mapping or {}).items()}
    mandatory_set = set(mandatory_fields or [])
    total_rows    = len(df)
    rows: List[Dict[str, Any]] = []

    for col in df.columns:
        series    = df[col]
        filled    = int(series.notna().sum())
        missing   = total_rows - filled
        pct       = round((filled / max(total_rows, 1)) * 100, 1)
        std_name  = reverse_map.get(col, "")
        is_mand   = std_name in mandatory_set if std_name else False
        type_lbl  = _field_type_label(series.dtype)
        unique_c  = int(series.nunique(dropna=True))

        if pct >= 95:
            val_status = "Good"
        elif pct >= 70:
            val_status = "Partial"
        else:
            val_status = "Poor"

        rows.append({
            "field_name":        col,
            "std_field_name":    std_name,
            "data_type":         type_lbl,
            "raw_dtype":         str(series.dtype),
            "populated":         filled,
            "missing":           missing,
            "completeness_pct":  pct,
            "unique_values":     unique_c,
            "sample_values":     _safe_sample(series),
            "is_mandatory":      is_mand,
            "classification":    "Mandatory" if is_mand else "Optional",
            "validation_status": val_status,
        })

    return rows
