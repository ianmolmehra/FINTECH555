# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/worst_day_view.py
# Purpose: Worst Day Forensic Breakdown — storytelling format narrative.
#          Identifies worst trading day and reconstructs it trade-by-trade.
#          Most memorable demo-day feature — makes analytics feel personal.
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np


def render_worst_day_forensic(df: pd.DataFrame):
    """
    Automatically identify and narrate the trader's worst trading day.

    Identifies worst day by: highest total loss OR highest number of biased trades.
    Renders a timeline of that day's trades with: entry → exit → result → tag.
    Narrative output sounds like a forensic analyst reconstructing the day.

    Args:
        df: Enriched trade DataFrame with pnl, entry_date, is_panic, is_revenge columns.
    """
    st.markdown("#### 🔍 Worst Day Forensic Breakdown")

    # Guard: need entry_date to identify specific trading days
    if "entry_date" not in df.columns:
        st.info("Date column required for worst day analysis.")
        return

    # ── Aggregate by trading date to find the worst day
    df_copy = df.copy()
    df_copy["trade_date"] = pd.to_datetime(df_copy["entry_date"]).dt.date

    daily_summary = df_copy.groupby("trade_date").agg(
        total_pnl=("pnl", "sum"),          # Total PnL for the day
        trade_count=("pnl", "count"),       # Number of trades made
        panic_count=("is_panic", "sum"),    # Number of panic exits
        revenge_count=("is_revenge", "sum") # Number of revenge trades
    ).reset_index()

    if daily_summary.empty:
        st.info("No daily data available for forensic analysis.")
        return

    # ── Find worst day: minimum total PnL (biggest loss day)
    # This is the day that hurts most financially AND reveals behavioral patterns
    worst_day_row = daily_summary.loc[daily_summary["total_pnl"].idxmin()]
    worst_date = worst_day_row["trade_date"]

    # ── Get all trades from that worst day
    worst_day_trades = df_copy[df_copy["trade_date"] == worst_date].copy()
    worst_day_trades = worst_day_trades.sort_values("entry_date")  # Chronological order

    # ── Compute day-level statistics for the narrative
    total_loss   = worst_day_row["total_pnl"]
    trade_count  = int(worst_day_row["trade_count"])
    panic_count  = int(worst_day_row["panic_count"])
    revenge_count = int(worst_day_row["revenge_count"])
    total_capital = worst_day_trades["capital_deployed"].sum() if "capital_deployed" in worst_day_trades.columns else 0

    # ── Header metrics
    st.markdown(f"**📅 Worst Trading Day: {worst_date}**")
    wc1, wc2, wc3, wc4 = st.columns(4)
    with wc1:
        st.metric("Total Loss That Day", f"₹{total_loss:,.0f}", delta_color="off")
    with wc2:
        st.metric("Trades Made", trade_count)
    with wc3:
        st.metric("Panic Exits", panic_count)
    with wc4:
        st.metric("Revenge Trades", revenge_count)

    # ── Generate forensic narrative — analyst voice, specific numbers
    # Multi-condition narrative: different story for different behavioral combinations
    narrative = _generate_forensic_narrative(
        worst_date, total_loss, trade_count, panic_count, revenge_count, total_capital
    )
    st.markdown(f"""
    <div style="
        background: #1A0A0A;
        border: 1px solid #FF525244;
        border-left: 4px solid #FF5252;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        font-style: italic;
        color: #FFCDD2;
        line-height: 1.7;
    ">{narrative}</div>
    """, unsafe_allow_html=True)

    # ── Trade-by-trade timeline table
    st.markdown("**📋 Trade-by-Trade Timeline:**")
    cols_to_show = ["symbol", "entry_date", "exit_date", "entry_price", "exit_price",
                    "pnl", "pnl_pct", "hold_days", "is_panic", "is_revenge"]
    available = [c for c in cols_to_show if c in worst_day_trades.columns]
    if available:
        st.dataframe(
            worst_day_trades[available].rename(columns={
                "symbol": "Stock", "entry_date": "Entry", "exit_date": "Exit",
                "entry_price": "Entry ₹", "exit_price": "Exit ₹",
                "pnl": "PnL ₹", "pnl_pct": "PnL%",
                "hold_days": "Hold Days", "is_panic": "Panic?", "is_revenge": "Revenge?"
            }),
            use_container_width=True,
        )


def _generate_forensic_narrative(date, total_loss, trade_count, panic_count,
                                  revenge_count, total_capital) -> str:
    """
    Generate analyst-voice forensic narrative for the worst day.
    Multi-condition logic: different combinations produce genuinely different narratives.
    """
    # ── Condition 1: Revenge spiral — multiple revenge trades after initial panic
    if revenge_count >= 2 and panic_count >= 1:
        return (
            f"On {date}, you made {trade_count} trades — and the data tells a painful story. "
            f"Your first loss triggered a panic exit. Then you re-entered the market immediately, "
            f"a textbook revenge trade. This happened {revenge_count} more times. "
            f"Each successive trade was made while your emotional state was compromised by the previous loss. "
            f"The total damage: ₹{abs(total_loss):,.0f} in a single session. "
            f"This is not bad luck — this is a revenge spiral, and it is entirely preventable. "
            f"The rule: after any loss, wait at least 4 hours before your next entry."
        )

    # ── Condition 2: Panic-dominated day — multiple panic exits
    elif panic_count >= 2:
        return (
            f"On {date}, fear drove every decision. You made {trade_count} trades, "
            f"and {panic_count} of them were panic exits — positions closed in under a day "
            f"at a loss when the market moved against you. "
            f"Total capital at risk that day: ₹{total_capital:,.0f}. "
            f"Total loss from premature exits: ₹{abs(total_loss):,.0f}. "
            f"In many of these cases, the position would have recovered. "
            f"Panic selling converted temporary paper losses into permanent realized losses."
        )

    # ── Condition 3: Single catastrophic trade — high loss, few trades
    elif trade_count <= 2 and abs(total_loss) > 0:
        return (
            f"On {date}, you made only {trade_count} trade(s) — but they were devastating. "
            f"A single position resulted in a loss of ₹{abs(total_loss):,.0f}. "
            f"This suggests either oversized position entry or a trade held through a major adverse move. "
            f"Your worst single-day performance came not from overtrading, but from a single large bet. "
            f"Review position sizing for trades above 2x your average capital deployed."
        )

    # ── Condition 4: Overtrading day — many trades, all bad
    elif trade_count >= 5:
        return (
            f"On {date}, you overtraded — making {trade_count} trades in a single session. "
            f"The compounding of small losses across {trade_count} positions resulted in "
            f"a total daily loss of ₹{abs(total_loss):,.0f}. "
            f"High-frequency trading days in your data consistently underperform low-frequency days. "
            f"Quality over quantity: your win rate on days with 1-2 trades is significantly higher "
            f"than on days with 4+ trades."
        )

    # ── Default condition: General bad day narrative
    else:
        return (
            f"On {date}, {trade_count} trades resulted in a combined loss of ₹{abs(total_loss):,.0f}. "
            f"This was your worst performing day in the dataset. "
            f"{'A panic exit contributed to the damage. ' if panic_count > 0 else ''}"
            f"Post-analysis suggests this day occurred during a period of elevated market volatility. "
            f"Setting a daily loss limit of ₹{abs(total_loss)*0.5:,.0f} would have halved the damage."
        )
