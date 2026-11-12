"""
ui/styles.py
Global CSS injection for the Baloyi Data World enterprise UI.
"""

BRAND_CSS = """
<style>
/* =========================================================
   BALOYI DATA WORLD – GLOBAL ENTERPRISE STYLES
   ========================================================= */

/* ---- Colour tokens ---- */
:root {
    --color-primary:    #142B3B;
    --color-secondary:  #263D4A;
    --color-accent:     #16A36A;
    --color-bg:         #F5F7FA;
    --color-card:       #FFFFFF;
    --color-text:       #202B36;
    --color-muted:      #73808C;
    --color-warning:    #F59E0B;
    --color-critical:   #DC2626;
    --color-success:    #16A36A;
    --color-border:     #E2E8F0;
    --color-hover:      #EEF2F7;
    --shadow-sm:        0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:        0 4px 6px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.05);
    --shadow-lg:        0 10px 15px rgba(0,0,0,.08), 0 4px 6px rgba(0,0,0,.04);
    --radius-sm:        6px;
    --radius-md:        10px;
    --radius-lg:        14px;
    --font-mono:        'JetBrains Mono', 'Consolas', monospace;
}

/* ---- Page / App shell ---- */
.stApp {
    background-color: var(--color-bg) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    color: var(--color-text);
}

/* ---- Hide default Streamlit chrome ---- */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: var(--color-primary) !important;
    border-right: none !important;
    min-width: 240px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .sidebar-logo-block {
    padding: 1.5rem 1.25rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,.12);
    margin-bottom: 0.5rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    cursor: pointer;
    display: block;
    padding: 0.55rem 1.25rem;
    border-radius: var(--radius-sm);
    transition: background 0.15s;
    font-size: 0.875rem;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,.08) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + label,
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background: var(--color-accent) !important;
    color: #FFFFFF !important;
}
/* style radio dots away */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* ---- Page header banner ---- */
.page-header {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: #FFFFFF;
    padding: 1.5rem 2rem;
    border-radius: var(--radius-lg);
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
}
.page-header h1 {
    margin: 0 0 0.25rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: #FFFFFF !important;
}
.page-header p {
    margin: 0;
    color: rgba(255,255,255,.75) !important;
    font-size: 0.9rem;
}

/* ---- Metric / KPI cards ---- */
.metric-card {
    background: var(--color-card);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--color-border);
    transition: box-shadow 0.2s, transform 0.2s;
    height: 100%;
}
.metric-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.metric-card .metric-icon {
    font-size: 1.75rem;
    margin-bottom: 0.5rem;
    display: block;
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary);
    line-height: 1.1;
}
.metric-card .metric-label {
    font-size: 0.8rem;
    color: var(--color-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}
.metric-card .metric-delta {
    font-size: 0.75rem;
    color: var(--color-accent);
    margin-top: 0.3rem;
}
.metric-card.warning .metric-value { color: var(--color-warning); }
.metric-card.critical .metric-value { color: var(--color-critical); }
.metric-card.success .metric-value { color: var(--color-success); }

/* ---- Section cards ---- */
.section-card {
    background: var(--color-card);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--color-border);
    margin-bottom: 1.25rem;
}
.section-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-primary);
    margin: 0 0 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid var(--color-border);
}

/* ---- Data table overrides ---- */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--color-border) !important;
}
[data-testid="stDataFrame"] thead th {
    background: var(--color-primary) !important;
    color: #FFFFFF !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: var(--color-hover) !important;
}

/* ---- Status badges ---- */
.badge {
    display: inline-block;
    padding: 0.2em 0.65em;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-success  { background: #DCFCE7; color: #15803D; }
.badge-warning  { background: #FEF3C7; color: #92400E; }
.badge-critical { background: #FEE2E2; color: #991B1B; }
.badge-info     { background: #DBEAFE; color: #1E40AF; }
.badge-muted    { background: #F1F5F9; color: #475569; }

/* ---- Progress bar custom ---- */
.progress-bar-wrapper {
    background: var(--color-border);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}
.progress-bar-fill.good    { background: var(--color-accent); }
.progress-bar-fill.warning { background: var(--color-warning); }
.progress-bar-fill.critical{ background: var(--color-critical); }

/* ---- Empty state ---- */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--color-muted);
}
.empty-state .empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: .6;
}
.empty-state h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-secondary);
    margin-bottom: 0.5rem;
}
.empty-state p {
    font-size: 0.875rem;
    max-width: 400px;
    margin: 0 auto;
}

/* ---- Alert overrides ---- */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
}

/* ---- Buttons ---- */
.stButton > button {
    background: var(--color-accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.2s, transform 0.1s !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: #128F5A !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* secondary button variant */
.btn-secondary > button {
    background: transparent !important;
    color: var(--color-primary) !important;
    border: 1.5px solid var(--color-border) !important;
    box-shadow: none !important;
}
.btn-secondary > button:hover {
    background: var(--color-hover) !important;
    transform: none !important;
}

/* ---- Form widgets ---- */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div,
[data-testid="stTextInput"] > div > div {
    border-radius: var(--radius-sm) !important;
    border-color: var(--color-border) !important;
}
[data-testid="stSelectbox"]:focus-within > div,
[data-testid="stTextInput"]:focus-within > div > div {
    border-color: var(--color-accent) !important;
    box-shadow: 0 0 0 3px rgba(22,163,106,.15) !important;
}

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: transparent;
    border-bottom: 2px solid var(--color-border);
    padding-bottom: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    padding: 0.6rem 1.25rem !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: var(--color-muted) !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--color-primary) !important;
    border-bottom: 2px solid var(--color-accent) !important;
}

/* ---- Spinner ---- */
[data-testid="stSpinner"] { color: var(--color-accent) !important; }

/* ---- Divider ---- */
hr { border-color: var(--color-border) !important; opacity: 1 !important; }

/* ---- Tooltip helper ---- */
.tooltip-hint {
    font-size: 0.75rem;
    color: var(--color-muted);
    font-style: italic;
    margin-top: 0.2rem;
}

/* ---- Section separator ---- */
.section-sep {
    border-top: 1px solid var(--color-border);
    margin: 1.5rem 0;
}

/* ---- Upload area ---- */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--color-border) !important;
    border-radius: var(--radius-md) !important;
    background: #F8FAFC !important;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--color-accent) !important;
}

/* ---- Sidebar nav section labels ---- */
.nav-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,.4) !important;
    padding: 1rem 1.25rem 0.3rem;
    display: block;
}

/* ---- Info row ---- */
.info-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--color-border);
    font-size: 0.875rem;
}
.info-row .info-label {
    color: var(--color-muted);
    min-width: 160px;
    font-weight: 500;
}
.info-row .info-value {
    color: var(--color-text);
    font-weight: 600;
}

/* ---- Animated counter ---- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.metric-card, .section-card, .page-header {
    animation: fadeInUp 0.35s ease both;
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--color-muted); }

/* ---- Mobile adjustments ---- */
@media (max-width: 768px) {
    .metric-card .metric-value { font-size: 1.5rem; }
    .page-header { padding: 1rem 1.25rem; }
    .page-header h1 { font-size: 1.25rem; }
}
</style>
"""


