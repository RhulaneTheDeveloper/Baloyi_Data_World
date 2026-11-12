# Baloyi Data World

A professional enterprise-grade Python web application for learner data profiling, quality assessment, and remediation. Built with Streamlit for the data analysis workstream at Baloyi Data World.

## Project Structure

```
Data_Analysis_Project/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── config/
│   ├── settings.py                 # Application settings and column aliases
│   └── quality_rules.py            # Quality rule thresholds
├── database/
│   ├── db.py                       # SQLite database operations
│   └── models.py                   # Data models
├── modules/
│   ├── __init__.py
│   ├── excel_import.py             # Workbook loading and field matching
│   ├── data_profiling.py           # DataFrame profiling and field dictionary
│   ├── completeness.py             # Mandatory field completeness
│   ├── duplicate_detection.py      # Duplicate record identification
│   ├── consistency.py              # Email, phone, date validation
│   ├── cleansing.py                # Cleansing plan generation
│   ├── remediation.py              # Remediation issue tracking
│   ├── readiness.py                # Technical readiness assessment
│   └── report_generator.py         # Excel & PDF report generation
├── ui/
│   ├── __init__.py
│   ├── styles.py                   # Global CSS and UI component helpers
│   └── sidebar.py                  # Persistent sidebar navigation
├── pages_new/
│   ├── __init__.py
│   ├── pg_dashboard.py             # Dashboard with real-time KPIs
│   ├── pg_upload.py                # Data upload with mapping & config
│   ├── pg_scope.py                 # Scope & volume analysis
│   ├── pg_dictionary.py            # Data dictionary generation
│   ├── pg_completeness.py          # Mandatory field completeness
│   ├── pg_quality.py               # Data quality analysis engine
│   ├── pg_remediation.py           # Remediation tracking centre
│   ├── pg_clarification.py         # Business clarification register
│   ├── pg_readiness.py             # Technical readiness assessment
│   ├── pg_reports.py               # Report generation & downloads
│   ├── pg_history.py               # Analysis session history
│   ├── pg_settings.py              # Application settings
│   └── pg_placeholder.py           # Placeholder page routing
├── exports/                        # Generated report output directory
├── tests/
│   ├── test_analysis.py            # Automated test suite
│   ├── generate_test_data.py       # Synthetic test data generator
│   └── fixtures/                   # Test data files
└── pages/                          # Legacy Streamlit multi-page (unused)
```

## Features

### Milestone 1 (Complete)
- ✅ Professional enterprise UI with custom CSS and branding
- ✅ Persistent sidebar navigation with 12 modules
- ✅ Dashboard with live KPIs, charts, and empty states
- ✅ Excel upload with file validation (type, size, content)
- ✅ Worksheet selection and header row configuration
- ✅ Data preview (first 25 rows)
- ✅ Learner identifier column selection
- ✅ Column mapping (source → standardised fields)
- ✅ Mandatory field configuration
- ✅ Scope & volume analysis with breakdowns
- ✅ Data dictionary with field inspector and export
- ✅ Completeness analysis with progress bars
- ✅ Data quality engine (duplicates, emails, inconsistencies)
- ✅ Remediation register with status tracking
- ✅ Business clarification register
- ✅ Technical readiness assessment
- ✅ Excel and PDF report generation
- ✅ Analysis history tracking
- ✅ Settings page
- ✅ SQLite database with full schema
- ✅ Automated test suite (40+ tests)
- ✅ Synthetic test data generator

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run the Application

```bash
.venv\Scripts\streamlit run app.py
```

The application will open at http://localhost:8501

## Run Tests

```bash
.venv\Scripts\python -m pytest tests/ -v
```

## Generate Test Data

```bash
.venv\Scripts\python tests\generate_test_data.py
```

This creates `tests/fixtures/test_learner_data.xlsx` with 150 synthetic learner records containing deliberate data quality issues.

## Typical Workflow

1. **Upload** an Excel workbook on the Data Upload page.
2. **Select** the worksheet and header row.
3. **Map** source columns to standardised field names.
4. **Configure** mandatory fields.
5. **Review** scope, volume, and the data dictionary.
6. **Analyse** completeness, duplicates, and data quality.
7. **Assign** remediation actions and record business clarifications.
8. **Confirm** technical readiness.
9. **Export** reports for management review.

## Technology Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.12+ | Runtime |
| Streamlit | Web UI |
| Pandas | Data manipulation |
| OpenPyXL | Excel processing |
| Plotly | Interactive charts |
| SQLite | Persistent storage |
| XlsxWriter | Excel report generation |
| ReportLab | PDF report generation |
| Pytest | Automated testing |

## Prepared By

**Rhulane Baloyi** · Baloyi Data World · 2026
