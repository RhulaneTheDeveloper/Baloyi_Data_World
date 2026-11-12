import re
from typing import Dict, List

import pandas as pd

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^(?:\+27|27|0)[6-8][0-9]{8}$")


def flag_invalid_emails(df: pd.DataFrame, email_field: str) -> int:
    if not email_field or email_field not in df.columns:
        return 0
    values = df[email_field].fillna("").astype(str)
    invalid = values[values.str.strip() != ""].map(lambda x: not bool(EMAIL_REGEX.match(x.strip())))
    return int(invalid.sum())


def flag_invalid_phones(df: pd.DataFrame, phone_field: str) -> int:
    if not phone_field or phone_field not in df.columns:
        return 0
    values = df[phone_field].fillna("").astype(str)
    invalid = values[values.str.strip() != ""].map(lambda x: not bool(PHONE_REGEX.match(x.strip())))
    return int(invalid.sum())


def flag_invalid_dates(df: pd.DataFrame, date_field: str) -> int:
    if not date_field or date_field not in df.columns:
        return 0
    parsed = pd.to_datetime(df[date_field], errors="coerce")
    invalid = parsed.isna() & df[date_field].fillna("").astype(str).str.strip().ne("")
    return int(invalid.sum())


def evaluate_consistency(df: pd.DataFrame, date_fields: List[str] | None = None) -> Dict[str, int]:
    results = {
        "invalid_emails": 0,
        "invalid_phones": 0,
        "invalid_dates": 0,
    }

    for column in df.columns:
        name = column.lower()
        if "email" in name:
            results["invalid_emails"] = flag_invalid_emails(df, column)
        if "phone" in name or "mobile" in name:
            results["invalid_phones"] = flag_invalid_phones(df, column)

    if date_fields:
        for field in date_fields:
            if field in df.columns:
                results["invalid_dates"] += flag_invalid_dates(df, field)

    return results
