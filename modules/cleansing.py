from typing import Dict, List

import pandas as pd


def build_cleansing_plan(df: pd.DataFrame, missingness: Dict[str, Dict[str, float]], duplicates: pd.DataFrame) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []

    for field, info in missingness.items():
        if info.get("missing_count", 0) > 0:
            actions.append(
                {
                    "issue": f"Missing values in {field}",
                    "severity": "High" if info.get("missing_pct", 0) > 25 else "Medium",
                    "recommendation": f"Request the data owner to complete values for the '{field}' field before analysis.",
                }
            )

    if not duplicates.empty:
        actions.append(
            {
                "issue": "Duplicate learner records",
                "severity": "High",
                "recommendation": "Review duplicate identifiers and retain only the authoritative record for each learner.",
            }
        )

    if not actions:
        actions.append(
            {
                "issue": "No material data quality issues identified",
                "severity": "Low",
                "recommendation": "Maintain the validated dataset and re-run checks when new records are added.",
            }
        )

    return actions
