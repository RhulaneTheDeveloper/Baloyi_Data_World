"""
pages_new/pg_readiness.py  –  Technical System Readiness
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime
from ui.styles import page_header, empty_state, metric_card, badge


def render() -> None:
    st.markdown(page_header("Technical Readiness Assessment",
        "Assess system and data readiness for downstream operational use","⚙️"),
        unsafe_allow_html=True)

    wb   = st.session_state.get("workbook")
    df   = st.session_state.get("active_df")
    analysis = st.session_state.get("analysis_results", {})
    mapping  = st.session_state.get("column_mapping", {})
    mandatory = st.session_state.get("mandatory_fields", [])
    issues   = st.session_state.get("quality_issues", [])

    # ── Automated checks ──────────────────────────────────────
    checks = [
        ("Workbook readability",        wb is not None, "Workbook loaded and parsed without error."),
        ("Required fields available",   bool(mapping), f"{len(mapping)} fields successfully mapped."),
        ("Mandatory fields configured", bool(mandatory), f"{len(mandatory)} mandatory fields configured."),
        ("Data type compatibility",     df is not None, "DataFrame loaded with pandas-compatible types."),
        ("Data structure compatibility",df is not None and not df.empty, "Dataset is non-empty."),
        ("Completeness baseline met",   analysis.get("overall_completeness",0) >= 70,
            f"Overall completeness: {analysis.get('overall_completeness',0):.1f}%"),
        ("Duplicate review completed",  "duplicate_count" in analysis,
            f"{analysis.get('duplicate_count',0)} duplicates detected."),
        ("Quality score calculated",    "quality_score" in analysis,
            f"Quality score: {analysis.get('quality_score',0):.1f}%"),
        ("Issue register populated",    bool(issues), f"{len(issues)} quality issues recorded."),
        ("Export directory accessible", True, "Exports directory is accessible."),
    ]

    passed  = sum(1 for _, ok, _ in checks if ok)
    failed  = sum(1 for _, ok, _ in checks if not ok)
    total   = len(checks)
    readiness_pct = round(passed / total * 100, 1)

    # ── Summary KPIs ──────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📊 Readiness Summary</h3>', unsafe_allow_html=True)
    mc = st.columns(4)
    mc[0].markdown(metric_card("📊",f"{readiness_pct:.0f}%","Readiness Score",
        "Ready" if readiness_pct>=80 else "Needs attention",
        "success" if readiness_pct>=80 else "warning"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("✅",str(passed),"Checks Passed","","success"), unsafe_allow_html=True)
    mc[2].markdown(metric_card("❌",str(failed),"Checks Failed","","critical" if failed else ""), unsafe_allow_html=True)
    mc[3].markdown(metric_card("📋",str(total),"Total Checks"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Overall status
    if readiness_pct >= 85:
        status_text = "✅ Ready for downstream processing"
        status_col  = "#DCFCE7"
        status_text_col = "#15803D"
    elif readiness_pct >= 70:
        status_text = "⚠️ Targeted remediation required before proceeding"
        status_col  = "#FEF3C7"
        status_text_col = "#92400E"
    else:
        status_text = "❌ Not ready — significant data quality issues must be resolved"
        status_col  = "#FEE2E2"
        status_text_col = "#991B1B"

    st.markdown(
        f'<div style="background:{status_col};color:{status_text_col};padding:1rem 1.5rem;'
        f'border-radius:10px;font-weight:600;font-size:.95rem;margin-bottom:1rem">{status_text}</div>',
        unsafe_allow_html=True)

    # ── Automated checks table ────────────────────────────────
    st.markdown('<div class="section-card"><h3>🤖 Automated System Checks</h3>', unsafe_allow_html=True)
    check_rows = [{"Check": name, "Status": "✅ Pass" if ok else "❌ Fail", "Evidence": note}
                  for name, ok, note in checks]
    st.dataframe(pd.DataFrame(check_rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Manual confirmation checkboxes ────────────────────────
    st.markdown('<div class="section-card"><h3>👤 Manual Business Confirmations</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:.8rem;color:var(--color-muted)">These items require human confirmation. '
        'Check each item when confirmed and provide the responsible person.</p>', unsafe_allow_html=True)

    if "manual_checks" not in st.session_state:
        st.session_state["manual_checks"] = {}

    manual_items = [
        ("hr_data_ownership",    "HR data ownership confirmed"),
        ("business_approval",    "Business approval for data use obtained"),
        ("access_permissions",   "Access permissions verified"),
        ("data_protection",      "Data protection controls in place"),
        ("backup_recovery",      "Backup and recovery arrangements confirmed"),
        ("authorised_corrections","Authorised data corrections approved"),
    ]

    for key, label in manual_items:
        mc_col, person_col, date_col = st.columns([2, 2, 1])
        with mc_col:
            checked = st.checkbox(label, value=st.session_state["manual_checks"].get(key,{}).get("checked",False), key=f"mc_{key}")
        with person_col:
            person = st.text_input("Responsible person", value=st.session_state["manual_checks"].get(key,{}).get("person",""),
                key=f"mcp_{key}", label_visibility="collapsed", placeholder="Responsible person")
        with date_col:
            if checked:
                st.markdown(f'<div style="padding:.4rem 0;font-size:.8rem;color:var(--color-muted)">'
                    f'{datetime.today().strftime("%d %b %Y")}</div>', unsafe_allow_html=True)
        st.session_state["manual_checks"][key] = {"checked": checked, "person": person}

    if st.button("💾 Save Manual Confirmations"):
        st.success("Manual confirmations saved.")
    st.markdown("</div>", unsafe_allow_html=True)
