QUALITY_RULES = {
    "duplicate_threshold": 1,
    "missing_threshold_percent": 20,
    "high_risk_score": 70,
    "warning_score": 85,
    "invalid_email_pattern": "simple_email",
    "invalid_phone_pattern": "south_africa_mobile",
}


def get_quality_rules() -> dict:
    return QUALITY_RULES.copy()
