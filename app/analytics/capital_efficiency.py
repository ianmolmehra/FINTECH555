"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/capital_efficiency.py
Module 14: Capital Efficiency Curve — Are bigger bets producing better returns?
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy import stats
from config.settings import THEME


def compute_capital_efficiency(df: pd.DataFrame) -> dict:
    """
    Measures the relationship between capital deployed and returns.

    Concept: OLS Regression — finds the best-fit line through capital vs PnL% scatter.
    Formula: β = (X'X)^{-1} X'y  — normal equation for ordinary least squares.
    Minimizes: Σ(y_i - ŷ_i)² — sum of squared residuals.

    Concept: Pearson Correlation Coefficient.
    Formula: r = cov(X,Y) / (σ_X × σ_Y) — measures linear relationship strength.
    Interpretation: r near 0 = capital size not rewarded with better returns.
    """
    X = df["capital_deployed"].values
    Y = df["pnl_pct"].fillna(0).values

    # ── Pearson correlation between capital deployed and return %
    r, p_corr = stats.pearsonr(X, Y) if len(X) > 2 else (0, 1)

    # ── OLS Regression: fit line through capital vs pnl%
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)

    # ── Capital Efficiency Score: based on correlation strength and direction
    # Positive r with high significance = capital is being deployed efficiently
    efficiency_score = max(0, min(100, r * 100 + 50))  # Center at 50

    # ── Identify optimal capital band (quartile with highest win rate)
    q1, q2, q3 = df["capital_deployed"].quantile([0.25, 0.50, 0.75])
    bands = {
        f"< ₹{q1:,.0f}": df[df["capital_deployed"] <= q1],
        f"₹{q1:,.0f}–₹{q2:,.0f}": df[(df["capital_deployed"] > q1) & (df["capital_deployed"] <= q2)],
        f"₹{q2:,.0f}–₹{q3:,.0f}": df[(df["capital_deployed"] > q2) & (df["capital_deployed"] <= q3)],
        f"> ₹{q3:,.0f}": df[df["capital_deployed"] > q3],
    }
    band_wr = {band: band_df["is_profit"].mean() * 100 for band, band_df in bands.items() if len(band_df) > 0}
    optimal_band = max(band_wr, key=band_wr.get) if band_wr else "N/A"

    return {
        "pearson_r": round(float(r), 3),
        "p_value": round(p_value, 4),
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "efficiency_score": round(efficiency_score, 1),
        "optimal_band": optimal_band,
        "band_wr": {k: round(v,1) for k,v in band_wr.items()},
        "capital": X,
        "pnl_pct": Y,
    }


def render_capital_efficiency_module(df: pd.DataFrame):
    """Renders Module 14 with scatter plot, regression line, and band analysis."""
    st.markdown("### 💹 Capital Efficiency Curve")
    ce = compute_capital_efficiency(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pearson r", f"{ce['pearson_r']:.3f}",
              help="Near 0 = no relationship between capital and returns")
    c2.metric("Efficiency Score", f"{ce['efficiency_score']:.0f}/100")
    c3.metric("Optimal Capital Band", ce["optimal_band"])
    c4.metric("Statistical p-value", f"{ce['p_value']:.4f}")

    # ── SCATTER + OLS REGRESSION LINE
    X = ce["capital"]
    Y = ce["pnl_pct"]
    X_line = np.linspace(X.min(), X.max(), 100)
    Y_line = ce["slope"] * X_line + ce["intercept"]

    fig = go.Figure()
    colors = [THEME["green"] if y > 0 else THEME["red"] for y in Y]
    fig.add_trace(go.Scatter(
        x=X, y=Y, mode="markers",
        marker=dict(color=colors, size=8, opacity=0.7),
        name="Individual Trades",
        hovertemplate="Capital: ₹%{x:,.0f}<br>Return: %{y:.1f}%<extra></extra>",
    ))
    # OLS regression line
    fig.add_trace(go.Scatter(
        x=X_line, y=Y_line, mode="lines",
        line=dict(color=THEME["amber"], width=2, dash="dash"),
        name=f"OLS Line (r={ce['pearson_r']:.2f})",
    ))
    fig.add_hline(y=0, line_dash="solid", line_color=THEME["subtext"], line_width=1)
    fig.update_layout(
        title="Capital Deployed vs Return % — Are You Rewarded for Bigger Bets?",
        paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
        font_color=THEME["text"], xaxis_title="Capital Deployed (₹)",
        yaxis_title="Return %", height=380,
        legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    from explainability.xai import explain_capital_efficiency
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_capital_efficiency(ce, df)}")
    st.success(f"⚡ **Action:** Focus your highest-conviction trades in the **{ce['optimal_band']}** capital range where your win rate is {ce['band_wr'].get(ce['optimal_band'], 50):.0f}% — your empirically optimal sizing zone.")
