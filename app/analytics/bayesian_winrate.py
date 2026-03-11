"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/bayesian_winrate.py
Module 16: Bayesian Win Rate — Beta-Binomial Conjugate Model
Purpose: Updates win rate estimate as trades accumulate using Bayesian inference.
         Shows how statistical confidence grows with more data.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy.stats import beta as beta_dist
from config.settings import BAYESIAN, THEME


def compute_bayesian_winrate(df: pd.DataFrame) -> dict:
    """
    Bayesian win rate estimation using Beta-Binomial conjugate model.

    Concept: Beta Distribution as conjugate prior for Binomial likelihood.
    Prior: Beta(α=1, β=1) = Uniform distribution — no initial assumption about trader.
    Posterior: After N trades with W wins → Beta(α=1+W, β=1+(N-W))
    Formula: P(win_rate | data) = Beta(W+1, L+1)

    Mean of posterior = (W+1)/(N+2) — Laplace smoothing (avoids 0% or 100% estimates)
    This is more conservative than raw win rate, especially with few trades.

    Credible interval: 95% probability that true win rate lies in [lower, upper].
    Unlike frequentist CI, Bayesian CI has direct probability interpretation.
    """
    outcomes = df["is_profit"].values
    N = len(outcomes)
    W = int(outcomes.sum())   # Total wins
    L = N - W                 # Total losses

    alpha_prior = BAYESIAN["prior_alpha"]  # Beta(1,1) = uniform prior
    beta_prior  = BAYESIAN["prior_beta"]

    # ── Posterior parameters: update prior with observed data
    alpha_post = alpha_prior + W    # Alpha = prior + observed wins
    beta_post  = beta_prior  + L    # Beta  = prior + observed losses

    # ── Posterior mean: most likely win rate given evidence
    posterior_mean = alpha_post / (alpha_post + beta_post)

    # ── 95% Bayesian Credible Interval: P(θ ∈ CI | data) = 0.95
    # scipy.stats.beta.ppf = percent point function (inverse CDF)
    ci_level = BAYESIAN["credible_interval"]
    ci_lower = beta_dist.ppf((1 - ci_level) / 2, alpha_post, beta_post)
    ci_upper = beta_dist.ppf((1 + ci_level) / 2, alpha_post, beta_post)

    # ── Stability threshold: CI width < 5% means estimate has stabilized
    ci_width = ci_upper - ci_lower
    is_stable = ci_width < BAYESIAN["stability_threshold"]

    # ── How many more trades until stable? Estimate via formula
    # CI width ∝ 1/√N — need N such that 1/√N < 0.05 → N > 400
    # Approximate using current rate of CI narrowing
    trades_to_stability = max(0, int((ci_width / BAYESIAN["stability_threshold"])**2 * N - N))

    # ── Evolution of posterior mean trade-by-trade (for animated chart)
    posterior_evolution = []
    for i in range(1, N + 1):
        w_i = outcomes[:i].sum()
        l_i = i - w_i
        a_i = alpha_prior + w_i
        b_i = beta_prior  + l_i
        mean_i = a_i / (a_i + b_i)
        # 95% CI at step i
        ci_l = beta_dist.ppf(0.025, a_i, b_i)
        ci_u = beta_dist.ppf(0.975, a_i, b_i)
        posterior_evolution.append({"trade": i, "mean": mean_i, "ci_l": ci_l, "ci_u": ci_u})

    # ── Prior vs Posterior distribution (for comparison plot)
    theta_range = np.linspace(0.01, 0.99, 200)
    prior_pdf  = beta_dist.pdf(theta_range, alpha_prior, beta_prior)
    post_pdf   = beta_dist.pdf(theta_range, alpha_post,  beta_post)

    return {
        "posterior_mean": round(posterior_mean * 100, 1),
        "raw_win_rate": round(W / N * 100, 1),
        "ci_lower": round(ci_lower * 100, 1),
        "ci_upper": round(ci_upper * 100, 1),
        "ci_width": round(ci_width * 100, 1),
        "is_stable": is_stable,
        "trades_to_stability": trades_to_stability,
        "total_trades": N,
        "wins": W,
        "losses": L,
        "posterior_evolution": posterior_evolution,
        "theta_range": theta_range,
        "prior_pdf": prior_pdf,
        "post_pdf": post_pdf,
    }


def render_bayesian_module(df: pd.DataFrame):
    """Renders Module 16 with evolving win rate chart and prior vs posterior overlay."""
    st.markdown("### 🎲 Bayesian Win Rate Estimator")
    bw = compute_bayesian_winrate(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bayesian Win Rate", f"{bw['posterior_mean']:.1f}%",
              help="Posterior mean — more stable than raw win rate with few trades")
    c2.metric("95% Credible Interval", f"{bw['ci_lower']:.1f}% – {bw['ci_upper']:.1f}%")
    c3.metric("Estimate Stable?", "✅ Yes" if bw["is_stable"] else f"⏳ Need ~{bw['trades_to_stability']} more")
    c4.metric("Raw Win Rate", f"{bw['raw_win_rate']:.1f}%")

    col1, col2 = st.columns([1, 1])

    with col1:
        # ── WIN RATE EVOLUTION with credible interval band
        evo = bw["posterior_evolution"]
        trades = [e["trade"] for e in evo]
        means  = [e["mean"] * 100 for e in evo]
        ci_ls  = [e["ci_l"] * 100 for e in evo]
        ci_us  = [e["ci_u"] * 100 for e in evo]

        fig = go.Figure()
        # CI band (shaded area)
        fig.add_trace(go.Scatter(
            x=trades + trades[::-1], y=ci_us + ci_ls[::-1],
            fill="toself", fillcolor=f"rgba(0,200,83,0.15)",
            line=dict(width=0), name="95% Credible Interval",
        ))
        # Posterior mean line
        fig.add_trace(go.Scatter(
            x=trades, y=means, line=dict(color=THEME["green"], width=2),
            name="Posterior Win Rate",
            hovertemplate="Trade %{x}<br>Win Rate: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=50, line_dash="dash", line_color=THEME["amber"],
                      annotation_text="50% baseline")
        fig.update_layout(title="Win Rate Confidence Evolution",
                          paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                          font_color=THEME["text"], yaxis=dict(range=[0,100]),
                          height=300, legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ── PRIOR vs POSTERIOR distribution overlay
        theta = bw["theta_range"] * 100
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=theta, y=bw["prior_pdf"], fill="tozeroy",
                                   fillcolor=f"rgba(68,138,255,0.2)",
                                   line=dict(color=THEME["blue"]), name="Prior (Uniform)"))
        fig2.add_trace(go.Scatter(x=theta, y=bw["post_pdf"], fill="tozeroy",
                                   fillcolor=f"rgba(0,200,83,0.2)",
                                   line=dict(color=THEME["green"]), name="Posterior"))
        fig2.update_layout(title="Prior vs Posterior Win Rate Distribution",
                           paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                           font_color=THEME["text"], xaxis_title="Win Rate %",
                           yaxis_title="Probability Density", height=300,
                           legend=dict(bgcolor=THEME["bg"], font_color=THEME["text"]))
        st.plotly_chart(fig2, use_container_width=True)

    from explainability.xai import explain_bayesian
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_bayesian(bw, df)}")
    st.success(f"⚡ **Action:** You need approximately **{bw['trades_to_stability']}** more trades before this estimate stabilizes to within 5%. Until then, treat your {bw['posterior_mean']:.1f}% win rate as a range of {bw['ci_lower']:.1f}%–{bw['ci_upper']:.1f}%, and size positions conservatively.")
