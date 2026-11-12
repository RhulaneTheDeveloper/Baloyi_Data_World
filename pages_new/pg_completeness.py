"""
pages_new/pg_completeness.py  –  Completeness Assessment (Milestone 3)
"""
from __future__ import annotations
import streamlit as st
from ui.styles import page_header, empty_state, metric_card, progress_bar, badge
import pandas as pd
import plotly.graph_objects as go


def render() -> None:
    st.markdown(page_header("Completeness Analysis",
        "Assess mandatory field completeness across all learner records","✅"), unsafe_allow_html=True)
    df: pd.DataFrame | None = st.session_state.get("active_df")
    if df is None:
        st.markdown(empty_state("📂","No dataset loaded",
            "Upload a workbook using the Data Upload module."), unsafe_allow_html=True)
        return
    total_rows = len(df)
    mandatory = st.session_state.get("mandatory_fields", [])
    mapping = st.session_state.get("column_mapping", {})

    if not mandatory:
        st.info("⚙️ No mandatory fields configured. Go to **Data Upload** → Step 5 to configure mandatory fields.")
        return

    st.markdown('<div class="section-card"><h3>📊 Mandatory Field Completeness</h3>', unsafe_allow_html=True)
    results = []
    total_score_parts = []
    for std_field in mandatory:
        src_col = mapping.get(std_field)
        if src_col and src_col in df.columns:
            series = df[src_col]
            # Count empty: NaN + empty strings + whitespace-only
            is_empty = series.isna() | series.astype(str).str.strip().eq("") | series.astype(str).str.strip().eq("nan")
            missing = int(is_empty.sum())
            filled = total_rows - missing
            pct = round((filled / max(total_rows,1)) * 100, 1)
            total_score_parts.append(pct)
            results.append({"Standardised Field": std_field, "Source Column": src_col,
                "Populated": filled, "Missing": missing, "Completeness %": pct,
                "Status": "✅ Good" if pct >= 95 else "⚠️ Partial" if pct >= 70 else "❌ Poor"})
        else:
            total_score_parts.append(0)
            results.append({"Standardised Field": std_field, "Source Column": "— Not mapped —",
                "Populated": 0, "Missing": total_rows, "Completeness %": 0.0,
                "Status": "❌ Field not found"})

    overall = round(sum(total_score_parts) / max(len(total_score_parts), 1), 1)
    # Update session state for dashboard
    missingness_dict = {r["Standardised Field"]: {"missing_pct": 100-r["Completeness %"],
        "missing_count": r["Missing"], "present_count": r["Populated"]} for r in results}
    analysis = st.session_state.get("analysis_results", {})
    analysis["missingness"] = missingness_dict
    analysis["overall_completeness"] = overall
    st.session_state["analysis_results"] = analysis

    # KPIs
    mc = st.columns(4)
    mc[0].markdown(metric_card("📌", str(len(mandatory)), "Mandatory Fields"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("📊", f"{overall:.1f}%", "Overall Completeness",
        "▲ Good" if overall >= 80 else "⚠ Needs attention",
        "success" if overall >= 80 else "warning"), unsafe_allow_html=True)
    poor = len([r for r in results if r["Completeness %"] < 70])
    mc[2].markdown(metric_card("❌", str(poor), "Fields Below 70%",
        "Action required" if poor else "", "critical" if poor else ""), unsafe_allow_html=True)
    good = len([r for r in results if r["Completeness %"] >= 95])
    mc[3].markdown(metric_card("✅", str(good), "Fields ≥ 95%", "", "success" if good else ""), unsafe_allow_html=True)

    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)

    # Progress bars
    for r in sorted(results, key=lambda x: x["Completeness %"]):
        st.markdown(progress_bar(r["Completeness %"],
            f"{r['Standardised Field']} ({r['Source Column']})"), unsafe_allow_html=True)
    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)

    # Detail table
    res_df = pd.DataFrame(results)
    st.dataframe(res_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Records failing mandatory requirements
    if mapping:
        st.markdown('<div class="section-card"><h3>🚨 Records Failing Mandatory Requirements</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:.8rem;color:var(--color-muted)">Records with at least one missing mandatory field.</p>', unsafe_allow_html=True)
        failing_mask = pd.Series([False] * total_rows, index=df.index)
        for std_field in mandatory:
            src_col = mapping.get(std_field)
            if src_col and src_col in df.columns:
                is_empty = df[src_col].isna() | df[src_col].astype(str).str.strip().eq("") | df[src_col].astype(str).str.strip().eq("nan")
                failing_mask = failing_mask | is_empty
        failing_df = df[failing_mask]
        st.markdown(f'<p style="font-size:.875rem"><strong>{len(failing_df):,}</strong> records have at least one missing mandatory field ({round(len(failing_df)/max(total_rows,1)*100,1)}% of total).</p>', unsafe_allow_html=True)
        if not failing_df.empty:
            st.dataframe(failing_df.head(50), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
