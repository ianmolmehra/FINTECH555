"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/upload/uploader.py
Purpose: Drag-and-drop CSV/Excel file upload handler.
         Accepts multiple broker formats, delegates to validator and parser.
================================================================================
"""

import streamlit as st
import pandas as pd
from upload.validator import validate_dataframe
from upload.broker_parser import detect_and_parse_broker
from config.settings import THEME


def render_uploader() -> pd.DataFrame | None:
    """
    Render the Streamlit file uploader widget.
    Returns a validated, standardized DataFrame or None if no file uploaded yet.

    Concept: Single-entry point for all data ingestion.
    Pipeline: upload → broker detection → column mapping → validation → clean df
    """
    # ── Upload widget — accepts CSV and Excel formats from all major brokers
    uploaded_file = st.file_uploader(
        label="📂 Drop your trade history here (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        help="Supports Zerodha, Upstox, Groww, Angel One, ICICI Direct, and generic formats.",
        label_visibility="visible",
    )

    if uploaded_file is None:
        # ── Render placeholder UI when no file is loaded yet
        _render_upload_placeholder()
        return None

    # ── Read raw file into DataFrame based on file extension
    try:
        if uploaded_file.name.endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)    # CSV: use pandas read_csv
        else:
            raw_df = pd.read_excel(uploaded_file)  # Excel: use openpyxl engine
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        return None

    # ── Pass raw dataframe to broker parser — detects format and maps columns
    parsed_df, broker_name, mapping_info = detect_and_parse_broker(raw_df)

    if parsed_df is None:
        # ── Manual column mapping UI rendered inside broker_parser if detection fails
        return None

    # ── Display broker detection success banner
    st.success(f"✅ Detected: **{broker_name}** format — {len(parsed_df)} trades loaded.")

    if mapping_info:
        # ── Show column mapping details so user can verify correctness
        with st.expander("🔍 Column Mapping Details", expanded=False):
            for std_col, raw_col in mapping_info.items():
                st.write(f"• `{std_col}` ← `{raw_col}`")

    # ── Validate the parsed dataframe — type coercion, null handling, outlier flagging
    validated_df, warnings = validate_dataframe(parsed_df)

    if warnings:
        with st.expander(f"⚠️ {len(warnings)} Data Quality Warnings", expanded=False):
            for w in warnings:
                st.warning(w)

    return validated_df


def _render_upload_placeholder():
    """
    Renders an attractive placeholder card when no file is uploaded.
    Uses HTML injection to match the dark FinTech theme from settings.THEME.
    """
    st.markdown(f"""
    <div style="
        border: 2px dashed {THEME['green']};
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: {THEME['card_bg']};
        margin: 20px 0;
    ">
        <div style="font-size: 48px;">📊</div>
        <h2 style="color: {THEME['green']}; margin: 10px 0;">FINTECH555 — Decision Intelligence Platform</h2>
        <p style="color: {THEME['subtext']}; font-size: 16px;">
            Upload your broker trade history CSV or Excel file above.<br>
            <em>Zerodha · Upstox · Groww · Angel One · ICICI Direct · Generic</em>
        </p>
        <p style="color: {THEME['text']}; font-size: 14px; margin-top: 20px;">
            🔒 Your data never leaves your browser session. All analytics run locally.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sample data download for demo/testing purposes
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with open("data/sample/sample_broker_report.csv", "r") as f:
            st.download_button(
                label="⬇️ Download Sample Trade File",
                data=f.read(),
                file_name="sample_trades.csv",
                mime="text/csv",
                use_container_width=True,
            )
