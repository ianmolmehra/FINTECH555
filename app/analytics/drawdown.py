"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/drawdown.py
Module 11: Drawdown Analysis — Peak-to-Trough Risk Assessment
Purpose: Computes maximum drawdown, duration, Calmar Ratio, and rolling drawdown.
         Used by all professional hedge funds as a primary risk metric.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from config.settings import THEME


def compute_drawdown(df: pd.DataFrame) -> dict:
    """
    Computes all drawdown metrics from the cumulative equity curve.

    Concept: Maximum Drawdown — measures worst peak-to-trough loss.
    Formula: MaxDD = (Peak_Value - Trough_Value) / Peak_Value × 100
    This is the single most important risk metric used by institutional funds.

    Concept: Calmar Ratio — annualized return divided by max drawdown.
    Formula: Calmar = Annual_Return / |Max_Drawdown|
    Higher Calmar = better risk-adjusted performance.
    """
    # ── Build equity curve — cumulative sum of PnL over time
    equity = df["pnl"].cumsum().values
    peak_equity = np.maximum.accumulate(equity)  # Running maximum (peak at each point)

    # ── Drawdown at each point: (peak - current) / peak
    # Formula: DD(t) = (Peak(t) - Equity(t)) / Peak(t)
    # Avoid division by zero when equity is 0 at start
    with np.errstate(invalid="ignore", divide="ignore"):
        drawdown_series = np.where(peak_equity != 0,
                                   (peak_equity - equity) / peak_equity * 100, 0)

    max_dd = round(float(drawdown_series.max()), 2)   # Maximum Drawdown %
    max_dd_idx = int(np.argmax(drawdown_series))       # Index of worst drawdown trough

    # ── Find peak index before the trough (start of worst drawdown)
    peak_idx = int(np.argmax(equity[:max_dd_idx + 1]))

    # ── Drawdown Duration: number of trading days from peak to recovery
    # Recovery = first point where equity exceeds peak value again
    recovery_idx = None
    peak_val = equity[peak_idx]
    for i in range(max_dd_idx, len(equity)):
        if equity[i] >= peak_val:
            recovery_idx = i
            break
    duration_days = (recovery_idx - peak_idx) if recovery_idx else (len(equity) - peak_idx)

    # ── Calmar Ratio: annualized return / max drawdown
    # Formula: Calmar = (Total_Return / N_days × 252) / MaxDD%
    n_days = len(df)
    total_return_pct = (equity[-1] - equity[0]) / abs(equity[0]) * 100 if equity[0] != 0 else 0
    annualized_return = total_return_pct * (252 / max(n_days, 1))
    calmar = round(annualized_return / max_dd, 2) if max_dd > 0 else float("inf")

    # ── Rolling 30-day drawdown for line chart
    equity_series = pd.Series(equity, index=df["entry_date"].values)
    rolling_peak = equity_series.rolling(30, min_periods=1).max()
    rolling_dd = ((rolling_peak - equity_series) / rolling_peak.replace(0, np.nan)) * 100

    return {
        "max_drawdown": max_dd,
        "max_dd_start_date": str(df["entry_date"].iloc[peak_idx])[:10],
        "max_dd_trough_date": str(df["entry_date"].iloc[max_dd_idx])[:10],
        "duration_days": int(duration_days),
        "recovered": recovery_idx is not None,
        "calmar_ratio": calmar,
        "annualized_return": round(annualized_return, 2),
        "equity_curve": equity,
        "drawdown_series": drawdown_series,
        "rolling_dd": rolling_dd,
        "dates": df["entry_date"].values,
    }


def render_drawdown_module(df: pd.DataFrame):
    """Renders Module 11 with equity curve, rolling drawdown chart, and Calmar gauge."""
    st.markdown("### 📉 Drawdown Analysis")
    dd = compute_drawdown(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Max Drawdown", f"{dd['max_drawdown']:.1f}%",
              delta="⚠️ High" if dd["max_drawdown"] > 20 else "✅ Acceptable", delta_color="inverse")
    c2.metric("Drawdown Duration", f"{dd['duration_days']} days")
    c3.metric("Calmar Ratio", f"{dd['calmar_ratio']:.2f}",
              help="Higher is better. > 1.0 = good risk-adjusted return")
    c4.metric("Recovery Status", "✅ Recovered" if dd["recovered"] else "⚠️ Still Underwater")

    # ── DUAL CHART: Equity Curve + Rolling Drawdown overlay
    fig = go.Figure()

    # Equity curve — area chart
    fig.add_trace(go.Scatter(
        x=list(range(len(dd["equity_curve"]))), y=dd["equity_curve"],
        fill="tozeroy",
        fillcolor=f"rgba(0,200,83,0.15)",
        line=dict(color=THEME["green"], width=2),
        name="Equity Curve (₹)",
        yaxis="y",
        hovertemplate="Trade %{x}<br>Equity: ₹%{y:,.0f}<extra></extra>",
    ))

    # Rolling drawdown — line on secondary axis
    fig.add_trace(go.Scatter(
        x=list(range(len(dd["drawdown_series"]))), y=-dd["drawdown_series"],
        line=dict(color=THEME["red"], width=1.5, dash="dot"),
        name="Drawdown %",
        yaxis="y2",
        hovertemplate="Trade %{x}<br>Drawdown: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title="Portfolio Equity Curve & Drawdown",
        paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
        font_color=THEME["text"], height=380,
        xaxis=dict(color=THEME["subtext"], title="Trade #"),
        yaxis=dict(color=THEME["green"], title="Equity (₹)"),
        yaxis2=dict(color=THEME["red"], title="Drawdown %",
                    overlaying="y", side="right", showgrid=False),
        legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    from explainability.xai import explain_drawdown
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_drawdown(dd, df)}")
    st.success(f"⚡ **Action:** Set a hard stop rule — if your portfolio drops {min(dd['max_drawdown']/2, 10):.0f}% from peak, take a mandatory 3-day trading break before re-evaluating your strategy.")


# ── Patch: ensure backward-compatible key names
# report.py uses "max_drawdown_pct"; original compute_drawdown uses "max_drawdown"
_original_compute_drawdown = compute_drawdown

def compute_drawdown(df):
    """
    Wrapper around drawdown computation.
    Adds 'max_drawdown_pct' alias for report.py compatibility.
    """
    result = _original_compute_drawdown(df)
    if "max_drawdown" in result and "max_drawdown_pct" not in result:
        result["max_drawdown_pct"] = result["max_drawdown"]  # Alias
    return result
