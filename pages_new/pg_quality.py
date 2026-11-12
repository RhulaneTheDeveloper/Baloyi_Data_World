"""
pages_new/pg_quality.py  –  Data Quality Analysis (Milestone 3)
"""
from __future__ import annotations
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui.styles import page_header, empty_state, metric_card, badge

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def _check_emails(df, col):
    vals = df[col].dropna().astype(str).str.strip()
    invalid = vals[vals != ""].apply(lambda v: not bool(EMAIL_RE.match(v)))
    return invalid[invalid].index.tolist()


def _check_duplicates(df, id_col):
    if not id_col or id_col not in df.columns:
        return pd.DataFrame()
    return df[df[id_col].duplicated(keep=False)].copy()


def _check_inconsistent_values(df, col, max_unique=40):
    """Return suspicious value variants (case/spacing inconsistencies)."""
    if col not in df.columns:
        return []
    vals = df[col].dropna().astype(str).str.strip()
    lower_groups: dict[str, list[str]] = {}
    for v in vals.unique():
        lower_groups.setdefault(v.lower(), []).append(v)
    return [(k, variants) for k, variants in lower_groups.items() if len(variants) > 1]


def render() -> None:
    st.markdown(page_header("Data Quality Analysis",
        "Detect duplicates, inconsistencies, invalid values and missing information", "🔍"),
        unsafe_allow_html=True)

    df: pd.DataFrame | None = st.session_state.get("active_df")
    if df is None:
        st.markdown(empty_state("📂","No dataset loaded",
            "Upload a workbook using the Data Upload module."), unsafe_allow_html=True)
        return

    total_rows = len(df)
    id_col = st.session_state.get("id_column","")
    mapping = st.session_state.get("column_mapping", {})
    issues: list[dict] = []
    invalid_email_idx: list = []  # populated below if email field exists

    # ── Duplicate detection ───────────────────────────────────
    st.markdown('<div class="section-card"><h3>🔁 Duplicate Detection</h3>', unsafe_allow_html=True)
    exact_dups = df[df.duplicated(keep=False)]
    id_dups    = _check_duplicates(df, id_col)
    email_col  = mapping.get("email","")
    email_dups = pd.DataFrame()
    if email_col and email_col in df.columns:
        email_dups = df[df[email_col].duplicated(keep=False) & df[email_col].notna()]

    mc = st.columns(3)
    mc[0].markdown(metric_card("🔁", str(len(exact_dups)), "Exact Duplicate Rows",
        "Review required" if len(exact_dups) else "✓ None",
        "critical" if len(exact_dups) else "success"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("🔑", str(len(id_dups)), "Duplicate Learner IDs",
        f"on field: {id_col}" if id_col else "No ID field",
        "critical" if len(id_dups) else "success"), unsafe_allow_html=True)
    mc[2].markdown(metric_card("📧", str(len(email_dups)), "Duplicate Emails",
        f"on field: {email_col}" if email_col else "No email field",
        "warning" if len(email_dups) else "success"), unsafe_allow_html=True)

    if not exact_dups.empty:
        with st.expander(f"View {len(exact_dups)} exact duplicate rows"):
            st.dataframe(exact_dups.head(100), use_container_width=True, hide_index=True)
        for _, row in exact_dups.head(20).iterrows():
            issues.append({"issue": "Exact duplicate row", "severity": "High",
                "field": "—", "original_value": "—", "status": "Open"})

    if not id_dups.empty:
        with st.expander(f"View {len(id_dups)} duplicate learner ID records"):
            st.dataframe(id_dups.head(100), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Invalid email check ───────────────────────────────────
    st.markdown('<div class="section-card"><h3>📧 Email Validation</h3>', unsafe_allow_html=True)
    if email_col and email_col in df.columns:
        invalid_email_idx = _check_emails(df, email_col)
        st.markdown(metric_card("📧", str(len(invalid_email_idx)), "Invalid Email Addresses",
            "Action required" if invalid_email_idx else "✓ All valid",
            "critical" if invalid_email_idx else "success"), unsafe_allow_html=True)
        if invalid_email_idx:
            invalid_email_df = df.loc[invalid_email_idx][[col for col in [id_col, email_col] if col and col in df.columns]]
            with st.expander(f"View {len(invalid_email_idx)} invalid email records"):
                st.dataframe(invalid_email_df.head(100), use_container_width=True, hide_index=True)
            for idx in invalid_email_idx[:50]:
                issues.append({"issue": "Invalid email format", "severity": "Medium",
                    "field": email_col, "original_value": str(df.loc[idx, email_col]), "status": "Open"})
    else:
        st.info("No email field mapped. Go to Data Upload to map the email column.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Inconsistency detection ───────────────────────────────
    st.markdown('<div class="section-card"><h3>⚡ Value Inconsistency Detection</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:.8rem;color:var(--color-muted)">Detects case and spacing variants of the same value (e.g., "Active" vs "ACTIVE" vs "active").</p>', unsafe_allow_html=True)
    inconsistency_found = False
    for col in df.select_dtypes(include="object").columns[:20]:
        variants = _check_inconsistent_values(df, col)
        if variants:
            inconsistency_found = True
            with st.expander(f"⚡ Inconsistent values in '{col}' ({len(variants)} groups)"):
                for base, v_list in variants[:20]:
                    v_badges = " ".join([f'<span class="badge badge-warning">{v}</span>' for v in v_list])
                    st.markdown(f'<div style="margin:.3rem 0"><code>{base}</code> → {v_badges}</div>', unsafe_allow_html=True)
                    issues.append({"issue": f"Inconsistent casing in '{col}'", "severity": "Medium",
                        "field": col, "original_value": str(v_list), "status": "Open"})
    if not inconsistency_found:
        st.success("✅ No case/spacing inconsistencies detected in text fields.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Missing information ───────────────────────────────────
    st.markdown('<div class="section-card"><h3>❌ Missing Information Summary</h3>', unsafe_allow_html=True)
    missing_rows = []
    for col in df.columns:
        series = df[col]
        null_count  = int(series.isna().sum())
        empty_str   = int((series.astype(str).str.strip() == "").sum()) - null_count
        ws_only     = int((series.astype(str).str.strip() == "nan").sum())
        total_missing = null_count + max(empty_str, 0)
        pct = round(total_missing / max(total_rows,1) * 100, 1)
        if total_missing > 0:
            missing_rows.append({"Field": col, "Null Values": null_count,
                "Empty Strings": max(empty_str,0), "Total Missing": total_missing, "Missing %": pct,
                "Severity": "Critical" if pct > 50 else "High" if pct > 25 else "Medium" if pct > 5 else "Low"})
    if missing_rows:
        miss_df = pd.DataFrame(missing_rows).sort_values("Missing %", ascending=False)
        st.dataframe(miss_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No missing values detected.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quality scoring ───────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📊 Quality Score Methodology</h3>', unsafe_allow_html=True)
    # Calculate transparent quality score
    comp_score   = st.session_state.get("analysis_results", {}).get("overall_completeness", 100.0)
    dup_pct      = (len(id_dups) / max(total_rows,1)) * 100 if not id_dups.empty else 0
    _inv_emails  = invalid_email_idx if (email_col and email_col in df.columns) else []
    email_inv_pct= (len(_inv_emails) / max(total_rows,1)) * 100
    incons_count = sum(1 for i in issues if "Inconsistent" in i.get("issue",""))
    incons_pct   = min((incons_count / max(total_rows,1)) * 100, 20)

    completeness_w = comp_score * 0.50
    uniqueness_w   = max(0, 100 - dup_pct * 2) * 0.25
    validity_w     = max(0, 100 - email_inv_pct * 3) * 0.15
    consistency_w  = max(0, 100 - incons_pct * 2) * 0.10
    final_score    = round(completeness_w + uniqueness_w + validity_w + consistency_w, 1)

    score_df = pd.DataFrame([
        {"Dimension": "Completeness (50%)",  "Score": f"{comp_score:.1f}%",  "Weighted": f"{completeness_w:.1f}"},
        {"Dimension": "Uniqueness (25%)",    "Score": f"{max(0,100-dup_pct*2):.1f}%", "Weighted": f"{uniqueness_w:.1f}"},
        {"Dimension": "Validity (15%)",      "Score": f"{max(0,100-email_inv_pct*3):.1f}%", "Weighted": f"{validity_w:.1f}"},
        {"Dimension": "Consistency (10%)",   "Score": f"{max(0,100-incons_pct*2):.1f}%", "Weighted": f"{consistency_w:.1f}"},
        {"Dimension": "Overall Quality Score","Score": f"{final_score}%", "Weighted": "—"},
    ])
    st.dataframe(score_df, use_container_width=True, hide_index=True)

    analysis = st.session_state.get("analysis_results", {})
    analysis["quality_score"] = final_score
    analysis["duplicate_count"] = len(id_dups)
    st.session_state["analysis_results"] = analysis
    st.session_state["quality_issues"] = issues
    st.markdown("</div>", unsafe_allow_html=True)
