import io
from typing import Any, Dict, Iterable, List, Union

import pandas as pd

from config.settings import DEFAULT_MANDATORY_FIELDS


def normalize_column_name(value: Any) -> str:
    text = "" if value is None else str(value).strip().lower()
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in text)
    return cleaned.strip("_")


def match_column(columns: Iterable[str], candidates: List[str]) -> str:
    normalized_columns = {normalize_column_name(col): col for col in columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized_columns:
            return normalized_columns[key]
    for candidate in candidates:
        key = normalize_column_name(candidate)
        for column in columns:
            if key in normalize_column_name(column):
                return column
    return ""


def load_workbook(source: Any) -> Dict[str, Any]:
    if isinstance(source, dict):
        frames = {str(name): pd.DataFrame(frame) for name, frame in source.items()}
        return summarise_workbook(frames)

    cached = source
    if hasattr(source, "getvalue"):
        file_obj = io.BytesIO(source.getvalue())
    else:
        file_obj = io.BytesIO(source.read())

    file_name = getattr(source, "name", "upload.xlsx")
    if file_name.lower().endswith(".csv"):
        data = pd.read_csv(file_obj)
        frames = {"Sheet1": data}
    else:
        xlsx = pd.ExcelFile(file_obj)
        frames = {sheet_name: pd.read_excel(file_obj, sheet_name=sheet_name) for sheet_name in xlsx.sheet_names}

    return summarise_workbook(frames)


def summarise_workbook(frames: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    combined = pd.concat(frames.values(), ignore_index=True, sort=False)
    combined = combined.copy()
    combined.columns = [str(col).strip() for col in combined.columns]
    return {
        "sheet_count": len(frames),
        "sheet_names": list(frames.keys()),
        "row_count": len(combined),
        "column_count": len(combined.columns),
        "column_names": list(combined.columns),
        "records_per_sheet": {name: len(frame) for name, frame in frames.items()},
        "data": combined,
        "identifier_field": match_column(combined.columns, [
            "learner_id",
            "student_id",
            "student_number",
            "candidate_id",
            "id_number",
        ]),
        "email_field": match_column(combined.columns, ["email", "email_address", "learner_email"]),
        "phone_field": match_column(combined.columns, ["phone", "phone_number", "mobile_number", "cell_number"]),
        "mandatory_fields": DEFAULT_MANDATORY_FIELDS,
    }
