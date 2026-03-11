# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/progress_timeline.py
# Purpose: Horizontal behavioral evolution timeline — month-by-month dots.
#          Green = disciplined month (BHS > 70), Amber = mixed, Red = impulsive.
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def render_progress_timeline(df: pd.DataFrame, panic: dict):
    """
    Render month-by-month behavioral evolution timeline.

    Concept: Time-series visualization of Behavioral Health Score (BHS) trend.
    Each month is a dot on a horizontal timeline, color-coded by performance.
    Hover tooltip shows: win rate, panic rate, trade count, avg PnL per month.

    Args:
        df:    Enriched trade DataFrame with 'month', 'year', 'is_profit', 'pnl' columns.
        panic: Panic detection result dict (used for BHS baseline).
    """
    # Guard: need at least 3 months of data for a meaningful timeline
    if "month" not in df.columns or "year" not in df.columns:
        st.info("ℹ️ Timeline requires date columns in your trade data.")
        return

    # ── Aggregate trades by year-month period
    # Group by year and month to compute monthly behavioral metrics
    df["ym"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    monthly = df.groupby("ym").agg(
        trade_count=("is_profit", "count"),
        win_rate=("is_profit", "mean"),        # Win rate = mean of 0/1 profit flag
        avg_pnl=("pnl", "mean"),               # Average PnL per trade in this month
        panic_count=("is_panic", "sum"),       # Count of panic trades this month
    ).reset_index().sort_values("ym")

    if len(monthly) < 2:
        st.info("ℹ️ Upload at least 2 months of trades to see the progress timeline.")
        return

    # ── Compute Behavioral Health Score per month
    # BHS proxy: win_rate × 60 + (1 - panic_rate) × 40
    # This gives a 0-100 score where high win rate + low panic = high BHS
    monthly["panic_rate"] = monthly["panic_count"] / monthly["trade_count"].clip(lower=1)
    monthly["bhs"] = (monthly["win_rate"] * 60 + (1 - monthly["panic_rate"]) * 40).round(1)

    # ── Assign color per month based on BHS thresholds from spec
    def month_color(bhs_val):
        """Color mapping: BHS > 70 = green disciplined, 40-70 = amber mixed, < 40 = red impulsive."""
        if bhs_val > 70:   return "#00C853"   # Green: disciplined month
        elif bhs_val > 40: return "#FFD600"   # Amber: mixed performance
        else:              return "#FF5252"   # Red: impulsive / poor month

    monthly["color"] = monthly["bhs"].apply(month_color)

    # ── Build Plotly timeline scatter plot
    # X axis = time, Y axis = BHS score, dot size = trade count, color = performance
    fig = go.Figure()

    # Connecting line (faint) to show trajectory
    fig.add_trace(go.Scatter(
        x=monthly["ym"],
        y=monthly["bhs"],
        mode="lines",
        line=dict(color="#1B2B1B", width=2),  # Background connecting line
        showlegend=False,
    ))

    # Monthly dots with hover tooltips
    for _, row in monthly.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["ym"]],
            y=[row["bhs"]],
            mode="markers+text",
            marker=dict(
                size=max(12, row["trade_count"] * 3),  # Dot size scales with trade count
                color=row["color"],
                line=dict(color="#0A0F0A", width=2),
            ),
            text=[f"{row['bhs']:.0f}"],  # BHS score label on dot
            textposition="top center",
            textfont=dict(color=row["color"], size=10),
            hovertemplate=(
                f"<b>{row['ym']}</b><br>"
                f"BHS: {row['bhs']:.1f}/100<br>"
                f"Win Rate: {row['win_rate']*100:.1f}%<br>"
                f"Panic Rate: {row['panic_rate']*100:.1f}%<br>"
                f"Trades: {row['trade_count']}<br>"
                f"Avg PnL: ₹{row['avg_pnl']:,.0f}<extra></extra>"
            ),
            showlegend=False,
        ))

    # BHS reference zones (background shading)
    fig.add_hrect(y0=70, y1=100, fillcolor="#00C853", opacity=0.06, line_width=0)  # Green zone
    fig.add_hrect(y0=40, y1=70,  fillcolor="#FFD600", opacity=0.06, line_width=0)  # Amber zone
    fig.add_hrect(y0=0,  y1=40,  fillcolor="#FF5252", opacity=0.06, line_width=0)  # Red zone

    fig.update_layout(
        title="📈 Behavioral Health Score — Monthly Progress Timeline",
        template="plotly_dark",
        paper_bgcolor="#0A0F0A",
        plot_bgcolor="#0A0F0A",
        font=dict(color="#E8F5E9"),
        xaxis_title="Month",
        yaxis_title="Behavioral Health Score (0-100)",
        yaxis=dict(range=[0, 105], gridcolor="#1B2B1B"),
        height=300,
        margin=dict(l=40, r=40, t=50, b=40),
    )

    st.markdown("#### 📈 Behavioral Progress Timeline")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Green dots = disciplined months (BHS > 70) · Amber = mixed · Red = impulsive. Dot size = trade count.")
