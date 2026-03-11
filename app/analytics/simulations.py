"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/simulations.py
Module 3: Patience Gap Simulator — Monte Carlo Alternate Reality
Purpose: Uses Geometric Brownian Motion to simulate what would have happened
         if the trader had held losing trades for 2, 5, 10, 15, or 30 more days.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from config.settings import MONTE_CARLO, THEME


def simulate_patience_gap(df: pd.DataFrame) -> dict:
    """
    Monte Carlo simulation using Geometric Brownian Motion (GBM).
    Simulates alternative PnL outcomes if losing trades were held longer.

    Concept: Geometric Brownian Motion — stochastic process for price simulation.
    Formula: S(t) = S(0) × exp((μ - σ²/2)t + σ√t × Z)
    Where:
        μ = drift (mean log return estimated from data)
        σ = volatility (std of log returns)
        Z ~ N(0,1) = standard normal random variable (Wiener process increment)
    """
    losing_trades = df[df["is_profit"] == 0].copy()
    if len(losing_trades) == 0:
        return {"error": "No losing trades found — nothing to simulate!"}

    # ── Estimate GBM parameters from all trade log returns
    # μ (drift) = mean of log returns across all trades
    mu = df["log_return"].mean() if "log_return" in df.columns else -0.002
    # σ (volatility) = std of log returns — measures price uncertainty
    sigma = df["log_return"].std() if "log_return" in df.columns else 0.025

    n_sims = MONTE_CARLO["simulations"]   # 1000 simulation paths per scenario
    results = {}

    for extra_days in MONTE_CARLO["extension_days"]:
        simulated_pnls = []

        for _, trade in losing_trades.iterrows():
            S0 = trade["exit_price"]     # Start from current exit price (counterfactual)
            qty = trade["quantity"]
            t = extra_days / 252         # Convert days to years (252 trading days/year)

            # ── GBM simulation: vectorized across n_sims paths
            # Z ~ N(0,1): standard normal shock (Wiener process)
            Z = np.random.standard_normal(n_sims)
            # GBM price formula: S(t) = S(0) × exp((μ - σ²/2)t + σ√t × Z)
            # The (μ - σ²/2) term is Ito's lemma correction for the log-normal process
            S_t = S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * np.sqrt(t) * Z)

            # ── Simulated PnL if trader had held extra_days more
            # pnl_extension = (simulated_price - exit_price) × quantity
            pnl_extension = (S_t - S0) * qty
            # Add the original (realized) loss to the extension gain
            original_loss = trade["pnl"]
            simulated_total_pnl = original_loss + pnl_extension
            simulated_pnls.append(np.mean(simulated_total_pnl))  # Expected value of PnL

        results[f"+{extra_days}d"] = {
            "avg_simulated_pnl": round(np.mean(simulated_pnls), 2),
            "pct_positive": round((np.array(simulated_pnls) > 0).mean() * 100, 1),
        }

    # ── Stop-loss comparison simulation
    stoploss_results = {}
    for sl_pct in MONTE_CARLO["stoploss_levels"]:
        # Stop-loss discipline: trader exits at sl_pct loss instead of waiting
        # Expected PnL improvement = (actual_loss - disciplined_loss) × count
        avg_loss = losing_trades["pnl"].mean()
        avg_capital = losing_trades["capital_deployed"].mean()
        disciplined_loss = avg_capital * sl_pct  # e.g., -2% of capital deployed
        stoploss_results[f"{int(sl_pct*100)}%"] = {
            "actual_avg_loss": round(avg_loss, 2),
            "disciplined_loss": round(disciplined_loss, 2),
            "savings": round(abs(disciplined_loss) - abs(avg_loss), 2),
        }

    return {
        "extension_scenarios": results,
        "stoploss_scenarios": stoploss_results,
        "actual_avg_loss": round(losing_trades["pnl"].mean(), 2),
        "losing_trades_count": len(losing_trades),
        "mu": round(mu, 4),
        "sigma": round(sigma, 4),
    }


def render_simulations_module(df: pd.DataFrame):
    """Renders Module 3 UI with butterfly chart comparing actual vs simulated PnL."""
    st.markdown("### ⏳ Patience Gap Simulator — Monte Carlo")
    sim = simulate_patience_gap(df)

    if "error" in sim:
        st.warning(sim["error"])
        return

    # ── KPI STRIP
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Losing Trades", sim["losing_trades_count"])
    c2.metric("Avg Loss (Actual)", f"₹{sim['actual_avg_loss']:,.0f}")
    c3.metric("GBM Drift (μ)", f"{sim['mu']:.4f}")
    c4.metric("GBM Volatility (σ)", f"{sim['sigma']:.4f}")

    # ── BUTTERFLY / DIVERGING BAR CHART: actual vs simulated per extension scenario
    scenarios = list(sim["extension_scenarios"].keys())
    actual_pnl = [sim["actual_avg_loss"]] * len(scenarios)
    simulated_pnl = [sim["extension_scenarios"][s]["avg_simulated_pnl"] for s in scenarios]
    pct_positive = [sim["extension_scenarios"][s]["pct_positive"] for s in scenarios]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Actual PnL (Realized)", x=scenarios, y=actual_pnl,
        marker_color=THEME["red"],
        hovertemplate="<b>%{x}</b><br>Actual: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Simulated PnL (If Held)", x=scenarios, y=simulated_pnl,
        marker_color=THEME["green"],
        hovertemplate="<b>%{x}</b><br>Simulated: ₹%{y:,.0f} | % positive: {pct_positive}<extra></extra>",
    ))
    fig.update_layout(
        title="Actual vs Simulated PnL — What If You Had Held?",
        barmode="group", paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
        font_color=THEME["text"], xaxis=dict(color=THEME["subtext"]),
        yaxis_title="Average PnL (₹)", height=350,
        legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── XAI EXPLANATION
    from explainability.xai import explain_simulations
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_simulations(sim, df)}")
    st.success(f"⚡ **Action:** Add a hard rule — never close a losing trade within the first {int(min(5, df['hold_days'].median()))} days unless it exceeds your pre-defined stop-loss level.")


# ── Aliases for report.py compatibility
def patience_gap_simulation(df):
    """Alias for simulate_patience_gap() — called by report.py."""
    return simulate_patience_gap(df)

def alternate_exit_simulation(df):
    """Secondary simulation (stop-loss comparison). Returns empty dict if not implemented."""
    return {"scenario_pnl": {}}
