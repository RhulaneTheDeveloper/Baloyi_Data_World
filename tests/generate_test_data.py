"""
tests/generate_test_data.py
Generate a synthetic learner dataset for development and testing.
Run: .venv\\Scripts\\python tests\\generate_test_data.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

FIRST_NAMES = [
    "Thabo", "Lerato", "Sipho", "Nomvula", "Bongani", "Zanele", "Mandla",
    "Palesa", "Kagiso", "Lindiwe", "Tshepo", "Naledi", "Mpho", "Refilwe",
    "Kabelo", "Dineo", "Katlego", "Boitumelo", "Lesego", "Masego",
]
SURNAMES = [
    "Mokoena", "Nkosi", "Mthembu", "Dlamini", "Zulu", "Ndlovu", "Khumalo",
    "Molefe", "Mahlangu", "Sithole", "Mabena", "Tshabalala", "Baloyi",
    "Mashaba", "Mabuza", "Phiri", "Chauke", "Mkhatshwa", "Gumede", "Shabangu",
]
DEPARTMENTS = [
    "IT", "Human Resources", "Finance", "Operations", "Learning & Development",
    "Marketing", "Sales", "Legal", "Compliance", "Executive Office",
]
PROGRAMMES = [
    "Leadership Development", "Data Analytics", "Project Management",
    "Compliance Training", "Digital Skills", "Financial Literacy",
    "Technical Certification", "Mentorship Programme",
]
STATUSES = ["Active", "Completed", "Withdrawn", "Deferred", "In Progress"]


def _rand_email(first: str, last: str) -> str:
    domain = random.choice(["baloyidataworld.co.za", "baloyidataworld.com", "baloyi.co.za"])
    sep = random.choice([".", "_", ""])
    return f"{first.lower()}{sep}{last.lower()}@{domain}"


def _rand_phone() -> str:
    prefix = random.choice(["082", "083", "084", "071", "072", "076", "078"])
    return prefix + "".join(str(random.randint(0, 9)) for _ in range(7))


def _rand_date(y_start: int = 2023, y_end: int = 2025) -> str:
    year  = random.randint(y_start, y_end)
    month = random.randint(1, 12)
    day   = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate(n: int = 150) -> pd.DataFrame:
    rows = []
    for i in range(n):
        first = random.choice(FIRST_NAMES)
        last  = random.choice(SURNAMES)
        lid   = f"HOS-{1000 + i:05d}"

        row = {
            "Learner ID":       lid,
            "First Name":       first,
            "Surname":          last,
            "Email Address":    _rand_email(first, last),
            "Phone Number":     _rand_phone(),
            "Department":       random.choice(DEPARTMENTS),
            "Programme":        random.choice(PROGRAMMES),
            "Enrolment Date":   _rand_date(2023, 2025),
            "Employment Status":random.choice(STATUSES),
            "Gender":           random.choice(["Male", "Female"]),
        }

        # Inject data quality issues deliberately (≈20% of records)
        if random.random() < 0.08:
            row["Email Address"] = "bad-email"
        if random.random() < 0.06:
            row["First Name"] = ""
        if random.random() < 0.05:
            row["Department"] = random.choice(["IT", "I.T.", "it", "Information Technology"])
        if random.random() < 0.05:
            row["Employment Status"] = random.choice(["ACTIVE", "active", "Actve"])
        if random.random() < 0.04:
            row["Phone Number"] = "12345"
        if random.random() < 0.03:
            row["Enrolment Date"] = "not-a-date"
        if random.random() < 0.04:
            row["Surname"] = None

        rows.append(row)

    # Add deliberate duplicate records
    if rows:
        rows.append({**rows[0]})
        rows.append({**rows[1], "Learner ID": rows[0]["Learner ID"]})  # duplicate ID

    df = pd.DataFrame(rows)
    return df


def main():
    output_dir = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = generate(150)
    output_path = output_dir / "test_learner_data.xlsx"
    df.to_excel(str(output_path), index=False, engine="openpyxl")
    print(f"Generated {len(df)} records → {output_path}")

    # Also generate a minimal CSV variant
    csv_path = output_dir / "test_learner_data.csv"
    df.head(30).to_csv(str(csv_path), index=False)
    print(f"Generated CSV sample → {csv_path}")


if __name__ == "__main__":
    main()
