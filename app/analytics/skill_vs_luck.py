"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/skill_vs_luck.py
Module 6: Skill vs Luck — Three-method decomposition
Methods: Monte Carlo z-score (40%) + Autocorrelation (30%) + Logistic Regression (30%)
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from config.settings import MONTE_CARLO, THEME


def compute_skill_vs_luck(df: pd.DataFrame) -> dict:
    """
    Three-method skill decomposition with Sharpe, Sortino, and bootstrap CI.

    Concept 1: Monte Carlo z-score — measures how far win rate is from random baseline.
    Formula: z = (actual_win_rate - mean_random) / std_random

    Concept 2: Pearson Autocorrelation lag-1 — measures if good trades cluster (skill)
    Formula: r = corr(PnL[t], PnL[t-1])

    Concept 3: Logistic Regression — binary classifier for win probability.
    Formula: P(Win) = sigmoid(w·X + b) where sigmoid(x) = 1/(1+e^{-x})
    """
    total = len(df)
    win_rate = df["is_profit"].mean()

    # ── METHOD 1: Monte Carlo z-score (40% weight)
    n_sims = MONTE_CARLO["simulations"]
    random_win_rates = np.random.binomial(total, 0.5, n_sims) / total
    z_score = (win_rate - random_win_rates.mean()) / random_win_rates.std()
    # p-value: probability of observing this win rate by random chance
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    mc_skill = min(100, max(0, (z_score / 3) * 100))  # z=3 → 100 pts

    # ── METHOD 2: Autocorrelation lag-1 (30% weight)
    # Positive autocorrelation: good trades followed by good trades (skill clustering)
    pnl_series = df["pnl"].values
    if len(pnl_series) > 2:
        # Pearson autocorrelation at lag 1
        autocorr = np.corrcoef(pnl_series[:-1], pnl_series[1:])[0, 1]
    else:
        autocorr = 0
    ac_skill = min(100, max(0, autocorr * 100 + 50))  # Center at 50

    # ── METHOD 3: Logistic Regression (30% weight)
    feature_cols = ["hold_days", "capital_pct"]
    available = [c for c in feature_cols if c in df.columns]
    lr_skill = 50.0  # Default: no edge detected
    if len(available) >= 1 and total >= 15:
        X = df[available].fillna(0).values
        y = df["is_profit"].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        lr = LogisticRegression(random_state=42, max_iter=200)
        lr.fit(X_scaled, y)
        # Accuracy above 50% baseline indicates predictive skill
        acc = lr.score(X_scaled, y)
        lr_skill = max(0, min(100, (acc - 0.5) * 200))  # 50% acc = 0, 100% acc = 100

    # ── COMPOSITE SKILL SCORE: weighted average of three methods
    composite_skill = 0.40 * mc_skill + 0.30 * ac_skill + 0.30 * lr_skill

    # ── SHARPE RATIO: risk-adjusted return using total volatility
    # Formula: Sharpe = (mean_return - risk_free_rate) / std_return × √252
    rf = MONTE_CARLO["risk_free_rate"] / 252  # Daily risk-free rate
    mean_pnl = df["pnl"].mean()
    std_pnl = df["pnl"].std()
    sharpe = ((mean_pnl - rf) / std_pnl * np.sqrt(252)) if std_pnl > 0 else 0

    # ── SORTINO RATIO: penalizes only downside volatility (better for asymmetric returns)
    # Formula: Sortino = mean_return / downside_std × √252
    downside = df[df["pnl"] < 0]["pnl"]
    downside_std = downside.std() if len(downside) > 1 else std_pnl
    sortino = (mean_pnl / downside_std * np.sqrt(252)) if downside_std > 0 else 0

    # ── KOLMOGOROV-SMIRNOV TEST against uniform random distribution
    # H0: PnL distribution is random. p<0.05 = statistically significant edge detected.
    random_baseline = np.random.normal(0, std_pnl, n_sims)
    ks_stat, ks_p = stats.ks_2samp(df["pnl"].values, random_baseline)

    # ── BOOTSTRAP 95% CONFIDENCE INTERVAL around skill estimate
    # Bootstrap CI: resample with replacement 1000 times, compute CI from distribution
    # Formula: 95% CI = [percentile_2.5, percentile_97.5] — empirical CI
    bootstrap_scores = []
    for _ in range(1000):
        sample = df["pnl"].sample(n=min(total, 30), replace=True)
        sample_wr = (sample > 0).mean()
        bootstrap_scores.append(sample_wr * 100)
    ci_lower = np.percentile(bootstrap_scores, 2.5)
    ci_upper = np.percentile(bootstrap_scores, 97.5)

    return {
        "composite_skill": round(composite_skill, 1),
        "mc_skill": round(mc_skill, 1),
        "ac_skill": round(ac_skill, 1),
        "lr_skill": round(lr_skill, 1),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "autocorrelation": round(float(autocorr), 3),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "ks_stat": round(ks_stat, 3),
        "ks_p_value": round(ks_p, 4),
        "ci_lower": round(ci_lower, 1),
        "ci_upper": round(ci_upper, 1),
        "win_rate_pct": round(win_rate * 100, 1),
    }


