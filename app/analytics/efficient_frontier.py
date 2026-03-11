"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/efficient_frontier.py
Module 17: Efficient Frontier — Markowitz Mean-Variance Portfolio Optimization
Purpose: Shows optimal sector allocation to maximize return for a given risk level.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy.optimize import minimize
from config.settings import FRONTIER, THEME


def compute_efficient_frontier(df: pd.DataFrame) -> dict:
    """
    Markowitz Mean-Variance Optimization applied to trader's sector allocations.

    Concept: Efficient Frontier — set of optimal portfolios offering highest return
             for a given variance (or lowest risk for a given return).

    Portfolio Return: E[Rp] = Σ(w_i × E[R_i])  — weighted average of sector returns.
    Portfolio Variance: Var(Rp) = w' × Σ × w    — quadratic form of covariance matrix.
    Where Σ = sector return covariance matrix, w = vector of sector weights.

    Solved via scipy.optimize.minimize — quadratic programming (QP) solver.
    Constraint: weights sum to 1.0 (fully invested). Bounds: [0.05, 0.60] per sector.
    """
    # ── Build sector return series: monthly average return per sector
    df_temp = df.copy()
    df_temp["month"] = df_temp["entry_date"].dt.to_period("M")

    sector_monthly = df_temp.groupby(["month","sector"])["pnl_pct"].mean().unstack()
    sector_monthly = sector_monthly.dropna(how="all").fillna(0)

    # Filter sectors with enough data
    valid_sectors = [col for col in sector_monthly.columns
                     if (sector_monthly[col] != 0).sum() >= FRONTIER["min_trades_per_sector"]]

    if len(valid_sectors) < FRONTIER["min_sectors"]:
        return {
            "insufficient_data": True,
            "sectors_found": len(valid_sectors),
            "sectors_needed": FRONTIER["min_sectors"],
        }

    sector_returns = sector_monthly[valid_sectors]
    mu = sector_returns.mean().values      # Expected returns vector
    Sigma = sector_returns.cov().values    # Covariance matrix Σ
    n = len(valid_sectors)

    # ── Generate random portfolios to plot the frontier cloud
    # Monte Carlo portfolio simulation: 5000 random weight vectors
    results = {"returns": [], "risks": [], "sharpes": [], "weights": []}
    for _ in range(FRONTIER["num_portfolios"]):
        w = np.random.dirichlet(np.ones(n))  # Random weights summing to 1
        w = np.clip(w, FRONTIER["weight_min"], FRONTIER["weight_max"])
        w /= w.sum()  # Re-normalize after clipping
        ret = mu @ w                         # E[Rp] = μ' w
        risk = np.sqrt(w @ Sigma @ w)        # σ_p = √(w' Σ w)
        sharpe = ret / risk if risk > 0 else 0
        results["returns"].append(ret)
        results["risks"].append(risk)
        results["sharpes"].append(sharpe)
        results["weights"].append(w)

    # ── Minimum Variance Portfolio: minimize portfolio variance
    def portfolio_variance(w): return w @ Sigma @ w
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(FRONTIER["weight_min"], FRONTIER["weight_max"])] * n
    w0 = np.ones(n) / n

    mv_result = minimize(portfolio_variance, w0, method="SLSQP",
                         bounds=bounds, constraints=constraints)
    mv_weights = mv_result.x / mv_result.x.sum()
    mv_return = mu @ mv_weights
    mv_risk = np.sqrt(mv_weights @ Sigma @ mv_weights)

    # ── Maximum Sharpe Portfolio: maximize Sharpe ratio
    def neg_sharpe(w):
        ret = mu @ w
        risk = np.sqrt(w @ Sigma @ w)
        return -ret / risk if risk > 0 else 0
    ms_result = minimize(neg_sharpe, w0, method="SLSQP",
                         bounds=bounds, constraints=constraints)
    ms_weights = ms_result.x / ms_result.x.sum()
    ms_return = mu @ ms_weights
    ms_risk = np.sqrt(ms_weights @ Sigma @ ms_weights)

    # ── Actual portfolio (equal weight in traded sectors as proxy)
    actual_weights = np.ones(n) / n
    actual_return = mu @ actual_weights
    actual_risk = np.sqrt(actual_weights @ Sigma @ actual_weights)

    return {
        "insufficient_data": False,
        "sectors": valid_sectors,
        "cloud_returns": results["returns"],
        "cloud_risks": results["risks"],
        "cloud_sharpes": results["sharpes"],
        "mv_return": mv_return, "mv_risk": mv_risk, "mv_weights": mv_weights.tolist(),
        "ms_return": ms_return, "ms_risk": ms_risk, "ms_weights": ms_weights.tolist(),
        "actual_return": actual_return, "actual_risk": actual_risk,
    }


