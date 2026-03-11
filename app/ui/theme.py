"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/ui/theme.py
Purpose: Dark FinTech CSS injection for Streamlit.
         Applies global dark theme, custom fonts, card styles, and badge colors.
================================================================================
"""
import streamlit as st
from config.settings import THEME


def inject_css():
    """Injects global CSS into the Streamlit app for dark FinTech aesthetics."""
    st.markdown(f"""
    <style>
    /* ── GLOBAL BACKGROUND ───────────────────────────── */
    .stApp {{ background-color: {THEME['bg']}; color: {THEME['text']}; }}
    .stApp > header {{ background-color: {THEME['bg']}; }}
    section[data-testid="stSidebar"] {{ background-color: {THEME['panel_bg']}; }}

    /* ── METRIC CARDS ────────────────────────────────── */
    div[data-testid="metric-container"] {{
        background: {THEME['card_bg']};
        border: 1px solid {THEME['grid']};
        border-radius: 8px;
        padding: 12px 16px;
    }}
    div[data-testid="metric-container"] label {{
        color: {THEME['subtext']} !important;
        font-size: 12px;
    }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: {THEME['text']} !important;
    }}

    /* ── TABS ────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {THEME['card_bg']};
        border-radius: 8px;
        gap: 4px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {THEME['subtext']};
        background: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {THEME['green']} !important;
        color: #000 !important;
        font-weight: 600;
    }}

    /* ── DATAFRAME ───────────────────────────────────── */
    .stDataFrame {{ background: {THEME['card_bg']}; border-radius: 8px; }}

    /* ── BUTTONS ─────────────────────────────────────── */
    .stButton > button {{
        background: {THEME['green']};
        color: #000;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }}

    /* ── INFO / SUCCESS / WARNING BOXES ─────────────── */
    .stAlert {{
        border-radius: 8px;
    }}

    /* ── SIDEBAR TEXT ────────────────────────────────── */
    section[data-testid="stSidebar"] * {{ color: {THEME['text']}; }}

    /* ── EXPANDER ────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background: {THEME['card_bg']};
        color: {THEME['subtext']};
        border-radius: 6px;
    }}

    /* ── HEADER BRANDING ─────────────────────────────── */
    .fintech-header {{
        background: linear-gradient(135deg, {THEME['bg']} 0%, {THEME['panel_bg']} 100%);
        border-bottom: 2px solid {THEME['green']};
        padding: 16px 24px;
        margin-bottom: 24px;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Renders the top branding header with project name and tagline."""
    st.markdown(f"""
    <div class="fintech-header">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="font-size:36px;">🧠</div>
            <div>
                <h1 style="color:{THEME['green']}; margin:0; font-size:24px; font-weight:800; letter-spacing:2px;">
                    FINTECH555
                </h1>
                <p style="color:{THEME['subtext']}; margin:0; font-size:13px; font-style:italic;">
                    Decision Intelligence Platform · Post-Trade AI Analytics
                </p>
                <p style="color:{THEME['text']}; margin:2px 0 0 0; font-size:12px;">
                    "We don't analyze trades. We analyze panic, patience, and decision discipline — using AI."
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def inject_theme():
    """Alias for inject_css() — called by layout.py."""
    inject_css()