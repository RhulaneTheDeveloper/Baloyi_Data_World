"""
pages_new/pg_clarification.py  –  Business Clarification Register
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime
from ui.styles import page_header, empty_state, metric_card

DEPARTMENTS = ["HR","IT","Finance","Operations","Learning & Development","Data Owner","Management","Other"]
APPROVAL_STATUSES = ["Pending","Under Review","Approved","Rejected","Escalated"]


def render() -> None:
    st.markdown(page_header("Business Clarification Register",
        "Track data issues that require human decisions or business owner input","💬"),
        unsafe_allow_html=True)

    if "clarification_register" not in st.session_state:
        st.session_state["clarification_register"] = []

    register: list[dict] = st.session_state["clarification_register"]

    # ── Summary ───────────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📊 Clarification Summary</h3>', unsafe_allow_html=True)
    mc = st.columns(4)
    pending = len([r for r in register if r.get("approval_status") == "Pending"])
    resolved = len([r for r in register if r.get("approval_status") == "Approved"])
    mc[0].markdown(metric_card("💬",str(len(register)),"Total Clarifications"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("⏳",str(pending),"Pending Response","","warning" if pending else ""), unsafe_allow_html=True)
    mc[2].markdown(metric_card("✅",str(resolved),"Approved / Resolved","","success" if resolved else ""), unsafe_allow_html=True)
    mc[3].markdown(metric_card("📋",str(len(register)-resolved-pending),"Under Review"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Add new clarification ─────────────────────────────────
    st.markdown('<div class="section-card"><h3>➕ Add New Clarification</h3>', unsafe_allow_html=True)
    df = st.session_state.get("active_df")
    with st.form("new_clarification", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        question    = fc1.text_area("Clarification question *", height=90)
        affected_field = fc1.selectbox("Affected field", ["—"] + (list(df.columns) if df is not None else []))
        affected_record = fc1.text_input("Affected record / learner ID")
        dept        = fc2.selectbox("Responsible department", DEPARTMENTS)
        assigned_to = fc2.text_input("Assigned person")
        date_raised = fc2.date_input("Date raised", value=datetime.today())
        submitted   = st.form_submit_button("Add Clarification")
    if submitted:
        if question.strip():
            register.append({
                "id": len(register)+1,
                "question": question,
                "affected_field": affected_field,
                "affected_record": affected_record,
                "responsible_dept": dept,
                "assigned_to": assigned_to,
                "date_raised": str(date_raised),
                "response": "",
                "business_decision": "",
                "approval_status": "Pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.session_state["clarification_register"] = register
            st.success("Clarification added.")
            st.rerun()
        else:
            st.error("Question is required.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Register table ────────────────────────────────────────
    if register:
        st.markdown('<div class="section-card"><h3>📋 Clarification Register</h3>', unsafe_allow_html=True)
        for idx, item in enumerate(register):
            with st.expander(f"#{item['id']} — {item['question'][:70]}… | {item['approval_status']}"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    st.markdown(f"""
                    <div style="font-size:.85rem;line-height:2">
                    <div class="info-row"><span class="info-label">Question</span><span class="info-value">{item['question']}</span></div>
                    <div class="info-row"><span class="info-label">Affected Field</span><span class="info-value">{item.get('affected_field','—')}</span></div>
                    <div class="info-row"><span class="info-label">Affected Record</span><span class="info-value">{item.get('affected_record','—')}</span></div>
                    <div class="info-row"><span class="info-label">Department</span><span class="info-value">{item.get('responsible_dept','—')}</span></div>
                    <div class="info-row"><span class="info-label">Assigned To</span><span class="info-value">{item.get('assigned_to','—')}</span></div>
                    <div class="info-row"><span class="info-label">Date Raised</span><span class="info-value">{item.get('date_raised','—')}</span></div>
                    </div>""", unsafe_allow_html=True)
                with uc2:
                    response = st.text_area("Response received", value=item.get("response",""), key=f"cl_resp_{idx}", height=70)
                    decision = st.text_input("Business decision", value=item.get("business_decision",""), key=f"cl_dec_{idx}")
                    new_status = st.selectbox("Approval status", APPROVAL_STATUSES,
                        index=APPROVAL_STATUSES.index(item.get("approval_status","Pending")),
                        key=f"cl_stat_{idx}")
                    if st.button("💾 Save", key=f"cl_save_{idx}"):
                        register[idx]["response"] = response
                        register[idx]["business_decision"] = decision
                        register[idx]["approval_status"] = new_status
                        register[idx]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.session_state["clarification_register"] = register
                        st.success("Saved.")
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Export
        st.markdown('<div class="section-card"><h3>⬇️ Export Register</h3>', unsafe_allow_html=True)
        import io as _io
        buf = _io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            pd.DataFrame(register).to_excel(writer, sheet_name="Clarification Register", index=False)
        buf.seek(0)
        st.download_button("📥 Download Clarification Register (Excel)", data=buf.getvalue(),
            file_name="business_clarification_register.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("</div>", unsafe_allow_html=True)
