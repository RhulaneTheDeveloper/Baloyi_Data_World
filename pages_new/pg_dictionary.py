"""
pages_new/pg_dictionary.py
Data Dictionary & Structure Analysis module.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.styles import badge, empty_state, metric_card, page_header


def _safe_samples(series: pd.Series, n: int = 5) -> str:
    """Return a safe preview string – no PII exposure in logs."""
    vals = series.dropna().head(n).astype(str).tolist()
    return " · ".join(vals) if vals else "—"


def _field_type_label(dtype) -> str:
    if pd.api.types.is_numeric_dtype(dtype):
        return "Numeric"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "Date / Time"
    if pd.api.types.is_bool_dtype(dtype):
        return "Boolean"
    return "Text"


def _possible_relationships(df: pd.DataFrame) -> list[dict]:
    """Heuristically detect possible FK-like relationships between columns."""
    hints: list[dict] = []
    id_cols = [c for c in df.columns if any(k in c.lower() for k in ("id", "number", "code"))]
    text_cols = [c for c in df.select_dtypes(include="object").columns if c not in id_cols]
    for id_col in id_cols[:5]:
        for txt_col in text_cols[:8]:
            if id_col == txt_col:
                continue
            try:
                corr_ratio = df[[id_col, txt_col]].dropna().groupby(id_col)[txt_col].nunique().mean()
                if 0.9 <= corr_ratio <= 1.1:
                    hints.append({"Field A": id_col, "Field B": txt_col,
                                  "Relationship": "Possible 1:1 mapping"})
            except Exception:
                pass
    return hints[:10]


def render() -> None:
    st.markdown(
        page_header(
            "Data Dictionary",
            "Detailed profile of every field in the dataset including types, completeness and sample values",
            "📖",
        ),
        unsafe_allow_html=True,
    )

    df: pd.DataFrame | None = st.session_state.get("active_df")
    if df is None:
        st.markdown(
            empty_state("📂", "No dataset loaded",
                        "Upload a workbook using the Data Upload module to generate the data dictionary."),
            unsafe_allow_html=True,
        )
        return

    total_rows = len(df)
    mapping    = st.session_state.get("column_mapping", {})
    reverse_map = {v: k for k, v in mapping.items()}
    mandatory  = st.session_state.get("mandatory_fields", [])

    # ── Summary metrics ───────────────────────────────────────
    text_cols  = df.select_dtypes(include="object").shape[1]
    num_cols   = df.select_dtypes(include="number").shape[1]
    date_cols  = df.select_dtypes(include=["datetime64"]).shape[1]
    mapped_cnt = len(mapping)

    st.markdown('<div class="section-card"><h3>📊 Field Summary</h3>', unsafe_allow_html=True)
    mc = st.columns(5)
    mc[0].markdown(metric_card("🗂️", str(len(df.columns)), "Total Fields"),        unsafe_allow_html=True)
    mc[1].markdown(metric_card("🔤", str(text_cols),       "Text Fields"),          unsafe_allow_html=True)
    mc[2].markdown(metric_card("🔢", str(num_cols),        "Numeric Fields"),       unsafe_allow_html=True)
    mc[3].markdown(metric_card("📅", str(date_cols),       "Date/Time Fields"),     unsafe_allow_html=True)
    mc[4].markdown(metric_card("🔄", str(mapped_cnt),      "Mapped Fields"),        unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Filter controls ───────────────────────────────────────
    st.markdown('<div class="section-card"><h3>🔍 Field Search & Filter</h3>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        search_term = st.text_input("Search fields", placeholder="Type a field name…", label_visibility="collapsed")
    with fc2:
        type_filter = st.selectbox("Filter by type", ["All types", "Text", "Numeric", "Date / Time"], label_visibility="collapsed")
    with fc3:
        mand_filter = st.selectbox("Mandatory", ["All", "Mandatory only", "Optional only"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Build dictionary ──────────────────────────────────────
    dict_rows = []
    for col in df.columns:
        series = df[col]
        filled = int(series.notna().sum())
        missing = total_rows - filled
        pct = round((filled / max(total_rows, 1)) * 100, 1)
        std_name = reverse_map.get(col, "")
        is_mand = std_name in mandatory if std_name else False
        type_label = _field_type_label(series.dtype)
        unique_cnt = int(series.nunique(dropna=True))

        # Validation status
        if pct >= 95:
            val_status = "✅ Good"
        elif pct >= 70:
            val_status = "⚠️ Partial"
        else:
            val_status = "❌ Poor"

        dict_rows.append({
            "Source Column":      col,
            "Standardised Field": std_name or "—",
            "Data Type":          type_label,
            "Populated":          filled,
            "Missing":            missing,
            "Completeness %":     pct,
            "Unique Values":      unique_cnt,
            "Sample Values":      _safe_samples(series),
            "Classification":     "Mandatory" if is_mand else "Optional",
            "Validation Status":  val_status,
        })

    dict_df = pd.DataFrame(dict_rows)

    # Apply filters
    if search_term:
        mask = dict_df["Source Column"].str.contains(search_term, case=False, na=False) | \
               dict_df["Standardised Field"].str.contains(search_term, case=False, na=False)
        dict_df = dict_df[mask]
    if type_filter != "All types":
        dict_df = dict_df[dict_df["Data Type"] == type_filter]
    if mand_filter == "Mandatory only":
        dict_df = dict_df[dict_df["Classification"] == "Mandatory"]
    elif mand_filter == "Optional only":
        dict_df = dict_df[dict_df["Classification"] == "Optional"]

    # ── Main dictionary table ─────────────────────────────────
    st.markdown('<div class="section-card"><h3>📖 Data Dictionary</h3>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:.8rem;color:var(--color-muted)">Showing {len(dict_df)} of {len(df.columns)} fields</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        dict_df.style.apply(
            lambda row: [
                "background-color:#FEF3C7" if "⚠️" in str(row["Validation Status"]) else
                "background-color:#FEE2E2" if "❌" in str(row["Validation Status"]) else
                ""
            ] * len(row),
            axis=1,
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Field deep-dive ───────────────────────────────────────
    st.markdown('<div class="section-card"><h3>🔎 Field Detail Inspector</h3>', unsafe_allow_html=True)
    selected_field = st.selectbox("Select a field to inspect", df.columns.tolist(), label_visibility="visible")
    if selected_field:
        series = df[selected_field]
        filled = series.notna().sum()
        pct = round((filled / max(total_rows, 1)) * 100, 1)
        type_label = _field_type_label(series.dtype)
        unique_cnt = series.nunique(dropna=True)

        di_c1, di_c2 = st.columns(2)
        with di_c1:
            st.markdown(f"""
            <div style="font-size:.875rem;line-height:2">
                <div class="info-row"><span class="info-label">Source Column</span><span class="info-value">{selected_field}</span></div>
                <div class="info-row"><span class="info-label">Standardised Name</span><span class="info-value">{reverse_map.get(selected_field,'—')}</span></div>
                <div class="info-row"><span class="info-label">Data Type</span><span class="info-value">{type_label}</span></div>
                <div class="info-row"><span class="info-label">Total Records</span><span class="info-value">{total_rows:,}</span></div>
                <div class="info-row"><span class="info-label">Populated</span><span class="info-value">{int(filled):,}</span></div>
                <div class="info-row"><span class="info-label">Missing</span><span class="info-value">{total_rows - int(filled):,}</span></div>
                <div class="info-row"><span class="info-label">Unique Values</span><span class="info-value">{int(unique_cnt):,}</span></div>
                <div class="info-row"><span class="info-label">Completeness</span><span class="info-value">{pct:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)

        with di_c2:
            # Value distribution for low-cardinality text fields
            if type_label == "Text" and unique_cnt <= 30:
                counts = series.value_counts(dropna=False).head(15)
                labels = [str(x) if str(x) != "nan" else "(missing)" for x in counts.index]
                fig = go.Figure(go.Bar(
                    x=counts.values.tolist(), y=labels, orientation="h",
                    marker_color="#142B3B",
                    hovertemplate="%{y}: %{x}<extra></extra>",
                ))
                fig.update_layout(
                    height=max(180, len(labels)*28),
                    margin=dict(l=10, r=30, t=10, b=10),
                    xaxis=dict(showgrid=False),
                    paper_bgcolor="white", plot_bgcolor="white",
                    font={"family": "Inter, Segoe UI, sans-serif"},
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            elif type_label == "Numeric":
                fig = go.Figure(go.Histogram(
                    x=series.dropna().tolist(),
                    marker_color="#16A36A",
                    nbinsx=20,
                ))
                fig.update_layout(
                    height=220,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="white", plot_bgcolor="white",
                    font={"family": "Inter, Segoe UI, sans-serif"},
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown(
                    f'<p style="color:var(--color-muted);font-size:.875rem;padding-top:.5rem">'
                    f'High-cardinality field ({unique_cnt:,} unique values). '
                    f'Sample values:<br><code>{_safe_samples(series, 8)}</code></p>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Possible relationships ────────────────────────────────
    rels = _possible_relationships(df)
    if rels:
        st.markdown('<div class="section-card"><h3>🔗 Possible Field Relationships</h3>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:.8rem;color:var(--color-muted)">These are automatically detected heuristic hints, '
            'not confirmed relationships. Verify with the data owner.</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(pd.DataFrame(rels), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────
    st.markdown('<div class="section-card"><h3>⬇️ Export Data Dictionary</h3>', unsafe_allow_html=True)
    import io as _io
    buf = _io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame(dict_rows).to_excel(writer, sheet_name="Data Dictionary", index=False)
        ws = writer.sheets["Data Dictionary"]
        ws.set_column(0, 10, 22)
    buf.seek(0)
    st.download_button(
        label="📥 Download Data Dictionary (Excel)",
        data=buf.getvalue(),
        file_name=f"data_dictionary_{st.session_state.get('uploaded_filename','dataset').rsplit('.',1)[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.markdown("</div>", unsafe_allow_html=True)
