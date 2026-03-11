"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/kelly_criterion.py
Module 15: Kelly Criterion — Mathematically Optimal Position Sizing
Purpose: Computes the fraction of capital to risk per trade that maximizes
         long-term portfolio growth. Used by Renaissance Technologies, Buffett.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from config.settings import KELLY, THEME


def compute_kelly(df: pd.DataFrame) -> dict:
    """
    Computes the Kelly Criterion and adherence score.

    Formula: f* = (b×p - q) / b
    Where:
        f* = optimal fraction of capital to risk per trade
        b  = average_win / average_loss  (win-to-loss ratio)
        p  = historical win probability
        q  = historical loss probability = 1 - p

    Derivation: Kelly maximizes E[log(wealth)] — the geometric mean growth rate.
    This is optimal because compound growth depends on log of wealth, not linear wealth.

    Half-Kelly (f*/2): Industry standard for retail traders — reduces variance by 75%
    while retaining about 75% of the optimal growth rate. Safer for volatile outcomes.
    """
    total = len(df)
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]

    if len(wins) == 0 or len(losses) == 0:
        return {"error": "Need both winning and losing trades to compute Kelly Criterion."}

    p = len(wins) / total          # Win probability
    q = 1 - p                      # Loss probability

    avg_win  = wins["pnl"].mean()      # Average winning trade PnL
    avg_loss = abs(losses["pnl"].mean())  # Average losing trade PnL (positive value)

    # ── Win-to-Loss Ratio: b = avg win amount / avg loss amount
    b = avg_win / avg_loss if avg_loss > 0 else 1.0

    # ── Full Kelly Fraction: f* = (b×p - q) / b
    # This is the fraction of total capital to risk on each trade
    full_kelly = (b * p - q) / b

    # ── Apply safety cap from settings: max 40% even if Kelly says more
    full_kelly_capped = min(full_kelly, KELLY["max_full_kelly"])
    full_kelly_capped = max(0, full_kelly_capped)  # Kelly is 0 when edge is negative

    # ── Half-Kelly: standard practice — f*/2 reduces variance substantially
    half_kelly = full_kelly_capped * KELLY["half_kelly_factor"]

    # ── Actual average sizing fraction from trader's data
    avg_capital = df["capital_deployed"].mean()
    total_portfolio_proxy = df["capital_deployed"].sum() / len(df)  # Heuristic
    actual_fraction = avg_capital / (total_portfolio_proxy * 10) if total_portfolio_proxy > 0 else 0.1

    # ── Kelly Adherence Score: how close is actual sizing to Half-Kelly?
    # Perfect adherence = actual_fraction == half_kelly → score = 100
    deviation = abs(actual_fraction - half_kelly) / max(half_kelly, 0.01)
    adherence_score = max(0, 100 - deviation * 100)

    return {
        "win_prob": round(p * 100, 1),
        "win_loss_ratio": round(b, 2),
        "full_kelly": round(full_kelly * 100, 1),
        "full_kelly_capped": round(full_kelly_capped * 100, 1),
        "half_kelly": round(half_kelly * 100, 1),
        "actual_fraction": round(actual_fraction * 100, 1),
        "adherence_score": round(adherence_score, 1),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "overbetting": actual_fraction > half_kelly,
        "overbet_ratio": round(actual_fraction / max(half_kelly, 0.01), 2),
    }


def render_kelly_module(df: pd.DataFrame):
    """Renders Module 15 with Kelly vs actual sizing chart and gauge."""
    st.markdown("### 📐 Kelly Criterion — Optimal Position Sizing")
    kelly = compute_kelly(df)

    if "error" in kelly:
        st.warning(kelly["error"])
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Win Rate", f"{kelly['win_prob']:.1f}%")
    c2.metric("Win/Loss Ratio", f"{kelly['win_loss_ratio']:.2f}")
    c3.metric("Full Kelly", f"{kelly['full_kelly_capped']:.1f}%")
    c4.metric("Half-Kelly (Recommended)", f"{kelly['half_kelly']:.1f}%")
    c5.metric("Kelly Adherence", f"{kelly['adherence_score']:.0f}/100",
              delta="⚠️ Overbetting" if kelly["overbetting"] else "✅ Well-sized",
              delta_color="inverse" if kelly["overbetting"] else "normal")

    col1, col2 = st.columns([1, 1])

    with col1:
        # ── GAUGE: Kelly adherence score
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kelly["adherence_score"],
            number={"suffix": "/100", "font": {"color": THEME["text"], "size": 32}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": THEME["subtext"]},
                "bar": {"color": THEME["green"] if kelly["adherence_score"] >= 60 else THEME["amber"]},
                "bgcolor": THEME["card_bg"],
                "steps": [
                    {"range": [0, 40], "color": "#1A0A0A"},
                    {"range": [40, 70], "color": "#1A1A0A"},
                    {"range": [70, 100], "color": "#0A1A0A"},
                ],
            }
        ))
        fig.update_layout(paper_bgcolor=THEME["bg"], font_color=THEME["text"],
                          height=260, margin=dict(t=20,b=10,l=20,r=20),
                          title=dict(text="Kelly Adherence Score", font_color=THEME["text"]))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ── BAR COMPARISON: Full Kelly vs Half-Kelly vs Actual
        categories = ["Full Kelly", "Half-Kelly\n(Recommended)", "Your Actual\nSizing"]
        values = [kelly["full_kelly_capped"], kelly["half_kelly"], kelly["actual_fraction"]]
        colors_bar = [THEME["blue"], THEME["green"],
                      THEME["red"] if kelly["overbetting"] else THEME["green"]]
        fig2 = go.Figure(go.Bar(
            x=categories, y=values, marker_color=colors_bar,
            text=[f"{v:.1f}%" for v in values], textposition="outside",
            hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
        ))
        fig2.update_layout(title="Capital Sizing Comparison",
                           paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                           font_color=THEME["text"], yaxis_title="% of Capital",
                           height=260, margin=dict(t=30,b=10,l=10,r=10))
        st.plotly_chart(fig2, use_container_width=True)

    from explainability.xai import explain_kelly
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_kelly(kelly, df)}")
    if kelly["overbetting"]:
        st.success(f"⚡ **Action:** Reduce your average position size by {(kelly['actual_fraction'] - kelly['half_kelly']):.1f}% to align with Half-Kelly ({kelly['half_kelly']:.1f}%). Overbetting by {kelly['overbet_ratio']:.1f}x the optimal amount is inflating your volatility without improving expected returns.")
    else:
        st.success(f"⚡ **Action:** Your sizing is well-calibrated to Kelly principles. Consider slightly increasing position size in your {df.groupby('sector')['is_profit'].mean().idxmax()} sector where your edge is strongest.")


# ── Alias: report.py calls compute_kelly_criterion()
def compute_kelly_criterion(df):
    """Alias for compute_kelly() — called by report.py."""
    return compute_kelly(df)