def render_efficient_frontier_module(df: pd.DataFrame):
    """Renders Module 17 with scatter frontier plot and portfolio comparison."""
    st.markdown("### 📊 Efficient Frontier — Markowitz Portfolio Theory")
    ef = compute_efficient_frontier(df)

    if ef.get("insufficient_data"):
        st.info(f"📚 Efficient Frontier requires {ef['sectors_needed']} sectors with sufficient data. You have {ef['sectors_found']} qualifying sectors.\n\nThis module will activate once you have more diversified trade history.")
        st.markdown("""**What this module would show:**
        The Efficient Frontier plots every possible combination of your sector allocations.
        Each point is a portfolio with a specific risk level (X-axis) and expected return (Y-axis).
        The curve at the top-left is the 'efficient frontier' — where you get maximum return for each level of risk.
        """)
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Min Variance Portfolio Risk", f"{ef['mv_risk']:.3f}")
    c2.metric("Max Sharpe Portfolio Return", f"{ef['ms_return']:.3f}%")
    c3.metric("Your Actual Portfolio Risk", f"{ef['actual_risk']:.3f}")

    # ── EFFICIENT FRONTIER SCATTER PLOT
    fig = go.Figure()
    # Portfolio cloud
    fig.add_trace(go.Scatter(
        x=ef["cloud_risks"], y=ef["cloud_returns"], mode="markers",
        marker=dict(color=ef["cloud_sharpes"], colorscale="RdYlGn",
                    size=4, opacity=0.4, colorbar=dict(title="Sharpe")),
        name="Portfolio Cloud",
        hovertemplate="Risk: %{x:.3f}<br>Return: %{y:.3f}%<extra></extra>",
    ))
    # Minimum Variance point
    fig.add_trace(go.Scatter(
        x=[ef["mv_risk"]], y=[ef["mv_return"]], mode="markers+text",
        marker=dict(color=THEME["blue"], size=14, symbol="star"),
        text=["Min Variance"], textposition="top center",
        name="Minimum Variance Portfolio",
    ))
    # Maximum Sharpe point
    fig.add_trace(go.Scatter(
        x=[ef["ms_risk"]], y=[ef["ms_return"]], mode="markers+text",
        marker=dict(color=THEME["amber"], size=14, symbol="star"),
        text=["Max Sharpe"], textposition="top center",
        name="Maximum Sharpe Portfolio",
    ))
    # Actual portfolio point
    fig.add_trace(go.Scatter(
        x=[ef["actual_risk"]], y=[ef["actual_return"]], mode="markers+text",
        marker=dict(color=THEME["red"], size=14, symbol="x"),
        text=["Your Portfolio"], textposition="top center",
        name="Your Actual Allocation",
    ))

    fig.update_layout(
        title="Efficient Frontier — Optimal Sector Allocation",
        paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
        font_color=THEME["text"], xaxis_title="Portfolio Risk (Std Dev)",
        yaxis_title="Expected Return (%)", height=420,
        legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    from explainability.xai import explain_frontier
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_frontier(ef, df)}")
    ms_sectors = dict(zip(ef["sectors"], [f"{w*100:.1f}%" for w in ef["ms_weights"]]))
    st.success(f"⚡ **Action:** The Maximum Sharpe Portfolio suggests: {ms_sectors}. Gradually shift your actual sector allocation toward these proportions over your next 10 trades.")
