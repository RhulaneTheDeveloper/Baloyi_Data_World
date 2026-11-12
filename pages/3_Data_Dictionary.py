import streamlit as st

from modules.excel_import import load_workbook
from modules.data_profiling import build_field_dictionary

st.title("03. Data Dictionary & Structure")
uploaded = st.file_uploader("Upload workbook", type=["xlsx", "xls", "csv"])
if uploaded is not None:
    workbook = load_workbook(uploaded)
    dictionary = build_field_dictionary(workbook["data"])
    st.dataframe(dictionary, use_container_width=True)
