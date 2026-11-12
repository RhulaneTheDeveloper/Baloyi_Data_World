"""
pages_new/pg_reports.py  –  Reports & Exports
"""
from __future__ import annotations
import io
import streamlit as st
import pandas as pd
from datetime import datetime
from ui.styles import page_header, empty_state, metric_card

PREPARED_BY = "Rhulane Baloyi"
PROJECT_NAME = "Baloyi Data World – Data Analysis"


def _excel_quality_report(df, summary, issues, mapping, mandatory) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb_xl = writer.book
        # Formats
        hdr_fmt = wb_xl.add_format({"bold":True,"bg_color":"#142B3B","font_color":"#FFFFFF","border":1})
        title_fmt = wb_xl.add_format({"bold":True,"font_size":14,"font_color":"#142B3B"})
        sub_fmt = wb_xl.add_format({"italic":True,"font_color":"#73808C","font_size":10})

        # Cover sheet
        cover = wb_xl.add_worksheet("Cover")
        cover.write(0, 0, "Baloyi Data World – Quality Report", title_fmt)
        cover.write(1, 0, f"Project: {PROJECT_NAME}", sub_fmt)
        cover.write(2, 0, f"Prepared by: {PREPARED_BY}", sub_fmt)
        cover.write(3, 0, f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}", sub_fmt)
        cover.write(5, 0, "Report Contents:", hdr_fmt)
        for i,name in enumerate(["Summary","Data Quality","Field Inventory","Issue Register"],1):
            cover.write(5+i, 0, f"  Sheet {i}: {name}")
        cover.set_column(0, 0, 50)

        # Summary sheet
        summary_data = [["Metric","Value"],
            ["File Name", summary.get("filename","—")],
            ["Total Records", summary.get("row_count",0)],
            ["Total Fields", summary.get("col_count",0)],
            ["Overall Completeness", f"{summary.get('overall_completeness',0):.1f}%"],
            ["Quality Score", f"{summary.get('quality_score',0):.1f}%"],
            ["Duplicate Records", summary.get("duplicate_count",0)],
            ["Total Issues", len(issues)],
            ["Mandatory Fields Configured", len(mandatory)],
            ["Mapped Fields", len(mapping)],
        ]
        ws_sum = wb_xl.add_worksheet("Summary")
        for r_idx, row in enumerate(summary_data):
            for c_idx, val in enumerate(row):
                if r_idx == 0:
                    ws_sum.write(r_idx, c_idx, val, hdr_fmt)
                else:
                    ws_sum.write(r_idx, c_idx, val)
        ws_sum.set_column(0, 0, 30)
        ws_sum.set_column(1, 1, 25)

        # Field inventory
        if df is not None:
            total_rows = len(df)
            rev_map = {v:k for k,v in mapping.items()}
            inv_rows = [["Source Column","Standardised","Type","Populated","Missing","Completeness %","Mandatory"]]
            for col in df.columns:
                s = df[col]
                filled = int(s.notna().sum())
                pct = round(filled/max(total_rows,1)*100,1)
                std = rev_map.get(col,"")
                is_mand = std in mandatory
                dtype_l = "Numeric" if pd.api.types.is_numeric_dtype(s.dtype) else "Text"
                inv_rows.append([col, std or "—", dtype_l, filled, total_rows-filled, pct, "Yes" if is_mand else "No"])
            ws_inv = wb_xl.add_worksheet("Field Inventory")
            for r_idx, row in enumerate(inv_rows):
                for c_idx, val in enumerate(row):
                    if r_idx == 0:
                        ws_inv.write(r_idx, c_idx, val, hdr_fmt)
                    else:
                        ws_inv.write(r_idx, c_idx, val)
            ws_inv.autofilter(0, 0, len(inv_rows)-1, len(inv_rows[0])-1)
            ws_inv.set_column(0, 6, 20)

        # Issue register
        if issues:
            issue_rows = [["Issue","Severity","Field","Original Value","Status","Assigned To","Notes"]]
            for iss in issues:
                issue_rows.append([iss.get("issue",""), iss.get("severity",""), iss.get("field",""),
                    str(iss.get("original_value",""))[:100], iss.get("status","Open"),
                    iss.get("owner",""), iss.get("notes","")])
            ws_iss = wb_xl.add_worksheet("Issue Register")
            for r_idx, row in enumerate(issue_rows):
                for c_idx, val in enumerate(row):
                    if r_idx == 0:
                        ws_iss.write(r_idx, c_idx, val, hdr_fmt)
                    else:
                        ws_iss.write(r_idx, c_idx, val)
            ws_iss.autofilter(0, 0, len(issue_rows)-1, len(issue_rows[0])-1)
            ws_iss.set_column(0, 6, 22)

    buf.seek(0)
    return buf.getvalue()


