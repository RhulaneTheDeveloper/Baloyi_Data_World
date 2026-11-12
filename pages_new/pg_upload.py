"""
pages_new/pg_upload.py
Data Upload module – professional enterprise file upload experience.
"""
from __future__ import annotations

import hashlib
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from config.settings import COLUMN_ALIASES, DEFAULT_MANDATORY_FIELDS
from modules.excel_import import load_workbook, normalize_column_name
from ui.styles import badge, empty_state, metric_card, page_header, progress_bar

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
ALLOWED_MIME = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}

STANDARDISED_FIELDS = [
    "learner_id", "first_name", "surname", "email",
    "phone", "department", "programme", "start_date",
    "end_date", "status", "id_number", "date_of_birth",
    "gender", "nationality",
]


# ─────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────

def _validate_file(uploaded_file) -> tuple[bool, str]:
    """Return (ok, error_message)."""
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: **{suffix}**. Please upload .xlsx, .xls, or .xlsm."
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size {size_mb:.1f} MB exceeds the {MAX_FILE_SIZE_MB} MB limit."
    return True, ""


def _file_hash(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:10]


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    return f"{size_bytes/(1024*1024):.1f} MB"


def _guess_header_row(df_raw: pd.DataFrame) -> int:
    """Try to detect the header row (0-based) by looking at all-string rows."""
    for i, row in df_raw.head(10).iterrows():
        if row.apply(lambda v: isinstance(v, str)).sum() >= max(len(df_raw.columns) // 2, 2):
            return int(i)
    return 0


def _auto_map_columns(source_cols: list[str]) -> dict[str, str]:
    """Return {standardised_field: source_column} using alias matching."""
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for std_field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            alias_norm = normalize_column_name(alias)
            for col in source_cols:
                col_norm = normalize_column_name(col)
                if alias_norm == col_norm and col not in used:
                    mapping[std_field] = col
                    used.add(col)
                    break
            if std_field in mapping:
                break
    return mapping


# ─────────────────────────────────────────────────────────────
# render
# ─────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        page_header(
            "Data Upload",
            "Import your Excel workbook and configure analysis settings",
            "📤",
        ),
        unsafe_allow_html=True,
    )

    # ── Step 1: File upload ──────────────────────────────────
    st.markdown('<div class="section-card"><h3>Step 1 — Upload Workbook</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:.875rem;color:var(--color-muted);margin-bottom:1rem">'
        'Drag and drop an Excel file or click to browse. Supported: <strong>.xlsx · .xls · .xlsm</strong> '
        f'· Max size: <strong>{MAX_FILE_SIZE_MB} MB</strong></p>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload workbook",
        type=["xlsx", "xls", "xlsm"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is None:
        st.markdown(
            empty_state(
                "📂",
                "Awaiting file upload",
                "Once you upload a workbook the application will read its structure and allow "
                "you to configure worksheets, header rows, field mapping and mandatory fields.",
            ),
            unsafe_allow_html=True,
        )
        return

    # ── Validation ───────────────────────────────────────────
    valid, err = _validate_file(uploaded_file)
    if not valid:
        st.error(err)
        return

    raw_bytes = uploaded_file.getvalue()
    file_hash = _file_hash(raw_bytes)

    # Read sheet names without loading everything
    try:
        xl = pd.ExcelFile(io.BytesIO(raw_bytes))
        sheet_names = xl.sheet_names
    except Exception as exc:
        st.error(f"Could not read workbook: {exc}")
        logger.exception("ExcelFile read failed")
        return

    # ── File info card ───────────────────────────────────────
    st.markdown('<div class="section-card"><h3>📄 File Information</h3>', unsafe_allow_html=True)
    info_cols = st.columns(4)
    info_cols[0].markdown(metric_card("📄", uploaded_file.name.rsplit(".",1)[0][:20], "File Name"), unsafe_allow_html=True)
    info_cols[1].markdown(metric_card("📦", _human_size(uploaded_file.size), "File Size"), unsafe_allow_html=True)
    info_cols[2].markdown(metric_card("🗂️", str(len(sheet_names)), "Worksheets Found"), unsafe_allow_html=True)
    info_cols[3].markdown(metric_card("🔑", file_hash, "File Fingerprint"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 2: Worksheet & header row selection ─────────────
    st.markdown('<div class="section-card"><h3>Step 2 — Worksheet & Header Configuration</h3>', unsafe_allow_html=True)

    col_ws, col_hdr = st.columns(2)
    with col_ws:
        selected_sheet = st.selectbox(
            "Select worksheet",
            sheet_names,
            help="Choose which worksheet contains the learner data to analyse.",
        )
    with col_hdr:
        header_row = st.number_input(
            "Header row (1-based)",
            min_value=1, max_value=20, value=1,
            help="Row number that contains the column headers. Usually row 1.",
        )

    # Load preview with selected sheet and header row
    with st.spinner("Loading worksheet…"):
        try:
            df_preview = pd.read_excel(
                io.BytesIO(raw_bytes),
                sheet_name=selected_sheet,
                header=int(header_row) - 1,
                nrows=200,
            )
            df_preview.columns = [str(c).strip() for c in df_preview.columns]
        except Exception as exc:
            st.error(f"Failed to load worksheet: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)
            return

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 3: Data preview ─────────────────────────────────
    st.markdown('<div class="section-card"><h3>Step 3 — Data Preview</h3>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:.8rem;color:var(--color-muted)">Showing first {min(25,len(df_preview))} '
        f'of {len(df_preview)} rows loaded for preview · {len(df_preview.columns)} columns</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(df_preview.head(25), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 4: Identifier & field mapping ──────────────────
    st.markdown('<div class="section-card"><h3>Step 4 — Field Mapping & Identifier Selection</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:.875rem;color:var(--color-muted)">Map your source column names to '
        'standardised field names. Auto-mapping has been attempted based on common aliases.</p>',
        unsafe_allow_html=True,
    )

    source_cols = list(df_preview.columns)
    auto_map = _auto_map_columns(source_cols)

    # Learner identifier column
    id_candidates = [c for c in source_cols
                     if any(k in c.lower() for k in ("id", "number", "learner", "student", "candidate"))]
    default_id = id_candidates[0] if id_candidates else source_cols[0] if source_cols else None

    id_col_choice = st.selectbox(
        "Learner identifier column",
        source_cols,
        index=source_cols.index(default_id) if default_id and default_id in source_cols else 0,
        help="The column that uniquely identifies each learner record (used for duplicate detection).",
    )

    # Column mapping table
    st.markdown(
        '<p style="font-size:.8rem;color:var(--color-muted);margin-top:1rem;margin-bottom:.5rem">'
        '🔄 Column Mapping — select source column for each standardised field (or leave blank to skip)</p>',
        unsafe_allow_html=True,
    )

    blank_opt = "— Not mapped —"
    mapping_result: dict[str, str] = {}

    map_col_a, map_col_b = st.columns(2)
    fields_left = STANDARDISED_FIELDS[:len(STANDARDISED_FIELDS)//2 + 1]
    fields_right = STANDARDISED_FIELDS[len(STANDARDISED_FIELDS)//2 + 1:]

    for col_widget, field_group in [(map_col_a, fields_left), (map_col_b, fields_right)]:
        with col_widget:
            for sf in field_group:
                current = auto_map.get(sf, blank_opt)
                opts = [blank_opt] + source_cols
                default_idx = opts.index(current) if current in opts else 0
                chosen = st.selectbox(
                    f"`{sf}`",
                    opts,
                    index=default_idx,
                    key=f"map_{sf}",
                    help=f"Map source column to standardised field: {sf}",
                )
                if chosen != blank_opt:
                    mapping_result[sf] = chosen

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 5: Mandatory fields ─────────────────────────────
    st.markdown('<div class="section-card"><h3>Step 5 — Mandatory Field Configuration</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:.875rem;color:var(--color-muted)">Select which fields are mandatory '
        'for this dataset. Completeness calculations will be based on this selection.</p>',
        unsafe_allow_html=True,
    )

    # Pre-select fields that have been mapped
    mapped_std_fields = list(mapping_result.keys())
    default_mandatory = [f for f in DEFAULT_MANDATORY_FIELDS if f in mapped_std_fields]
    if not default_mandatory:
        default_mandatory = mapped_std_fields[:min(5, len(mapped_std_fields))]

    mandatory_fields = st.multiselect(
        "Mandatory fields",
        options=mapped_std_fields if mapped_std_fields else STANDARDISED_FIELDS,
        default=default_mandatory,
        help="Fields marked as mandatory will drive completeness scoring and issue flagging.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Confirm & Process ────────────────────────────────────
    st.markdown("<div style='margin:1.25rem 0'></div>", unsafe_allow_html=True)
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        process_btn = st.button(
            "▶  Load & Analyse Dataset",
            use_container_width=True,
            type="primary",
        )

    if process_btn:
        with st.spinner("Processing workbook and running initial analysis…"):
            try:
                workbook = load_workbook(uploaded_file)

                # Build a clean df from selected sheet & header
                df_full = pd.read_excel(
                    io.BytesIO(raw_bytes),
                    sheet_name=selected_sheet,
                    header=int(header_row) - 1,
                )
                df_full.columns = [str(c).strip() for c in df_full.columns]

                # Store in session state
                now = datetime.now()
                st.session_state["workbook"]          = workbook
                st.session_state["active_df"]         = df_full
                st.session_state["selected_sheet"]    = selected_sheet
                st.session_state["id_column"]         = id_col_choice
                st.session_state["column_mapping"]    = mapping_result
                st.session_state["mandatory_fields"]  = mandatory_fields
                st.session_state["uploaded_filename"] = uploaded_file.name
                st.session_state["upload_time"]       = now.strftime("%Y-%m-%d %H:%M")
                st.session_state["last_analysis_time"]= now.strftime("%Y-%m-%d %H:%M")
                st.session_state["analysis_results"]  = {}
                st.session_state["quality_issues"]    = []

                # Update history
                history = st.session_state.get("analysis_history", [])
                history.append({
                    "timestamp": now.strftime("%d %b %Y %H:%M"),
                    "filename":  uploaded_file.name,
                    "rows":      len(df_full),
                    "sheet":     selected_sheet,
                })
                st.session_state["analysis_history"] = history

                st.session_state["active_page"] = "gap_review"
                st.success(
                    f"✅ **Dataset loaded successfully!**  "
                    f"{len(df_full):,} records · {len(df_full.columns)} fields · "
                    f"Sheet: {selected_sheet}"
                )
                st.caption("The analysis has moved to the post-upload Gap Review page.")
                st.rerun()

            except Exception as exc:
                st.error(f"Failed to process workbook: {exc}")
                logger.exception("Workbook processing error")
                return

        # Show summary after load
        st.markdown('<div class="section-card"><h3>✅ Dataset Summary</h3>', unsafe_allow_html=True)
        df_loaded = st.session_state["active_df"]
        s_cols = st.columns(5)
        s_cols[0].markdown(metric_card("📋", f"{len(df_loaded):,}", "Records"), unsafe_allow_html=True)
        s_cols[1].markdown(metric_card("🗂️", str(len(df_loaded.columns)), "Columns"), unsafe_allow_html=True)
        s_cols[2].markdown(metric_card("🔑", id_col_choice[:18], "Identifier"), unsafe_allow_html=True)
        s_cols[3].markdown(metric_card("📌", str(len(mandatory_fields)), "Mandatory Fields"), unsafe_allow_html=True)
        s_cols[4].markdown(metric_card("🔄", str(len(mapping_result)), "Mapped Fields"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Mapping summary table
        if mapping_result:
            st.markdown('<div class="section-card"><h3>🔄 Field Mapping Summary</h3>', unsafe_allow_html=True)
            map_df = pd.DataFrame([
                {
                    "Standardised Field": k,
                    "Source Column": v,
                    "Mandatory": "✅ Yes" if k in mandatory_fields else "○ No",
                }
                for k, v in mapping_result.items()
            ])
            st.dataframe(map_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)