def inject_styles() -> None:
    """Inject global CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def metric_card(icon: str, value: str, label: str, delta: str = "", variant: str = "") -> str:
    """Return HTML for a styled KPI metric card."""
    variant_class = f" {variant}" if variant else ""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    return f"""
<div class="metric-card{variant_class}">
  <span class="metric-icon">{icon}</span>
  <div class="metric-value">{value}</div>
  <div class="metric-label">{label}</div>
  {delta_html}
</div>"""


def page_header(title: str, description: str = "", icon: str = "") -> str:
    """Return HTML for a styled page header banner."""
    icon_html = f'<span style="margin-right:.5rem">{icon}</span>' if icon else ""
    desc_html = f"<p>{description}</p>" if description else ""
    return f"""
<div class="page-header">
  <h1>{icon_html}{title}</h1>
  {desc_html}
</div>"""


def empty_state(icon: str, heading: str, body: str) -> str:
    """Return HTML for a styled empty-state block."""
    return f"""
<div class="empty-state">
  <div class="empty-icon">{icon}</div>
  <h3>{heading}</h3>
  <p>{body}</p>
</div>"""


def badge(text: str, variant: str = "muted") -> str:
    """Return an inline badge HTML element."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def progress_bar(pct: float, label: str = "") -> str:
    """Return HTML for a branded progress bar.  pct is 0–100."""
    if pct >= 80:
        cls = "good"
    elif pct >= 50:
        cls = "warning"
    else:
        cls = "critical"
    label_html = f'<div style="font-size:.8rem;color:var(--color-muted);margin-bottom:.2rem">{label} &nbsp;<strong>{pct:.1f}%</strong></div>' if label else ""
    return f"""
{label_html}
<div class="progress-bar-wrapper">
  <div class="progress-bar-fill {cls}" style="width:{min(pct,100):.1f}%"></div>
</div>"""


def section_card_start(title: str) -> str:
    """Return opening HTML for a section card."""
    return f'<div class="section-card"><h3>{title}</h3>'


def section_card_end() -> str:
    """Return closing HTML for a section card."""
    return "</div>"