def _pdf_summary_report(summary, issues) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
        fontSize=20, spaceAfter=6, textColor=colors.HexColor("#142B3B"))
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
        fontSize=13, spaceAfter=4, textColor=colors.HexColor("#142B3B"))
    body_style = ParagraphStyle("Body2", parent=styles["Normal"],
        fontSize=10, spaceAfter=4, textColor=colors.HexColor("#202B36"))
    muted_style = ParagraphStyle("Muted", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#73808C"))

    story = []
    story.append(Paragraph("Baloyi Data World", title_style))
    story.append(Paragraph("Data Quality Analysis Report", h2_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#16A36A")))
    story.append(Spacer(1, 0.3*cm))

    meta = [
        ["Project", PROJECT_NAME],
        ["Prepared by", PREPARED_BY],
        ["Dataset", summary.get("filename","—")],
        ["Generated", datetime.now().strftime("%d %B %Y %H:%M")],
    ]
    for k, v in meta:
        story.append(Paragraph(f"<b>{k}:</b> {v}", body_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Executive Summary", h2_style))
    story.append(Paragraph(
        f"This report presents the results of the data quality assessment conducted on the uploaded "
        f"learner dataset. The dataset contains <b>{summary.get('row_count',0):,}</b> records across "
        f"<b>{summary.get('col_count',0)}</b> fields. "
        f"The overall data completeness is <b>{summary.get('overall_completeness',0):.1f}%</b> and the "
        f"calculated quality score is <b>{summary.get('quality_score',0):.1f}%</b>. "
        f"A total of <b>{len(issues)}</b> quality issues have been identified.",
        body_style))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Key Metrics", h2_style))
    table_data = [["Metric", "Value"],
        ["Total Records", f"{summary.get('row_count',0):,}"],
        ["Total Fields", str(summary.get('col_count',0))],
        ["Overall Completeness", f"{summary.get('overall_completeness',0):.1f}%"],
        ["Quality Score", f"{summary.get('quality_score',0):.1f}%"],
        ["Duplicate Records", str(summary.get('duplicate_count',0))],
        ["Total Issues Identified", str(len(issues))],
    ]
    tbl = Table(table_data, colWidths=[8*cm, 7*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#142B3B")),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTSIZE",   (0,0),(-1,-1), 10),
        ("BACKGROUND", (0,1),(-1,-1), colors.HexColor("#F5F7FA")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F7FA")]),
        ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("RIGHTPADDING",(0,0),(-1,-1), 8),
        ("TOPPADDING", (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    if issues:
        story.append(Paragraph("Top Issues Summary", h2_style))
        issue_table_data = [["Issue", "Severity", "Status"]]
        for iss in issues[:20]:
            issue_table_data.append([iss.get("issue","")[:60], iss.get("severity",""), iss.get("status","Open")])
        iss_tbl = Table(issue_table_data, colWidths=[10*cm, 3*cm, 4*cm])
        iss_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#142B3B")),
            ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ("LEFTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F5F7FA")]),
        ]))
        story.append(iss_tbl)
        story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Disclaimer", h2_style))
    story.append(Paragraph(
        "This report was generated by the Baloyi Data World application. All findings are based on "
        "the uploaded dataset only. Corrections must not be applied without formal business approval. "
        "The original dataset has not been modified.", muted_style))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def render() -> None:
    st.markdown(page_header("Reports & Exports",
        "Generate and download professional reports for management and audit purposes","📊"),
        unsafe_allow_html=True)

    df = st.session_state.get("active_df")
    analysis = st.session_state.get("analysis_results", {})
    issues = st.session_state.get("quality_issues", [])
    mapping = st.session_state.get("column_mapping", {})
    mandatory = st.session_state.get("mandatory_fields", [])
    fname = st.session_state.get("uploaded_filename","dataset.xlsx")

    if df is None:
        st.markdown(empty_state("📂","No dataset loaded",
            "Upload a workbook using the Data Upload module to generate reports."),
            unsafe_allow_html=True)
        return

    summary = {
        "filename": fname,
        "row_count": len(df),
        "col_count": len(df.columns),
        "overall_completeness": analysis.get("overall_completeness",0),
        "quality_score": analysis.get("quality_score",0),
        "duplicate_count": analysis.get("duplicate_count",0),
    }

    # ── Available reports ─────────────────────────────────────
    reports = [
        ("📊 Data Quality Analysis Report", "Full quality report with metrics, field inventory and issues", "excel_quality"),
        ("📋 Source Data Analysis Report",   "Overview of the uploaded dataset structure and volume",       "excel_quality"),
        ("📖 Data Dictionary Export",        "Detailed field-by-field data dictionary",                     "excel_quality"),
        ("🛠️ Remediation Register",         "Issue register with status and resolution tracking",           "excel_quality"),
        ("💬 Business Clarification Register","Clarifications raised and business decisions recorded",      "excel_quality"),
        ("📋 Consolidated Management Report","Executive summary PDF for management review",                 "pdf"),
    ]

    st.markdown('<div class="section-card"><h3>📄 Available Reports</h3>', unsafe_allow_html=True)
    for label, description, report_type in reports:
        rc1, rc2, rc3 = st.columns([3, 4, 2])
        rc1.markdown(f'<div style="font-weight:600;font-size:.9rem">{label}</div>', unsafe_allow_html=True)
        rc2.markdown(f'<div style="font-size:.8rem;color:var(--color-muted)">{description}</div>', unsafe_allow_html=True)
        with rc3:
            btn_key = f"report_btn_{label[:20]}"
            if st.button("⬇️ Download", key=btn_key, use_container_width=True):
                with st.spinner("Generating report…"):
                    if report_type == "pdf":
                        data = _pdf_summary_report(summary, issues)
                        st.download_button(f"📥 {label}", data=data,
                            file_name=f"hosi_management_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf", key=f"dl_{btn_key}")
                    else:
                        data = _excel_quality_report(df, summary, issues, mapping, mandatory)
                        st.download_button(f"📥 {label}", data=data,
                            file_name=f"hosi_quality_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{btn_key}")
        st.markdown("<hr style='margin:.6rem 0;border-color:var(--color-border)'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick download buttons ────────────────────────────────
    st.markdown('<div class="section-card"><h3>⚡ Quick Downloads</h3>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        excel_data = _excel_quality_report(df, summary, issues, mapping, mandatory)
        st.download_button("📥 Excel Quality Report",
            data=excel_data,
            file_name=f"hosi_quality_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)
    with q2:
        pdf_data = _pdf_summary_report(summary, issues)
        st.download_button("📥 PDF Management Report",
            data=pdf_data,
            file_name=f"hosi_management_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True)
    with q3:
        import io as _io
        buf = _io.StringIO()
        df.to_csv(buf, index=False)
        st.download_button("📥 Raw Data (CSV)",
            data=buf.getvalue().encode(),
            file_name=f"hosi_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
