# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/main.py
# Purpose: Application entry point. Run with: streamlit run app/main.py
# Concept: Single-file entry point pattern — keeps startup logic minimal.
# =============================================================================

import streamlit as st  # Streamlit: Python web framework for data apps

# ── Page config MUST be the FIRST Streamlit call before any other st.* calls
# This sets the browser tab title, icon, and default layout mode
st.set_page_config(
    page_title="FINTECH555 — Decision Intelligence Platform",
    page_icon="🧠",
    layout="wide",                      # Wide layout: uses full browser width
    initial_sidebar_state="expanded",   # Sidebar open by default for watchlist
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": (
            "**FINTECH555 — Decision Intelligence Platform**\n\n"
            "Post-Trade AI Analytics · 6th Semester Major Project\n\n"
            "19 Modules · 12+ ML Concepts · XAI Layer · Multi-Broker Support\n\n"
            "*Not investment advice. All analytics for educational purposes only.*"
        ),
    }
)

# ── Import and call the master layout renderer after page config is set
# render_layout() handles: theme injection, hero, sidebar, upload, full report
from ui.layout import render_layout  # Top-level UI orchestrator

# ── Application entry point — render_layout() drives the entire app
render_layout()
