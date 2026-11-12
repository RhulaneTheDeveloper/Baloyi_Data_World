from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
EXPORTS_DIR = APP_ROOT / "exports"
UPLOADS_DIR = APP_ROOT / "uploads"
DATABASE_PATH = APP_ROOT / "database" / "hosi_analysis.db"

DEFAULT_MANDATORY_FIELDS = [
    "learner_id",
    "first_name",
    "surname",
    "email",
    "programme",
    "start_date",
    "status",
]

COLUMN_ALIASES = {
    "learner_id": ["learner_id", "student_id", "student_number", "candidate_id", "learner number"],
    "first_name": ["first_name", "firstname", "given_name", "name", "forenames"],
    "surname": ["surname", "last_name", "lastname", "family_name"],
    "email": ["email", "email_address", "learner_email"],
    "phone": ["phone", "phone_number", "mobile_number", "cell_number"],
    "programme": ["programme", "program", "course", "qualification"],
    "start_date": ["start_date", "date_started", "enrolment_date"],
    "status": ["status", "learner_status", "registration_status"],
    "date_of_birth": ["date_of_birth", "dob", "birth_date"],
    "department": ["department", "business_unit", "unit"],
}
