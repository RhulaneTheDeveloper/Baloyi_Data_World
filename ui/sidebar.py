"""
ui/sidebar.py
Persistent sidebar navigation and branding for Baloyi Data World.
"""
from __future__ import annotations

import streamlit as st

# (label, icon, page_key)
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("Dashboard",             "🏠", "dashboard"),
    ("Data Upload",           "📤", "upload"),
    ("Gap Review",            "🧭", "gap_review"),
    ("Scope & Volume",        "🔭", "scope"),
    ("Data Dictionary",       "📖", "dictionary"),
    ("Completeness Analysis", "✅", "completeness"),
    ("Data Quality",          "🔍", "quality"),
    ("Data Remediation",      "🛠️", "remediation"),
    ("Business Clarification","💬", "clarification"),
    ("Technical Readiness",   "⚙️", "readiness"),
    ("Reports & Exports",     "📊", "reports"),
    ("Analysis History",      "🕐", "history"),
    ("Settings",              "⚙️", "settings"),
]

_SECTION_BREAKS: dict[str, str] = {
    "scope":        "ANALYSIS",
    "remediation":  "MANAGEMENT",
    "reports":      "OUTPUTS",
    "settings":     "SYSTEM",
}


def render_sidebar() -> str:
    """Render the sidebar navigation. Returns the active page key."""
    with st.sidebar:
        # ── Branding ──────────────────────────────────────────
        st.markdown(
            """
            <div style="padding:1.5rem 1rem 1rem;
                        border-bottom:1px solid rgba(255,255,255,.12);
                        margin-bottom:.5rem">
              <div style="font-size:1.5rem;font-weight:800;
                          color:#FFFFFF;letter-spacing:-.5px">
                📊 Baloyi
              </div>
              <div style="font-size:.68rem;color:rgba(255,255,255,.5);
                          text-transform:uppercase;letter-spacing:.12em;
                          margin-top:.15rem">
                Data World &nbsp;·&nbsp; v1.0
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Active dataset chip ───────────────────────────────
        wb    = st.session_state.get("workbook")
        fname = st.session_state.get("uploaded_filename", "")
        if wb and fname:
            rows = wb.get("row_count", 0)
            st.markdown(
                f"""
                <div style="margin:.4rem .75rem .75rem;padding:.6rem .9rem;
                            background:rgba(22,163,106,.2);border-radius:8px;
                            border:1px solid rgba(22,163,106,.4)">
                  <div style="font-size:.65rem;color:rgba(255,255,255,.5);
                              text-transform:uppercase;letter-spacing:.08em">
                    Active dataset
                  </div>
                  <div style="font-size:.82rem;color:#FFFFFF;font-weight:600;
                              margin-top:.2rem;white-space:nowrap;overflow:hidden;
                              text-overflow:ellipsis" title="{fname}">
                    {fname[:28]}{"…" if len(fname)>28 else ""}
                  </div>
                  <div style="font-size:.7rem;color:rgba(255,255,255,.5);margin-top:.1rem">
                    {rows:,} records
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="margin:.4rem .75rem .75rem;padding:.5rem .9rem;
                            background:rgba(255,255,255,.06);border-radius:8px;
                            border:1px solid rgba(255,255,255,.1)">
                  <div style="font-size:.75rem;color:rgba(255,255,255,.4)">
                    No dataset loaded
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Initialise active page ────────────────────────────
        if "active_page" not in st.session_state:
            st.session_state["active_page"] = "dashboard"

        active = st.session_state["active_page"]

        # ── Navigation items ──────────────────────────────────
        for label, icon, key in NAV_ITEMS:
            # Section header
            if key in _SECTION_BREAKS:
                st.markdown(
                    f'<div style="font-size:.62rem;font-weight:700;'
                    f'text-transform:uppercase;letter-spacing:.1em;'
                    f'color:rgba(255,255,255,.32);padding:.85rem 1rem .25rem;'
                    f'display:block">{_SECTION_BREAKS[key]}</div>',
                    unsafe_allow_html=True,
                )

            is_active = active == key
            # Highlight active item with a coloured left border block
            if is_active:
                st.markdown(
                    f'<div style="background:rgba(22,163,106,.22);'
                    f'border-left:3px solid #16A36A;border-radius:0 6px 6px 0;'
                    f'margin:0 .5rem 0 0;padding:.45rem .75rem;'
                    f'font-size:.875rem;font-weight:600;color:#FFFFFF;">'
                    f'{icon}&nbsp;&nbsp;{label}</div>',
                    unsafe_allow_html=True,
                )
                # Hidden button that is never clicked but keeps state
                st.button(
                    f"{icon} {label}",
                    key=f"nav_btn_{key}",
                    use_container_width=True,
                    disabled=True,
                )
            else:
                if st.button(
                    f"{icon}  {label}",
                    key=f"nav_btn_{key}",
                    use_container_width=True,
                ):
                    st.session_state["active_page"] = key
                    st.rerun()

        # ── Footer ────────────────────────────────────────────
        st.markdown(
            """
            <div style="padding:.85rem 1rem;margin-top:1rem;
                        border-top:1px solid rgba(255,255,255,.1);
                        font-size:.68rem;color:rgba(255,255,255,.32)">
              Prepared by: <strong style="color:rgba(255,255,255,.5)">Rhulane Baloyi</strong><br>
              Baloyi Data World · 2026
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.get("active_page", "dashboard")
