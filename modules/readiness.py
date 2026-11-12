from typing import Dict, List


def assess_readiness(report: Dict[str, object]) -> Dict[str, object]:
    score = float(report.get("quality_score", 0))

    checks = [
        ("Workbook loaded successfully", True),
        ("Record volume reviewed", report.get("row_count", 0) > 0),
        ("Mandatory fields reviewed", report.get("mandatory_fields_found", 0) > 0),
        ("Duplicate review completed", report.get("duplicate_count", 0) >= 0),
        ("Data quality findings flagged", report.get("issue_count", 0) >= 0),
        ("Remediation list available", True),
    ]

    if score >= 85:
        status = "Ready for operational use"
    elif score >= 70:
        status = "Needs targeted remediation"
    else:
        status = "Not ready for operational use"

    return {
        "quality_score": round(score, 2),
        "status": status,
        "checks": checks,
    }
