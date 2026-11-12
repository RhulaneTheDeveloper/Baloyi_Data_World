"""
pages_new/pg_scope.py
Scope & Volume Analysis module.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.styles import badge, empty_state, metric_card, page_header, progress_bar


def _completeness_pct(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    total_cells = df.size
    filled_cells = df.notna().sum().sum()
    pct = (filled_cells / total_cells) * 100 if total_cells else 0.0
    return round(pct, 2)


def _empty_rows(df: pd.DataFrame) -> int:
    return int(df.isna().all(axis=1).sum())


def _empty_cols(df: pd.DataFrame) -> int:
    return int(df.isna().all(axis=0).sum())


def _exact_duplicates(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def _col_type_chart(df: pd.DataFrame) -> go.Figure:
    type_counts: dict[str, int] = {}
    for dtype in df.dtypes:
        label = "Numeric" if pd.api.types.is_numeric_dtype(dtype) else \
                "Date/Time" if pd.api.types.is_datetime64_any_dtype(dtype) else "Text"
        type_counts[label] = type_counts.get(label, 0) + 1
    colours = {"Numeric": "#16A36A", "Date/Time": "#3B82F6", "Text": "#142B3B"}
    fig = go.Figure(go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=0.55,
        marker_colors=[colours.get(k, "#73808C") for k in type_counts],
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} columns<extra></extra>",
    ))
    fig.update_layout(
        height=240, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, paper_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif"},
    )
    return fig


def render() -> None:
    st.markdown(
        page_header(
            "Scope & Volume Analysis",
            "Assess the total scope, structure and volume of the uploaded dataset",
            "🔭",
        ),
        unsafe_allow_html=True,
    )

    df: pd.DataFrame | None = st.session_state.get("active_df")
    wb = st.session_state.get("workbook")

    if df is None or wb is None:
        st.markdown(
            empty_state("📂", "No dataset loaded",
                        "Upload a workbook using the Data Upload module to run scope analysis."),
            unsafe_allow_html=True,
        )
        return

    # ── Core metrics ─────────────────────────────────────────
    total_rows       = len(df)
    total_cols       = len(df.columns)
    sheet_count      = wb.get("sheet_count", 1)
    sheet_names      = wb.get("sheet_names", [])
    empty_row_count  = _empty_rows(df)
    empty_col_count  = _empty_cols(df)
    exact_dups       = _exact_duplicates(df)
    overall_comp     = _completeness_pct(df)
    id_col           = st.session_state.get("id_column", "")
    unique_ids       = df[id_col].nunique() if id_col and id_col in df.columns else 0

    st.markdown('<div class="section-card"><h3>📊 Volume Summary</h3>', unsafe_allow_html=True)
    mc = st.columns(4)
    mc[0].markdown(metric_card("📋", f"{total_rows:,}",    "Total Records"),        unsafe_allow_html=True)
    mc[1].markdown(metric_card("🗂️", str(total_cols),      "Total Fields"),         unsafe_allow_html=True)
    mc[2].markdown(metric_card("📄", str(sheet_count),     "Worksheets"),           unsafe_allow_html=True)
    mc[3].markdown(metric_card("🔑", f"{unique_ids:,}",    "Unique Identifiers"),   unsafe_allow_html=True)
    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)
    mc2 = st.columns(4)
    mc2[0].markdown(metric_card("🗑️", str(empty_row_count), "Empty Rows",   "Remove before import" if empty_row_count else "", "warning" if empty_row_count else ""), unsafe_allow_html=True)
    mc2[1].markdown(metric_card("🗑️", str(empty_col_count), "Empty Columns","Remove before import" if empty_col_count else "", "warning" if empty_col_count else ""), unsafe_allow_html=True)
    mc2[2].markdown(metric_card("🔁", str(exact_dups),       "Exact Duplicates","Review required" if exact_dups else "✓ None", "critical" if exact_dups else "success"), unsafe_allow_html=True)
    mc2[3].markdown(metric_card("📊", f"{overall_comp:.1f}%","Data Completeness",
                                "▲ Good" if overall_comp >= 80 else "⚠ Needs attention",
                                "success" if overall_comp >= 80 else "warning"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Records per sheet ────────────────────────────────────
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown('<div class="section-card"><h3>📄 Records per Worksheet</h3>', unsafe_allow_html=True)
        rps = wb.get("records_per_sheet", {})
        if rps:
            rps_df = pd.DataFrame([
                {"Worksheet": name, "Records": cnt,
                 "% of Total": f"{(cnt/max(total_rows,1))*100:.1f}%"}
                for name, cnt in rps.items()
            ])
            st.dataframe(rps_df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p style="color:var(--color-muted);font-size:.875rem">No sheet breakdown available.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-card"><h3>🗂️ Column Type Distribution</h3>', unsafe_allow_html=True)
        st.plotly_chart(_col_type_chart(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Column inventory ─────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📋 Field Inventory</h3>', unsafe_allow_html=True)
    mapping = st.session_state.get("column_mapping", {})
    reverse_map = {v: k for k, v in mapping.items()}
    mandatory = st.session_state.get("mandatory_fields", [])

    inventory_rows = []
    for col in df.columns:
        series = df[col]
        filled = series.notna().sum()
        pct = round((filled / max(total_rows, 1)) * 100, 1)
        std_name = reverse_map.get(col, "")
        is_mand = std_name in mandatory if std_name else False
        dtype_label = (
            "Numeric" if pd.api.types.is_numeric_dtype(series.dtype) else
            "Date/Time" if pd.api.types.is_datetime64_any_dtype(series.dtype) else "Text"
        )
        inventory_rows.append({
            "Source Column":      col,
            "Standardised Field": std_name or "—",
            "Data Type":          dtype_label,
            "Populated":          int(filled),
            "Missing":            int(total_rows - filled),
            "Completeness":       f"{pct}%",
            "Mandatory":          "✅ Yes" if is_mand else "○ No",
            "Unique Values":      int(series.nunique(dropna=True)),
        })

    inv_df = pd.DataFrame(inventory_rows)
    st.dataframe(inv_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Date range analysis ───────────────────────────────────
    date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns.tolist()
    # Also try to detect date-like string columns
    for col in df.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            if parsed.notna().sum() / max(len(df), 1) > 0.5:
                date_cols.append(col)
        except Exception:
            pass

    if date_cols:
        st.markdown('<div class="section-card"><h3>📅 Date Range Coverage</h3>', unsafe_allow_html=True)
        date_rows = []
        for col in date_cols[:6]:
            parsed = pd.to_datetime(df[col], errors="coerce")
            valid = parsed.dropna()
            if valid.empty:
                continue
            date_rows.append({
                "Field":    col,
                "Earliest": valid.min().strftime("%d %b %Y"),
                "Latest":   valid.max().strftime("%d %b %Y"),
                "Span (days)": (valid.max() - valid.min()).days,
                "Invalid":  int(len(df) - len(valid)),
            })
        if date_rows:
            st.dataframe(pd.DataFrame(date_rows), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Department / Status breakdown ─────────────────────────
    for col in df.columns:
        col_lower = col.lower()
        if any(k in col_lower for k in ("department", "dept", "business_unit", "status", "learner_status")):
            counts = df[col].value_counts(dropna=False)
            if 1 < len(counts) <= 40:
                st.markdown(f'<div class="section-card"><h3>📊 Breakdown by: {col}</h3>', unsafe_allow_html=True)
                fig = go.Figure(go.Bar(
                    x=counts.index.astype(str).tolist(),
                    y=counts.values.tolist(),
                    marker_color="#142B3B",
                    hovertemplate="%{x}: %{y}<extra></extra>",
                ))
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=10, b=60),
                    xaxis=dict(tickangle=-30, tickfont={"size": 10}),
                    paper_bgcolor="white", plot_bgcolor="white",
                    font={"family": "Inter, Segoe UI, sans-serif"},
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Export button ─────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>⬇️ Export Scope Assessment</h3>', unsafe_allow_html=True)
    if st.button("Download Scope Assessment (CSV)"):
        import io as _io
        buf = _io.StringIO()
        inv_df.to_csv(buf, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=buf.getvalue().encode(),
            file_name=f"scope_assessment_{st.session_state.get('uploaded_filename','dataset').rsplit('.',1)[0]}.csv",
            mime="text/csv",
        )
    st.markdown("</div>", unsafe_allow_html=True)
