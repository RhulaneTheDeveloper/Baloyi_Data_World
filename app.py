"""
app.py
Baloyi Data World – Main Application Entry Point.

Run with:
    start_app.bat
  or
    C:\\Users\\Hosi\\AppData\\Local\\hosi_analyzer_venv\\Scripts\\streamlit.exe run app.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import streamlit as st

# ── Path setup ────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Page config (must be first Streamlit call) ─────────────────
st.set_page_config(
    page_title="Baloyi Data World",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Baloyi Data World v1.0 · Prepared by Rhulane Baloyi",
    },
)

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("baloyi_data_world.app")


# ── Database init ─────────────────────────────────────────────
@st.cache_resource
def _init_database() -> None:
    try:
        from database.db import init_db
        init_db()
        logger.info("Database initialised.")
    except Exception as exc:
        logger.warning("Database init warning: %s", exc)


# ── Page dispatcher ───────────────────────────────────────────
def _load_page(page_key: str) -> None:
    """Dispatch to the appropriate page module by key."""
    dispatch = {
        "dashboard":    "pages_new.pg_dashboard",
        "upload":       "pages_new.pg_upload",
        "gap_review":   "pages_new.pg_gap_review",
        "scope":        "pages_new.pg_scope",
        "dictionary":   "pages_new.pg_dictionary",
        "completeness": "pages_new.pg_completeness",
        "quality":      "pages_new.pg_quality",
        "remediation":  "pages_new.pg_remediation",
        "clarification":"pages_new.pg_clarification",
        "readiness":    "pages_new.pg_readiness",
        "reports":      "pages_new.pg_reports",
        "history":      "pages_new.pg_history",
        "settings":     "pages_new.pg_settings",
    }
    module_name = dispatch.get(page_key)
    if not module_name:
        st.error(f"Unknown page: {page_key!r}")
        return
    try:
        import importlib
        module = importlib.import_module(module_name)
        module.render()
    except Exception as exc:
        logger.exception("Page render error for '%s': %s", page_key, exc)
        st.error(f"⚠️ An error occurred loading this page.")
        with st.expander("Error details"):
            st.exception(exc)


# ── Main ──────────────────────────────────────────────────────
def main() -> None:
    # Inject CSS
    from ui.styles import inject_styles
    inject_styles()

    # Sidebar nav button styling overrides
    st.markdown("""
    <style>
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: rgba(255,255,255,.72) !important;
        border: none !important;
        border-radius: 6px !important;
        text-align: left !important;
        font-size: .875rem !important;
        font-weight: 500 !important;
        padding: .45rem 1rem !important;
        margin: .05rem 0 !important;
        box-shadow: none !important;
        width: 100% !important;
        justify-content: flex-start !important;
        transition: background .15s, color .15s !important;
        border-left: 3px solid transparent !important;
        display: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:not(:disabled):hover {
        background: rgba(255,255,255,.09) !important;
        color: #FFFFFF !important;
        transform: none !important;
        display: block !important;
    }
    [data-testid="stSidebar"] .stButton > button:disabled {
        display: none !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _init_database()

    from ui.sidebar import render_sidebar
    active_page = render_sidebar()

    _load_page(active_page)


if __name__ == "__main__":
    main()
