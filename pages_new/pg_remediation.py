"""
pages_new/pg_remediation.py  –  Data Remediation Centre
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime
from ui.styles import page_header, empty_state, metric_card, badge

STATUSES = ["Open","Under Review","Awaiting HR Clarification","Awaiting Data Owner",
            "Approved for Correction","Resolved","Rejected"]


def render() -> None:
    st.markdown(page_header("Data Remediation Centre",
        "Track, assign and resolve data quality issues with a full audit trail","🛠️"),
        unsafe_allow_html=True)

    issues: list[dict] = st.session_state.get("quality_issues",[])
    if not issues and st.session_state.get("active_df") is None:
        st.markdown(empty_state("📂","No dataset loaded",
            "Upload a workbook and run Data Quality analysis to populate the remediation register."),
            unsafe_allow_html=True)
        return

    if not issues:
        st.info("✅ No quality issues found in the current dataset. Run **Data Quality** analysis first.")
        return

    # ── Summary ───────────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📊 Remediation Summary</h3>', unsafe_allow_html=True)
    open_c     = len([i for i in issues if i.get("status") == "Open"])
    resolved_c = len([i for i in issues if i.get("status") == "Resolved"])
    high_c     = len([i for i in issues if i.get("severity") in ("High","Critical")])
    mc = st.columns(4)
    mc[0].markdown(metric_card("🔍",str(len(issues)),"Total Issues"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("🔴",str(open_c),"Open Issues","",
        "critical" if open_c else ""), unsafe_allow_html=True)
    mc[2].markdown(metric_card("✅",str(resolved_c),"Resolved","","success" if resolved_c else ""), unsafe_allow_html=True)
    mc[3].markdown(metric_card("⚠️",str(high_c),"High/Critical","Prioritise these","warning" if high_c else ""), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Filter ────────────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>🔍 Filter Issues</h3>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    sev_filter = fc1.selectbox("Severity",["All","Critical","High","Medium","Low"])
    stat_filter = fc2.selectbox("Status",["All"]+STATUSES)
    field_filter = fc3.text_input("Field name contains", "")
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = list(issues)
    if sev_filter != "All":
        filtered = [i for i in filtered if i.get("severity") == sev_filter]
    if stat_filter != "All":
        filtered = [i for i in filtered if i.get("status") == stat_filter]
    if field_filter:
        filtered = [i for i in filtered if field_filter.lower() in str(i.get("field","")).lower()]

    # ── Issue register ────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📋 Remediation Register</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:.8rem;color:var(--color-muted)">Showing {len(filtered)} of {len(issues)} issues</p>', unsafe_allow_html=True)

    for idx, issue in enumerate(filtered[:100]):
        sev = issue.get("severity","Low")
        sev_v = "critical" if sev == "Critical" else "warning" if sev in ("High","Medium") else "muted"
        with st.expander(f"{badge(sev,sev_v)} {issue.get('issue','—')[:80]} | {issue.get('field','—')}", expanded=False):
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown(f"""
                <div style="font-size:.85rem;line-height:2">
                <div class="info-row"><span class="info-label">Issue</span><span class="info-value">{issue.get('issue','—')}</span></div>
                <div class="info-row"><span class="info-label">Field</span><span class="info-value">{issue.get('field','—')}</span></div>
                <div class="info-row"><span class="info-label">Original Value</span><span class="info-value"><code>{str(issue.get('original_value','—'))[:80]}</code></span></div>
                <div class="info-row"><span class="info-label">Severity</span><span class="info-value">{badge(sev,sev_v)}</span></div>
                <div class="info-row"><span class="info-label">Status</span><span class="info-value">{badge(issue.get('status','Open'),'info')}</span></div>
                </div>""", unsafe_allow_html=True)
            with ec2:
                new_status = st.selectbox("Update status", STATUSES,
                    index=STATUSES.index(issue.get("status","Open")) if issue.get("status","Open") in STATUSES else 0,
                    key=f"rem_status_{idx}")
                owner = st.text_input("Assigned to", value=issue.get("owner",""), key=f"rem_owner_{idx}")
                notes = st.text_area("Resolution notes", value=issue.get("notes",""), height=80, key=f"rem_notes_{idx}")
                if st.button("💾 Save", key=f"rem_save_{idx}"):
                    issues[issues.index(issue)]["status"] = new_status
                    issues[issues.index(issue)]["owner"]  = owner
                    issues[issues.index(issue)]["notes"]  = notes
                    issues[issues.index(issue)]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state["quality_issues"] = issues
                    st.success("Saved.")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────
    if issues:
        st.markdown('<div class="section-card"><h3>⬇️ Export Remediation Register</h3>', unsafe_allow_html=True)
        import io as _io
        buf = _io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            pd.DataFrame(issues).to_excel(writer, sheet_name="Remediation Register", index=False)
        buf.seek(0)
        st.download_button("📥 Download Remediation Register (Excel)", data=buf.getvalue(),
            file_name="remediation_register.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("</div>", unsafe_allow_html=True)
