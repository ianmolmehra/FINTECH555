"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/upload/uploader.py
Purpose: Drag-and-drop CSV/Excel file upload handler.
         Accepts multiple broker formats, delegates to validator and parser.
         Also supports one-click local sample data loading for demos.
================================================================================
"""

import streamlit as st
import pandas as pd
from upload.validator import validate_dataframe
from upload.broker_parser import detect_and_parse_broker
from config.settings import THEME

# ─────────────────────────────────────────────────────────────────────────────
# 📁 Local Sample File Path
# Place your sample CSV or Excel file at this path inside the project:
#   FINTECH555/data/sample/sample_broker_report.csv
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_FILE_PATH = "data/sample/sample_broker_report.csv"
SAMPLE_FILE_NAME = "sample_broker_report.csv"


def _load_local_sample() -> pd.DataFrame | None:
    """
    Reads the bundled sample CSV from the local data/sample/ folder.
    Returns a raw DataFrame, or None if the file is missing.
    """
    try:
        df = pd.read_csv(SAMPLE_FILE_PATH)
        return df
    except FileNotFoundError:
        st.error(
            f"❌ Sample file not found at `{SAMPLE_FILE_PATH}`. "
            "Please place your sample CSV there and restart the app."
        )
        return None
    except Exception as e:
        st.error(f"❌ Could not read sample file: {e}")
        return None


def render_uploader() -> pd.DataFrame | None:
    """
    Render the Streamlit file uploader widget.
    Returns a validated, standardized DataFrame or None if no file uploaded yet.

    Concept: Single-entry point for all data ingestion.
    Pipeline: upload → broker detection → column mapping → validation → clean df

    Two input modes:
      1. User uploads their own CSV/Excel broker report
      2. User clicks 'Try with Sample Data' to load the bundled local sample
    """

    # ── Upload widget — accepts CSV and Excel formats from all major brokers
    uploaded_file = st.file_uploader(
        label="📂 Drop your trade history here (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        help="Supports Zerodha, Upstox, Groww, Angel One, ICICI Direct, and generic formats.",
        label_visibility="visible",
    )

    # ── Session state: track if sample mode is active
    if "load_sample" not in st.session_state:
        st.session_state["load_sample"] = False

    # ── If user uploads a real file, disable sample mode automatically
    if uploaded_file is not None:
        st.session_state["load_sample"] = False

    # ── Neither uploaded nor sample clicked → show placeholder
    if uploaded_file is None and not st.session_state["load_sample"]:
        _render_upload_placeholder()
        return None

    # ── Determine data source: local sample OR user upload
    if st.session_state["load_sample"]:
        raw_df = _load_local_sample()
        if raw_df is None:
            st.session_state["load_sample"] = False
            return None
        st.info(
            "📊 Using **Sample Report** — this is a demo trade history file. "
            "You can upload your own file anytime using the uploader above."
        )

    else:
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

    Shows two options:
      - ⬇️ Download Sample File  →  saves the sample CSV to user's machine
      - 🚀 Try with Sample Data  →  loads the sample directly into the app
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
        <hr style="border-color: {THEME['green']}33; margin: 20px 0;">
        <p style="color: {THEME['subtext']}; font-size: 13px;">
            Don't have a file handy? Use the sample report below 👇
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two side-by-side buttons for sample file options
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Download button — user saves the sample CSV to their own machine
        try:
            with open(SAMPLE_FILE_PATH, "r") as f:
                st.download_button(
                    label="⬇️ Download Sample File",
                    data=f.read(),
                    file_name=SAMPLE_FILE_NAME,
                    mime="text/csv",
                    use_container_width=True,
                    help="Save the sample CSV to your computer, then upload it above.",
                )
        except FileNotFoundError:
            st.warning(f"Sample file not found at `{SAMPLE_FILE_PATH}`")

    with col2:
        # One-click load — no download needed, loads directly into the pipeline
        if st.button(
            "🚀 Try with Sample Data",
            use_container_width=True,
            help="Instantly loads the bundled sample report — perfect for demos!",
        ):
            st.session_state["load_sample"] = True
            st.rerun()