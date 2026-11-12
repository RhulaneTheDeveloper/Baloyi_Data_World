"""
pages_new/pg_dashboard.py
Dashboard page – professional overview with real session data.
"""
from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from ui.styles import (
    badge,
    empty_state,
    metric_card,
    page_header,
    progress_bar,
)


# ─────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────

def _quality_gauge(score: float) -> go.Figure:
    colour = "#16A36A" if score >= 80 else "#F59E0B" if score >= 60 else "#DC2626"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 36, "color": "#202B36"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 11}},
            "bar": {"color": colour, "thickness": 0.28},
            "bgcolor": "#F5F7FA",
            "steps": [
                {"range": [0,  60], "color": "#FEE2E2"},
                {"range": [60, 80], "color": "#FEF3C7"},
                {"range": [80, 100], "color": "#DCFCE7"},
            ],
            "threshold": {
                "line": {"color": colour, "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif"},
    )
    return fig


def _completeness_bar(fields_data: dict) -> go.Figure | None:
    if not fields_data:
        return None
    items = sorted(fields_data.items(), key=lambda x: x[1].get("missing_pct", 0), reverse=True)
    labels = [i[0] for i in items[:12]]
    vals   = [100 - i[1].get("missing_pct", 0) for i in items[:12]]
    colours = ["#16A36A" if v >= 80 else "#F59E0B" if v >= 60 else "#DC2626" for v in vals]

    fig = go.Figure(go.Bar(
        x=vals, y=labels, orientation="h",
        marker_color=colours,
        text=[f"{v:.0f}%" for v in vals],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=max(200, len(labels) * 36),
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(range=[0, 115], showgrid=False, visible=False),
        yaxis=dict(tickfont={"size": 11}),
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif"},
    )
    return fig


def _severity_donut(issues: list[dict]) -> go.Figure | None:
    if not issues:
        return None
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for iss in issues:
        sev = str(iss.get("severity", "Low"))
        counts[sev] = counts.get(sev, 0) + 1
    labels = [k for k, v in counts.items() if v > 0]
    values = [v for v in counts.values() if v > 0]
    colours = {
        "Critical": "#DC2626", "High": "#F59E0B",
        "Medium": "#3B82F6", "Low": "#16A36A",
    }
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker_colors=[colours.get(l, "#73808C") for l in labels],
        textinfo="label+percent",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif"},
    )
    return fig


