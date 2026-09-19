"""
style.py
---------
Shared visual identity for the app: fonts, colors, badges and card components.
Import `inject_css()` at the top of every page to apply it, and use the small
helper functions (badge, section_label, etc.) to render consistent UI pieces.

Design tokens
-------------
Ink (primary)   : #1F2D50  -- deep academic navy, used for headings/nav
Paper (bg)      : #FAF7F1  -- warm paper background
Panel (bg alt)  : #FFFFFF  -- card surfaces
Gold (accent)   : #B98B27  -- accent for highlights, links, active states
Positive        : #3A7D57  -- muted green
Neutral         : #8A6E2F  -- muted ochre
Negative        : #B0413E  -- muted brick red (also = High priority)
Medium priority : #C08A2E
Low priority    : #3A7D57
Border          : #E4DCC9
Muted text      : #6B7280

Typography: "Lora" (serif) for headings/display, "Inter" (sans) for body & data.
"""

import streamlit as st
from html import escape

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Lora', serif !important;
    color: #1F2D50 !important;
    letter-spacing: -0.01em;
}

/* App background */
.stApp {
    background-color: #FAF7F1;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1F2D50;
    border-right: 1px solid #17223E;
}
section[data-testid="stSidebar"] * {
    color: #F0EADD !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(240,234,221,0.2);
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    background-color: #1F2D50;
    color: #FAF7F1;
    border: none;
    border-radius: 4px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: background-color 0.15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #B98B27;
    color: #1F2D50;
}

/* Text inputs / textareas */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    border-radius: 4px !important;
    border: 1px solid #E4DCC9 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #B98B27 !important;
    box-shadow: 0 0 0 1px #B98B27 !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E4DCC9;
    border-left: 4px solid #B98B27;
    border-radius: 4px;
    padding: 0.9rem 1rem 0.7rem 1rem;
}
div[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-weight: 500;
}
div[data-testid="stMetricValue"] {
    color: #1F2D50 !important;
    font-family: 'Lora', serif;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #E4DCC9;
    border-radius: 4px;
}

/* Divider spacing tighten */
hr {
    margin: 1.1rem 0;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1F2D50 0%, #2C3E6B 100%);
    color: #FAF7F1;
    padding: 2.4rem 2.2rem;
    border-radius: 6px;
    margin-bottom: 1.6rem;
}
.hero h1 {
    color: #FAF7F1 !important;
    margin: 0 0 0.4rem 0;
    font-size: 2.1rem;
}
.hero p {
    color: #D9CDB3;
    margin: 0;
    font-size: 1.02rem;
    max-width: 560px;
}
.hero .eyebrow {
    color: #B98B27;
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

/* Nav cards on home page */
.nav-card {
    background-color: #FFFFFF;
    border: 1px solid #E4DCC9;
    border-top: 3px solid #1F2D50;
    border-radius: 4px;
    padding: 1.3rem 1.3rem 1.1rem 1.3rem;
    height: 100%;
}
.nav-card h3 {
    margin-top: 0;
    font-size: 1.15rem;
}
.nav-card p {
    color: #52586A;
    font-size: 0.93rem;
    line-height: 1.5;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.28rem 0.75rem;
    border-radius: 3px;
    font-weight: 600;
    font-size: 0.92rem;
    font-family: 'Inter', sans-serif;
}
.badge-Positive   { background-color: #E4F0E8; color: #3A7D57; }
.badge-Neutral    { background-color: #F2ECDA; color: #8A6E2F; }
.badge-Negative   { background-color: #F6E4E3; color: #B0413E; }
.badge-Low        { background-color: #E4F0E8; color: #3A7D57; }
.badge-Medium     { background-color: #FBEED9; color: #C08A2E; }
.badge-High       { background-color: #F6E4E3; color: #B0413E; }
.badge-Pending    { background-color: #F2ECDA; color: #8A6E2F; }
.badge-In-Progress{ background-color: #E4EAF2; color: #33538A; }
.badge-Resolved   { background-color: #E4F0E8; color: #3A7D57; }

/* Result card on submission */
.result-card {
    background-color: #FFFFFF;
    border: 1px solid #E4DCC9;
    border-radius: 6px;
    padding: 1.4rem 1.5rem;
    margin-top: 0.6rem;
}
.result-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid #F0EADD;
}
.result-row:last-child { border-bottom: none; }
.result-label {
    color: #6B7280;
    font-weight: 500;
    font-size: 0.95rem;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str) -> str:
    """Return an HTML badge span for a status/sentiment/priority value."""
    safe_text = escape(str(text))
    css_class = safe_text.replace(" ", "-")
    return f'<span class="badge badge-{css_class}">{safe_text}</span>'


def hero(eyebrow: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