def render_skill_vs_luck_module(df: pd.DataFrame):
    """Renders Module 6 with gauge chart, method breakdown, and statistical summary."""
    st.markdown("### 🎲 Skill vs Luck Decomposition")
    result = compute_skill_vs_luck(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Skill Score", f"{result['composite_skill']:.1f}/100")
    c2.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
    c3.metric("Sortino Ratio", f"{result['sortino_ratio']:.2f}")
    c4.metric("KS p-value", f"{result['ks_p_value']:.4f}",
              help="p < 0.05 = statistically significant edge")
    c5.metric("Win Rate 95% CI", f"{result['ci_lower']:.1f}–{result['ci_upper']:.1f}%")

    col1, col2 = st.columns([1, 1])
    with col1:
        # ── GAUGE CHART: composite skill score
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=result["composite_skill"],
            number={"suffix": "/100", "font": {"color": THEME["text"], "size": 36}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": THEME["subtext"]},
                "bar": {"color": THEME["green"] if result["composite_skill"] >= 60
                        else THEME["amber"] if result["composite_skill"] >= 40 else THEME["red"]},
                "bgcolor": THEME["card_bg"],
                "steps": [
                    {"range": [0, 40], "color": "#1A0A0A"},
                    {"range": [40, 60], "color": "#1A1A0A"},
                    {"range": [60, 100], "color": "#0A1A0A"},
                ],
                "threshold": {"line": {"color": THEME["amber"], "width": 3}, "value": 50},
            },
        ))
        fig.update_layout(paper_bgcolor=THEME["bg"], font_color=THEME["text"],
                          height=280, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        methods = {"Monte Carlo\n(40%)": result["mc_skill"],
                   "Autocorrelation\n(30%)": result["ac_skill"],
                   "Logistic Reg.\n(30%)": result["lr_skill"]}
        bar_fig = go.Figure()
        for name, val in methods.items():
            color = THEME["green"] if val >= 60 else THEME["amber"] if val >= 40 else THEME["red"]
            bar_fig.add_trace(go.Bar(x=[val], y=[name], orientation="h",
                                     marker_color=color,
                                     hovertemplate=f"<b>{name}</b>: {val:.1f}/100<extra></extra>"))
        bar_fig.update_layout(paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                              showlegend=False, xaxis=dict(range=[0,100], color=THEME["subtext"]),
                              yaxis=dict(color=THEME["text"]), height=280,
                              margin=dict(t=10,b=10,l=10,r=10), barmode="overlay")
        st.plotly_chart(bar_fig, use_container_width=True)

    from explainability.xai import explain_skill_vs_luck
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_skill_vs_luck(result, df)}")
    edge = "statistically significant" if result["ks_p_value"] < 0.05 else "not yet statistically significant"
    st.success(f"⚡ **Action:** Your trading edge is {edge} (KS p={result['ks_p_value']:.4f}). You need at least {max(0, int(30 - len(df) * result['composite_skill'] / 100))} more trades to build a reliable track record.")
