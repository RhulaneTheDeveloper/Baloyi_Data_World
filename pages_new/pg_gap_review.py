"""
pages_new/pg_gap_review.py
Post-upload data gap review and remediation summary.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.styles import empty_state, metric_card, page_header


def _series_empty_flags(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series([], dtype=bool)
    return series.isna() | series.astype(str).str.strip().eq("") | series.astype(str).str.strip().eq("nan")


def render() -> None:
    st.markdown(
        page_header(
            "Data Gap Review",
            "Review gaps, cleansing needs, business interpretation items and quality issues after upload",
            "🧭",
        ),
        unsafe_allow_html=True,
    )

    df: pd.DataFrame | None = st.session_state.get("active_df")
    if df is None:
        st.markdown(
            empty_state(
                "📂",
                "No dataset loaded",
                "Upload a workbook using the Data Upload page to review the data gap register.",
            ),
            unsafe_allow_html=True,
        )
        return

    mapping = st.session_state.get("column_mapping", {})
    mandatory = st.session_state.get("mandatory_fields", [])
    issues = st.session_state.get("quality_issues", [])
    analysis = st.session_state.get("analysis_results", {})
    id_col = st.session_state.get("id_column", "")

    total_rows = len(df)
    total_cols = len(df.columns)
    missing_total = int(df.isna().sum().sum())
    dup_total = int(df.duplicated(subset=[id_col]).sum()) if id_col and id_col in df.columns else 0
    quality_score = float(analysis.get("quality_score", 0.0) or 0.0)
    completeness = float(analysis.get("overall_completeness", 0.0) or 0.0)

    st.markdown('<div class="section-card"><h3>📊 Review Summary</h3>', unsafe_allow_html=True)
    metrics = st.columns(5)
    metrics[0].markdown(metric_card("📋", f"{total_rows:,}", "Records"), unsafe_allow_html=True)
    metrics[1].markdown(metric_card("🗂️", str(total_cols), "Fields"), unsafe_allow_html=True)
    metrics[2].markdown(metric_card("❌", str(missing_total), "Missing Cells"), unsafe_allow_html=True)
    metrics[3].markdown(metric_card("🔁", str(dup_total), "Duplicate Records"), unsafe_allow_html=True)
    metrics[4].markdown(metric_card("📈", f"{quality_score:.1f}%", "Quality Score"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Data gaps register
    st.markdown('<div class="section-card"><h3>🚨 Data Gaps and Quality Issues</h3>', unsafe_allow_html=True)
    gap_rows = []
    for std_field in mandatory:
        src_col = mapping.get(std_field)
        if src_col and src_col in df.columns:
            empties = _series_empty_flags(df[src_col])
            count = int(empties.sum())
            pct = round((count / max(total_rows, 1)) * 100, 1)
            gap_rows.append({
                "Field": src_col,
                "Standardised": std_field,
                "Missing": count,
                "% Missing": pct,
                "Priority": "Critical" if pct >= 30 else "High" if pct >= 15 else "Medium" if pct >= 5 else "Low",
            })

    if not gap_rows:
        st.info("No mandatory field gaps were identified for the current mapping.")
    else:
        st.dataframe(pd.DataFrame(gap_rows).sort_values("% Missing", ascending=False), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Business interpretation / clarification
    st.markdown('<div class="section-card"><h3>🧠 Information Requiring Business Interpretation</h3>', unsafe_allow_html=True)
    biz_rows = []
    for col in df.columns:
        non_null = df[col].dropna()
        if non_null.empty:
            continue
        unique_count = non_null.astype(str).nunique(dropna=True)
        if unique_count > 0 and unique_count <= 10 and len(non_null) > 0:
            sample_vals = ", ".join(str(v) for v in non_null.astype(str).drop_duplicates().head(5).tolist())
            biz_rows.append({
                "Field": col,
                "Distinct Values": unique_count,
                "Example Values": sample_vals,
                "Business Review": "Review code definitions and approved value set" if unique_count <= 8 else "Confirm interpretation with business owner",
            })

    if not biz_rows:
        st.success("No obvious business interpretation items were detected in the current dataset.")
    else:
        st.dataframe(pd.DataFrame(biz_rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Records needing cleansing or clarification
    st.markdown('<div class="section-card"><h3>🧹 Records Requiring Cleansing or Business Clarification</h3>', unsafe_allow_html=True)
    cleanse_candidates = []

    if id_col and id_col in df.columns:
        duplicate_mask = df[id_col].duplicated(keep=False)
        cleanse_candidates.append(df.loc[duplicate_mask, :].copy())

    mandatory_mask = pd.Series(False, index=df.index)
    for std in mandatory:
        src = mapping.get(std)
        if src and src in df.columns:
            mandatory_mask = mandatory_mask | _series_empty_flags(df[src])
    if mandatory_mask.any():
        cleanse_candidates.append(df.loc[mandatory_mask, :].copy())

    if issues:
        issue_idx = []
        for item in issues:
            field = item.get("field")
            if field and field in df.columns:
                issue_idx.extend(df.index[df[field].astype(str).eq(str(item.get("original_value")))].tolist())
        if issue_idx:
            cleanse_candidates.append(df.loc[list(dict.fromkeys(issue_idx)), :].copy())

    all_candidates = pd.concat(cleanse_candidates, ignore_index=True) if cleanse_candidates else pd.DataFrame(columns=df.columns)
    if all_candidates.empty:
        st.success("No records currently need cleansing or clarification based on the detected quality rules.")
    else:
        deduped = all_candidates.drop_duplicates().head(100)
        st.dataframe(deduped, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Format, naming conventions and field consistency
    st.markdown('<div class="section-card"><h3>🧾 Format, Naming Convention and Field Consistency Review</h3>', unsafe_allow_html=True)
    summary_rows = []
    for col in df.columns:
        series = df[col].dropna().astype(str)
        if series.empty:
            continue
        mixed_case = series.str.contains(r"[a-z][A-Z]|")
        space_issue = series.str.contains(r"\s{2,}")
        summary_rows.append({
            "Field": col,
            "Sample Values": series.head(3).str.cat(sep=" | "),
            "Mixed Case": bool(mixed_case.any()),
            "Extra Spaces": bool(space_issue.any()),
            "Review": "Standardise naming and formatting" if bool(mixed_case.any()) or bool(space_issue.any()) else "Consistent",
        })
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Available fields, structures and scope
    st.markdown('<div class="section-card"><h3>📚 Available Fields and Dataset Structure</h3>', unsafe_allow_html=True)
    field_inventory = pd.DataFrame({
        "Field": df.columns,
        "Data Type": [str(df[col].dtype) for col in df.columns],
        "Populated": [int(df[col].notna().sum()) for col in df.columns],
        "Missing": [int(df[col].isna().sum()) for col in df.columns],
        "Mandatory": ["Yes" if col in [mapping.get(m) for m in mandatory if mapping.get(m)] else "No" for col in df.columns],
    })
    st.dataframe(field_inventory, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Scope and volume summary
    st.markdown('<div class="section-card"><h3>🔭 Scope and Volume</h3>', unsafe_allow_html=True)
    scope_rows = [
        {"Dimension": "Records", "Value": f"{total_rows:,}"},
        {"Dimension": "Fields", "Value": str(total_cols)},
        {"Dimension": "Mandatory Fields", "Value": str(len(mandatory))},
        {"Dimension": "Completeness", "Value": f"{completeness:.1f}%"},
        {"Dimension": "Duplicate Records", "Value": str(dup_total)},
        {"Dimension": "Data Gaps", "Value": str(missing_total)},
    ]
    st.dataframe(pd.DataFrame(scope_rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
