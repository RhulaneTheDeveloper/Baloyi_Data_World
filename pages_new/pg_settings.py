"""
pages_new/pg_settings.py  –  Application Settings
"""
from __future__ import annotations
import streamlit as st
from ui.styles import page_header, metric_card


def render() -> None:
    st.markdown(page_header("Settings",
        "Configure application preferences, mandatory fields and quality thresholds","⚙️"),
        unsafe_allow_html=True)

    # ── Analysis project name ─────────────────────────────────
    st.markdown('<div class="section-card"><h3>📋 Project Information</h3>', unsafe_allow_html=True)
    project_name = st.text_input("Analysis project name",
        value=st.session_state.get("project_name","Baloyi Data World – Data Analysis"))
    analyst_name = st.text_input("Analyst name",
        value=st.session_state.get("analyst_name","Rhulane Baloyi"))
    if st.button("Save Project Info"):
        st.session_state["project_name"] = project_name
        st.session_state["analyst_name"] = analyst_name
        st.success("Project information saved.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quality thresholds ────────────────────────────────────
    st.markdown('<div class="section-card"><h3>⚖️ Quality Thresholds</h3>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    comp_warn  = tc1.slider("Completeness warning threshold (%)", 50, 95, st.session_state.get("comp_warn",70))
    comp_good  = tc1.slider("Completeness good threshold (%)", comp_warn+1, 100, st.session_state.get("comp_good",95))
    qual_warn  = tc2.slider("Quality score warning threshold (%)", 40, 85, st.session_state.get("qual_warn",60))
    qual_good  = tc2.slider("Quality score good threshold (%)", qual_warn+1, 100, st.session_state.get("qual_good",80))
    if st.button("Save Thresholds"):
        st.session_state.update({"comp_warn":comp_warn,"comp_good":comp_good,
                                  "qual_warn":qual_warn,"qual_good":qual_good})
        st.success("Thresholds saved.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── File upload settings ──────────────────────────────────
    st.markdown('<div class="section-card"><h3>📤 Upload Settings</h3>', unsafe_allow_html=True)
    max_size = st.number_input("Maximum file size (MB)", min_value=5, max_value=200, value=50)
    if st.button("Save Upload Settings"):
        st.session_state["max_upload_mb"] = max_size
        st.success("Upload settings saved.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Session ───────────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>🔄 Session Management</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:.875rem;color:var(--color-muted)">Clear the current analysis session. '
        'This will not delete uploaded files from your computer.</p>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Current Session", type="secondary"):
        for key in ["workbook","active_df","analysis_results","quality_issues",
                    "column_mapping","mandatory_fields","id_column","uploaded_filename"]:
            st.session_state.pop(key, None)
        st.success("Session cleared. Upload a new workbook to begin.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