def _dept_bar(df_col) -> go.Figure | None:
    if df_col is None or df_col.dropna().empty:
        return None
    counts = df_col.value_counts().head(10)
    fig = go.Figure(go.Bar(
        x=counts.values.tolist(),
        y=counts.index.tolist(),
        orientation="h",
        marker_color="#142B3B",
        hovertemplate="%{y}: %{x}<extra></extra>",
    ))
    fig.update_layout(
        height=max(200, len(counts) * 32),
        margin=dict(l=10, r=30, t=10, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(tickfont={"size": 11}),
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif"},
    )
    return fig


# ─────────────────────────────────────────────────────────────
# main render
# ─────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        page_header(
            "Dashboard",
            "Real-time overview of your data analysis workstream",
            "🏠",
        ),
        unsafe_allow_html=True,
    )

    wb       = st.session_state.get("workbook")
    analysis = st.session_state.get("analysis_results", {})
    issues   = st.session_state.get("quality_issues", [])
    missingness = analysis.get("missingness", {})

    # ── Empty state ──────────────────────────────────────────
    if wb is None:
        st.markdown(
            empty_state(
                "📊",
                "No dataset loaded",
                "Upload an Excel workbook using the Data Upload module to begin your analysis. "
                "Your dashboard will populate automatically once a file has been processed.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("<div class='section-sep'></div>", unsafe_allow_html=True)

        # Render informational cards to show what's coming
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                """<div class="section-card">
                    <h3>📋 What you can analyse</h3>
                    <ul style="font-size:.875rem;color:#73808C;line-height:1.9">
                        <li>Learner record completeness</li>
                        <li>Duplicate learner identifiers</li>
                        <li>Invalid emails & dates</li>
                        <li>Naming & format consistency</li>
                        <li>Department distribution</li>
                    </ul>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """<div class="section-card">
                    <h3>📁 Supported file types</h3>
                    <ul style="font-size:.875rem;color:#73808C;line-height:1.9">
                        <li>.xlsx – Excel Workbook</li>
                        <li>.xls – Legacy Excel</li>
                        <li>.xlsm – Macro-enabled Excel</li>
                    </ul>
                    <p style="font-size:.8rem;color:#73808C;margin-top:.5rem">
                        Max file size: 50 MB
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                """<div class="section-card">
                    <h3>📊 Reports available</h3>
                    <ul style="font-size:.875rem;color:#73808C;line-height:1.9">
                        <li>Source Data Analysis</li>
                        <li>Completeness Assessment</li>
                        <li>Data Quality Report</li>
                        <li>Remediation Register</li>
                        <li>Technical Readiness</li>
                        <li>Consolidated Management Report</li>
                    </ul>
                </div>""",
                unsafe_allow_html=True,
            )
        return

    # ── Data is loaded – live dashboard ─────────────────────
    row_count      = wb.get("row_count", 0)
    col_count      = wb.get("column_count", 0)
    dup_count      = analysis.get("duplicate_count", 0)
    quality_score  = analysis.get("quality_score", 0.0)
    overall_comp   = analysis.get("overall_completeness", 0.0)
    resolved       = len([i for i in issues if str(i.get("status","")).lower() == "resolved"])
    outstanding    = len([i for i in issues if str(i.get("status","")).lower() != "resolved"])
    fname          = st.session_state.get("uploaded_filename", "—")
    last_run       = st.session_state.get("last_analysis_time", "—")

    # ── KPI strip ───────────────────────────────────────────
    cols = st.columns(4)
    kpis = [
        ("📋", f"{row_count:,}", "Total Records", "", ""),
        ("🗂️", str(col_count), "Fields Identified", "", ""),
        ("📊", f"{overall_comp:.1f}%", "Overall Completeness",
         "▲ Good" if overall_comp >= 80 else "⚠ Needs attention", "success" if overall_comp >= 80 else "warning"),
        ("🔁", f"{dup_count:,}", "Duplicate Records",
         "✓ No duplicates" if dup_count == 0 else "Review required",
         "" if dup_count == 0 else "warning"),
    ]
    for col, (icon, val, label, delta, variant) in zip(cols, kpis):
        with col:
            st.markdown(metric_card(icon, val, label, delta, variant), unsafe_allow_html=True)

    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    kpis2 = [
        ("🔍", f"{len(issues):,}", "Issues Detected", "", "warning" if issues else ""),
        ("✅", f"{resolved:,}",    "Resolved Issues", "", "success"),
        ("⏳", f"{outstanding:,}", "Outstanding Issues", "", "critical" if outstanding > 0 else ""),
        ("📁", fname[:22] + "…" if len(fname) > 22 else fname, "Dataset", f"Analysed: {last_run}", ""),
    ]
    for col, (icon, val, label, delta, variant) in zip(cols2, kpis2):
        with col:
            st.markdown(metric_card(icon, val, label, delta, variant), unsafe_allow_html=True)

    st.markdown("<div style='margin:1rem 0'></div>", unsafe_allow_html=True)

    # ── Charts row 1 ────────────────────────────────────────
    left, right = st.columns([1, 2])

    with left:
        st.markdown('<div class="section-card"><h3>📊 Data Quality Score</h3>', unsafe_allow_html=True)
        fig_gauge = _quality_gauge(quality_score)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
        q_label = "Excellent" if quality_score >= 85 else "Good" if quality_score >= 70 else "Needs Work" if quality_score >= 50 else "Poor"
        q_variant = "success" if quality_score >= 70 else "warning" if quality_score >= 50 else "critical"
        st.markdown(
            f'<div style="text-align:center;margin-top:-.5rem;padding-bottom:.5rem">'
            f'{badge(q_label, q_variant)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card"><h3>✅ Completeness by Field</h3>', unsafe_allow_html=True)
        fig_comp = _completeness_bar(missingness)
        if fig_comp:
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown(
                '<p style="color:var(--color-muted);font-size:.875rem;padding:.5rem 0">'
                'Run a completeness analysis to see field-level data.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts row 2 ────────────────────────────────────────
    left2, right2 = st.columns([1, 2])

    with left2:
        st.markdown('<div class="section-card"><h3>⚠️ Issue Severity</h3>', unsafe_allow_html=True)
        fig_sev = _severity_donut(issues)
        if fig_sev:
            st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown(
                '<p style="color:var(--color-muted);font-size:.875rem;padding:.5rem 0">'
                'No quality issues detected yet. Run the Data Quality module.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right2:
        # Department distribution (if available)
        df = st.session_state.get("active_df")
        dept_col = None
        if df is not None:
            for col in df.columns:
                if any(k in col.lower() for k in ("department", "dept", "business_unit", "unit")):
                    dept_col = df[col]
                    break

        st.markdown('<div class="section-card"><h3>🏢 Department Distribution</h3>', unsafe_allow_html=True)
        fig_dept = _dept_bar(dept_col)
        if fig_dept:
            st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown(
                '<p style="color:var(--color-muted);font-size:.875rem;padding:.5rem 0">'
                'No department / business unit field detected in this dataset.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Recent activity ─────────────────────────────────────
    act_left, act_right = st.columns(2)

    with act_left:
        st.markdown('<div class="section-card"><h3>🕐 Recent Analysis Activity</h3>', unsafe_allow_html=True)
        history = st.session_state.get("analysis_history", [])
        if history:
            for entry in history[-5:][::-1]:
                st.markdown(
                    f"""<div class="info-row">
                      <span class="info-label">{entry.get('timestamp','—')}</span>
                      <span class="info-value">{entry.get('filename','—')}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p style="color:var(--color-muted);font-size:.875rem">'
                'No previous analysis sessions found.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with act_right:
        st.markdown('<div class="section-card"><h3>🛠️ Recent Remediation Activity</h3>', unsafe_allow_html=True)
        recent_rem = [i for i in issues if i.get("status")][:5]
        if recent_rem:
            for item in recent_rem:
                sev = str(item.get("severity", "Low"))
                sev_v = "critical" if sev == "Critical" else "warning" if sev in ("High","Medium") else "muted"
                st.markdown(
                    f"""<div class="info-row">
                      <span class="info-label">{badge(sev, sev_v)}</span>
                      <span class="info-value" style="font-size:.8rem">{str(item.get('issue',''))[:55]}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p style="color:var(--color-muted);font-size:.875rem">'
                'No remediation actions recorded yet.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
