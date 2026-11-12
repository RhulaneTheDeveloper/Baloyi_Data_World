import streamlit as st

from modules.excel_import import load_workbook

st.title("01. Excel Import & Data Preview")
uploaded = st.file_uploader("Upload Excel workbook", type=["xlsx", "xls", "csv"])
if uploaded is not None:
    workbook = load_workbook(uploaded)
    st.success(f"Loaded {workbook['row_count']} rows from {workbook['sheet_count']} sheet(s).")
    st.dataframe(workbook["data"].head(20), use_container_width=True)
