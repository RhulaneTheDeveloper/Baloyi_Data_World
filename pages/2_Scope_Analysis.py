import streamlit as st

from modules.excel_import import load_workbook

st.title("02. Scope & Volume Analysis")
uploaded = st.file_uploader("Upload a workbook", type=["xlsx", "xls", "csv"])
if uploaded is not None:
    summary = load_workbook(uploaded)
    st.write(summary["sheet_names"])
    st.dataframe(
        {
            "Metric": ["Row count", "Column count", "Sheet count"],
            "Value": [summary["row_count"], summary["column_count"], summary["sheet_count"]],
        },
        use_container_width=True,
        hide_index=True,
    )
