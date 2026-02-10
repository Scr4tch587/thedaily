"""Streamlit entry point — The Daily: Tech Breakthrough Radar."""

from datetime import datetime, timezone

import streamlit as st

st.set_page_config(
    page_title="The Daily",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── NYT-inspired global CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Libre+Franklin:wght@300;400;500;600&family=Lora:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Reset & base ── */
.stApp {
    background-color: #FAFAF8;
}

/* ── Masthead ── */
.masthead {
    text-align: center;
    padding: 1.2rem 0 0.6rem 0;
    border-bottom: 2px solid #000;
    margin-bottom: 0;
}
.masthead-date {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.72rem;
    font-weight: 400;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.25rem;
}
.masthead-title {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #000;
    letter-spacing: -0.5px;
    line-height: 1;
    margin: 0;
    padding: 0;
}
.masthead-subtitle {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.68rem;
    font-weight: 300;
    color: #888;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}
.thin-rule {
    border: none;
    border-top: 1px solid #E0E0E0;
    margin: 0.5rem 0;
}
.thick-rule {
    border: none;
    border-top: 2px solid #000;
    margin: 0.8rem 0 0.5rem 0;
}

/* ── Section headers ── */
.section-label {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    color: #000;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0.8rem 0 0.3rem 0;
}

/* ── Headline styles ── */
.headline-lg {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #121212;
    line-height: 1.25;
    margin: 0.3rem 0 0.2rem 0;
}
.headline-md {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #121212;
    line-height: 1.3;
    margin: 0.2rem 0;
}
.headline-sm {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #121212;
    line-height: 1.3;
    margin: 0.15rem 0;
}
.summary-text {
    font-family: 'Lora', 'Georgia', serif;
    font-size: 0.88rem;
    color: #333;
    line-height: 1.55;
    margin: 0.15rem 0 0.3rem 0;
}
.meta-text {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.68rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.meta-text a {
    color: #999;
    text-decoration: none;
}
.meta-text a:hover {
    color: #000;
}

/* ── Sidebar NYT styling ── */
[data-testid="stSidebar"] {
    background-color: #FAFAF8;
    border-right: 1px solid #E0E0E0;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    font-family: 'Lora', 'Georgia', serif;
    font-size: 0.85rem;
    color: #333;
    line-height: 1.5;
}

/* ── Chat styling ── */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0.8rem 0 !important;
    border-bottom: 1px solid #E8E8E8 !important;
}
[data-testid="stChatMessage"] p {
    font-family: 'Lora', 'Georgia', serif;
    font-size: 0.92rem;
    color: #333;
    line-height: 1.6;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    font-family: 'Playfair Display', 'Georgia', serif;
    color: #121212;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Lora', 'Georgia', serif;
    font-size: 0.9rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #E0E0E0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #666;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    color: #000 !important;
    border-bottom: 2px solid #000 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background-color: transparent;
    border: 1px solid #E0E0E0;
    padding: 0.6rem;
}
[data-testid="stMetricLabel"] p {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #888;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', 'Georgia', serif;
    color: #121212;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'Libre Franklin', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #333;
}

/* ── Links ── */
a {
    color: #326891 !important;
    text-decoration: none !important;
}
a:hover {
    text-decoration: underline !important;
}

/* ── Hide Streamlit default header/footer ── */
header[data-testid="stHeader"] {
    background-color: #FAFAF8;
}
</style>
""", unsafe_allow_html=True)

# ── Masthead ──────────────────────────────────────────────────────────
today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
st.markdown(f"""
<div class="masthead">
    <div class="masthead-date">{today}</div>
    <div class="masthead-title">The Daily</div>
    <div class="masthead-subtitle">Tech Breakthrough Radar</div>
</div>
""", unsafe_allow_html=True)

# ── Imports after page config ─────────────────────────────────────────
from ui.sidebar import render_sidebar
from ui.chat import render_chat
from ui.charts import render_charts

# Sidebar
render_sidebar()

# Main area
st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)

# Two-column NYT-style layout: chat (main) + charts (aside)
col_main, col_aside = st.columns([3, 2], gap="large")

with col_main:
    st.markdown('<div class="section-label">Intelligence Briefing</div>', unsafe_allow_html=True)
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    render_chat()

with col_aside:
    st.markdown('<div class="section-label">Data & Trends</div>', unsafe_allow_html=True)
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    render_charts()
