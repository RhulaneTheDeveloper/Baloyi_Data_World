import streamlit as st

from config.settings import DEFAULT_MANDATORY_FIELDS
from modules.completeness import calculate_missingness
from modules.excel_import import load_workbook

st.title("04. Completeness Assessment")
uploaded = st.file_uploader("Upload workbook", type=["xlsx", "xls", "csv"])
if uploaded is not None:
    workbook = load_workbook(uploaded)
    result = calculate_missingness(workbook["data"], DEFAULT_MANDATORY_FIELDS)
    st.dataframe(result, use_container_width=True)
