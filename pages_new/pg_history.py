"""
pages_new/pg_history.py  –  Analysis History
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from ui.styles import page_header, empty_state, metric_card


def render() -> None:
    st.markdown(page_header("Analysis History",
        "Review previous analysis sessions and their results","🕐"),
        unsafe_allow_html=True)

    history: list[dict] = st.session_state.get("analysis_history", [])
    if not history:
        st.markdown(empty_state("🕐","No history yet",
            "Analysis sessions are recorded each time you upload and process a workbook."),
            unsafe_allow_html=True)
        return

    st.markdown('<div class="section-card"><h3>📋 Session History</h3>', unsafe_allow_html=True)
    mc = st.columns(3)
    mc[0].markdown(metric_card("🕐",str(len(history)),"Total Sessions"), unsafe_allow_html=True)
    mc[1].markdown(metric_card("📄",history[-1].get("filename","—")[:20],"Last File"), unsafe_allow_html=True)
    mc[2].markdown(metric_card("📅",history[-1].get("timestamp","—"),"Last Analysis"), unsafe_allow_html=True)

    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)
    hist_df = pd.DataFrame(history[::-1])  # most recent first
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear History"):
        st.session_state["analysis_history"] = []
        st.rerun()
