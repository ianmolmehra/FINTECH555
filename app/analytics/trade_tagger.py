"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/trade_tagger.py
Module 18: Trade Auto-Tagger — AI-generated behavioral tags per trade
Purpose: Scans every trade and attaches color-coded behavioral/performance tags.
         Creates a labeled trade history visible in an interactive dataframe.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
from config.settings import TAG_TAXONOMY, THEME


def tag_all_trades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tags every trade with one or more behavioral/performance labels.

    Concept: Rule-based classification — a deterministic decision tree applied
             to each trade's features. Similar to expert system reasoning.
    Each trade may receive multiple tags (M-to-M relationship).

    Tags are derived from precomputed features in the dataframe,
    so this function assumes engineer_features() has already run.
    """
    df = df.copy()
    df["tags"] = [[] for _ in range(len(df))]

    # ── Compute thresholds from the full dataset for relative comparisons
    pnl_top5  = df["pnl"].quantile(0.95)     # Top 5% PnL threshold
    pnl_bot5  = df["pnl"].quantile(0.05)     # Bottom 5% PnL threshold
    avg_cap   = df["capital_deployed"].mean()

    for idx in df.index:
        row = df.loc[idx]
        tags = []

        # ── Tag: Clean Win — profitable, no behavioral flags
        if row["pnl"] > 0 and row.get("is_panic", 0) == 0 and row.get("is_revenge", 0) == 0:
            tags.append("✅ Clean Win")

        # ── Tag: Diamond Hold — held > 30 days and profitable
        if row.get("hold_days", 0) > 30 and row["pnl"] > 0:
            tags.append("💎 Diamond Hold")

        # ── Tag: Quick Strike — profitable in < 3 days
        if 0 <= row.get("hold_days", 0) <= 3 and row["pnl"] > 0:
            tags.append("⚡ Quick Strike")

        # ── Tag: Panic Exit — same-day exit with a loss
        if row.get("is_panic", 0) == 1:
            tags.append("😨 Panic Exit")

        # ── Tag: Revenge Trade — entered after a loss
        if row.get("is_revenge", 0) == 1:
            tags.append("🔁 Revenge Trade")

        # ── Tag: Oversized — capital > 1.8x average
        if row.get("is_oversized", 0) == 1:
            tags.append("📏 Oversized")

        # ── Tag: Premature Exit — short hold on small loss (could have recovered)
        if 1 <= row.get("hold_days", 0) <= 3 and -3 < row.get("pnl_pct", -10) < 0:
            tags.append("📉 Premature Exit")

        # ── Tag: Best Trade — top 5% PnL in the dataset
        if row["pnl"] >= pnl_top5:
            tags.append("🏆 Best Trade")

        # ── Tag: Worst Trade — bottom 5% PnL in the dataset
        if row["pnl"] <= pnl_bot5:
            tags.append("💀 Worst Trade")

        # ── Tag: Recovery Trade — first win after a loss streak
        if row.get("is_after_loss", 0) == 1 and row["is_profit"] == 1:
            tags.append("🔄 Recovery Trade")

        df.at[idx, "tags"] = tags

    # ── Convert list of tags to display string
    df["tags_display"] = df["tags"].apply(lambda t: "  ".join(t) if t else "—")
    return df


def render_trade_tagger_module(df: pd.DataFrame):
    """Renders Module 18 — interactive color-coded trade history with tag badges."""
    st.markdown("### 🏷️ Trade Auto-Tagger — AI-Labeled History")

    tagged_df = tag_all_trades(df)

    # ── TAG FREQUENCY SUMMARY
    all_tags = [tag for tags in tagged_df["tags"] for tag in tags]
    from collections import Counter
    tag_counts = Counter(all_tags)

    if tag_counts:
        tag_cols = st.columns(min(len(tag_counts), 5))
        for i, (tag, count) in enumerate(tag_counts.most_common(5)):
            color = TAG_TAXONOMY.get(tag, THEME["text"])
            tag_cols[i % 5].markdown(
                f'<div style="background:{color}22; border:1px solid {color}; '
                f'border-radius:8px; padding:8px; text-align:center">'
                f'<span style="color:{color}">{tag}</span><br>'
                f'<b style="color:{THEME["text"]}">{count} trades</b></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── TAG FILTER
    all_tag_names = list(TAG_TAXONOMY.keys())
    selected_tag = st.selectbox("🔍 Filter by tag:", ["All Tags"] + all_tag_names)

    if selected_tag != "All Tags":
        filtered = tagged_df[tagged_df["tags"].apply(lambda t: selected_tag in t)]
    else:
        filtered = tagged_df

    # ── INTERACTIVE DATAFRAME
    display_cols = ["symbol", "entry_date", "hold_days", "pnl", "pnl_pct", "tags_display"]
    available_display = [c for c in display_cols if c in filtered.columns]

    display_df = filtered[available_display].copy()
    if "pnl" in display_df.columns:
        display_df["pnl"] = display_df["pnl"].apply(lambda x: f"₹{x:,.0f}")
    if "pnl_pct" in display_df.columns:
        display_df["pnl_pct"] = display_df["pnl_pct"].apply(lambda x: f"{x:.2f}%")

    st.dataframe(display_df, use_container_width=True, height=420, hide_index=True)
    st.caption(f"Showing {len(filtered)} of {len(tagged_df)} trades")


# ── Alias: report.py calls compute_trade_tags(df, dis, panic, kelly)
def compute_trade_tags(df, dis=None, panic=None, kelly=None):
    """
    Alias for tag_all_trades() with enriched context from other modules.
    Passes dis, panic, kelly context for more accurate tagging.
    """
    # Tag all trades using rule-based taxonomy
    tagged = tag_all_trades(df)
    # Gather unique tags for filter UI
    all_tags = []
    if "tags" in tagged.columns:
        for tag_list in tagged["tags"].dropna():
            all_tags.extend(str(tag_list).split(","))
        all_tags = list(set(t.strip() for t in all_tags if t.strip()))
    return {"tagged_df": tagged, "all_tags": all_tags}
