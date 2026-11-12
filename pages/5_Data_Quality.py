import pandas as pd
import streamlit as st

from modules.consistency import evaluate_consistency
from modules.duplicate_detection import find_duplicate_rows
from modules.excel_import import load_workbook

st.title("05. Data Quality Analysis")
uploaded = st.file_uploader("Upload workbook", type=["xlsx", "xls", "csv"])
if uploaded is not None:
    workbook = load_workbook(uploaded)
    df = workbook["data"]
    duplicate_df = find_duplicate_rows(df, workbook["identifier_field"] or df.columns[0])
    st.write("Duplicate rows:")
    st.dataframe(duplicate_df.head(20), use_container_width=True)
    st.write("Consistency checks:")
    st.dataframe(pd.DataFrame([evaluate_consistency(df)]), use_container_width=True)
