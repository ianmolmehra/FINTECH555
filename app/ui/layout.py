# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/layout.py
# Purpose: Top-level Streamlit page structure, sidebar, Watchlist Intelligence,
#          and the master render_layout() entry-point called by main.py.
# =============================================================================

import streamlit as st
import pandas as pd

# ── Import config constants — THEME colors, NSE sector symbol map
from config.settings import NSE_SECTOR_MAP, THEME

# ── Import theme CSS injector
from ui.theme import inject_theme

# ── Import the drag-and-drop uploader (handles all broker formats)
from upload.uploader import render_uploader

# ── Import the master report renderer (orchestrates all 19+ modules)
from ui.report import render_report


def render_sidebar(sector_stats: pd.DataFrame = None) -> dict:
    """
    Render sidebar with branding and Watchlist Intelligence.
    Watchlist: user pastes NSE symbols → matched against historical sector win-rate.
    No API needed — NSE_SECTOR_MAP is a hardcoded dict of top-100 NSE symbols.
    """
    with st.sidebar:
        st.markdown("# 🧠 FINTECH555")
        st.markdown("**Decision Intelligence Platform**")
        st.markdown("*Post-Trade AI Analytics*")
        st.divider()
        st.markdown("*\"We don't analyze trades. We analyze panic, patience, and decision discipline — using AI.\"*")
        st.divider()

        st.markdown("### 📋 Watchlist Intelligence")
        st.caption("Paste NSE symbols to see your historical edge:")

        watchlist_input = st.text_area(
            label="Symbols",
            placeholder="RELIANCE, TCS, HDFCBANK, INFY",
            height=80,
            key="watchlist_input",
            label_visibility="collapsed",
        )

        if watchlist_input:
            # Split comma-separated input into individual ticker symbols
            symbols = [s.strip().upper() for s in watchlist_input.split(",") if s.strip()]

            # Build sector → win_rate dict from historical data (if available)
            sector_wr = {}
            if sector_stats is not None and not sector_stats.empty:
                if "sector" in sector_stats.columns and "win_rate" in sector_stats.columns:
                    sector_wr = dict(zip(sector_stats["sector"], sector_stats["win_rate"]))

            st.markdown("**🔍 Sector Match Analysis:**")
            for sym in symbols[:12]:
                # Lookup sector from built-in NSE top-100 mapping dictionary
                sector = NSE_SECTOR_MAP.get(sym, "Unknown")
                wr = sector_wr.get(sector, None)

                if sector == "Unknown":
                    st.markdown(f"⚪ **{sym}** → *Not in NSE top-100 map*")
                elif wr is None:
                    st.markdown(f"⚪ **{sym}** → {sector} → *No history*")
                elif wr >= 60:
                    # Win rate ≥ 60% = strong historical edge in this sector
                    st.markdown(f"🟢 **{sym}** → {sector} → {wr:.0f}% → **STRONG MATCH**")
                elif wr >= 45:
                    # Win rate 45-59% = neutral sector
                    st.markdown(f"🟡 **{sym}** → {sector} → {wr:.0f}% → **NEUTRAL**")
                else:
                    # Win rate < 45% = weak match; trader loses money here
                    st.markdown(f"🔴 **{sym}** → {sector} → {wr:.0f}% → **WEAK MATCH**")

        st.divider()
        st.markdown("✅ **Phase 1:** Rule-based XAI active")
        st.markdown("🔧 **Phase 2:** LLM API — *see api_integration/*")
        st.divider()
        try:
            with open("data/sample/sample_broker_report.csv", "r") as f:
                st.download_button("⬇️ Download Sample CSV", data=f.read(),
                                   file_name="sample_trades.csv", mime="text/csv",
                                   use_container_width=True)
        except Exception:
            st.caption("Sample: data/sample/sample_broker_report.csv")
        st.divider()
        st.caption("FINTECH555 © 2025 — Not investment advice.")
    return {}


def render_hero():
    """Render branded hero header with feature badges."""
    st.markdown("""
    <div style="text-align:center; padding:28px 20px 18px; background:linear-gradient(135deg,#060D06,#0D1F0D);
         border-radius:16px; border:1px solid #00C85333; margin-bottom:1.5rem;">
        <h1 style="font-size:2.8rem; color:#00C853; font-weight:900; letter-spacing:0.08em; margin:0;">
            🧠 FINTECH555
        </h1>
        <h3 style="color:#81C784; font-weight:400; margin:6px 0 4px;">Decision Intelligence Platform</h3>
        <p style="color:#4CAF50; font-style:italic; font-size:1rem; margin:0;">
            "We don't analyze trades. We analyze panic, patience, and decision discipline — using AI."
        </p>
        <div style="margin-top:12px;">
            <span style="background:#00C85322;color:#00C853;border:1px solid #00C85344;
                  padding:3px 10px;border-radius:20px;font-size:0.78rem;margin:0 4px;">
                19 Analytics Modules
            </span>
            <span style="background:#FFD60022;color:#FFD600;border:1px solid #FFD60044;
                  padding:3px 10px;border-radius:20px;font-size:0.78rem;margin:0 4px;">
                12+ ML Concepts
            </span>
            <span style="background:#1A88FF22;color:#64B5F6;border:1px solid #1A88FF44;
                  padding:3px 10px;border-radius:20px;font-size:0.78rem;margin:0 4px;">
                XAI Explainability
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_layout():
    """
    Master entry point called by main.py.
    Flow: theme → hero → sidebar → uploader → (if data) full analytics report.
    """
    # Step 1: Inject dark FinTech CSS theme into the Streamlit page
    inject_theme()

    # Step 2: Render the branded hero header
    render_hero()

    # Step 3: Render sidebar (placeholder — no sector data yet before file upload)
    render_sidebar(sector_stats=None)

    # Step 4: Drag-and-drop file uploader — handles multi-broker format detection
    # Returns standardized validated DataFrame or None if no file uploaded
    df = render_uploader()

    # Step 5: Run analytics only after a valid file is successfully uploaded
    if df is not None and len(df) >= 3:
        # Run the full 19-module analytics pipeline and render tabbed report
        render_report(df)
    elif df is not None and len(df) > 0:
        st.warning(f"⚠️ Only {len(df)} trades detected. Upload at least 3 trades for meaningful analytics.")
    elif df is not None:
        st.error("❌ No valid trades found. Please check the file format matches a supported broker.")
