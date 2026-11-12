from typing import List

import pandas as pd


def find_duplicate_rows(df: pd.DataFrame, key_field: str) -> pd.DataFrame:
    if not key_field or key_field not in df.columns:
        return pd.DataFrame(columns=df.columns)
    return df[df[key_field].duplicated(keep=False)].copy().sort_values(by=key_field).reset_index(drop=True)


def find_duplicate_count(df: pd.DataFrame, key_field: str) -> int:
    duplicates = find_duplicate_rows(df, key_field)
    return int(len(duplicates))


def identify_duplicate_ids(df: pd.DataFrame, key_field: str) -> List[str]:
    if not key_field or key_field not in df.columns:
        return []
    duplicates = df[df[key_field].duplicated(keep=False)][key_field].dropna().unique().tolist()
    return [str(item) for item in duplicates]
