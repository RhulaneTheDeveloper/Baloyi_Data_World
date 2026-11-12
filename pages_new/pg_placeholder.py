"""
pages_new/pg_placeholder.py
Generic professional placeholder for modules under development.
"""
from __future__ import annotations

import streamlit as st
from ui.styles import badge, empty_state, page_header


def render_no_data(module_name: str, icon: str, description: str) -> None:
    """Show 'no dataset loaded' state within any module."""
    st.markdown(
        empty_state(
            "📂",
            "No dataset loaded",
            f"Upload a workbook using the Data Upload module to use {module_name}.",
        ),
        unsafe_allow_html=True,
    )


def render_scope() -> None:
    from pages_new.pg_scope import render
    render()


def render_dictionary() -> None:
    from pages_new.pg_dictionary import render
    render()


def render_completeness() -> None:
    from pages_new.pg_completeness import render
    render()


def render_quality() -> None:
    from pages_new.pg_quality import render
    render()


def render_remediation() -> None:
    from pages_new.pg_remediation import render
    render()


def render_clarification() -> None:
    from pages_new.pg_clarification import render
    render()


def render_readiness() -> None:
    from pages_new.pg_readiness import render
    render()


def render_reports() -> None:
    from pages_new.pg_reports import render
    render()


def render_history() -> None:
    from pages_new.pg_history import render
    render()


def render_settings() -> None:
    from pages_new.pg_settings import render
    render()
