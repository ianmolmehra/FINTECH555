"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/panic_detection.py
Module 2: Behavioral Bias & Panic Detection
Purpose: Detects 5 behavioral biases using KMeans clustering and rule-based logic.
         Biases: Panic Selling, Revenge Trading, Loss Aversion,
                 Overconfidence, Disposition Effect (Shefrin & Statman 1985)
================================================================================
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.cluster import KMeans        # Unsupervised clustering for behavior profiling
from sklearn.preprocessing import StandardScaler  # Feature normalization before clustering
from config.settings import BIAS, THEME


def compute_biases(df: pd.DataFrame) -> dict:
    """
    Computes 5 behavioral bias scores and clusters trades into behavior profiles.

    Concept: KMeans Clustering — unsupervised algorithm that minimizes within-cluster
             sum of squares (inertia) to find natural groupings in trader behavior.
    Formula: Inertia = Σ_k Σ_{x∈C_k} ||x - μ_k||² where μ_k = cluster centroid

    Returns: Dictionary with bias scores (0-100 each) and cluster labels
    """
    total = len(df)
    wins = df["is_profit"].sum()
    losses = total - wins
    win_rate = wins / total if total > 0 else 0

    # ── BIAS 1: Panic Selling — rate of quick exits on losing trades
    # Signal: trade closed same day (hold_days == 0) AND resulted in a loss
    panic_trades = df[(df["hold_days"] == 0) & (df["is_profit"] == 0)]
    panic_pct = (len(panic_trades) / total * 100) if total > 0 else 0

    # ── BIAS 2: Revenge Trading — re-entry within 4 hours after a loss
    # Signal: is_after_loss == 1 (previous trade was a loss) AND is_quick_trade == 1
    revenge_count = df["is_revenge"].sum() if "is_revenge" in df.columns else 0
    revenge_pct = (revenge_count / max(losses, 1) * 100)

    # ── BIAS 3: Loss Aversion — holding losers longer than winners
    # Concept: Prospect Theory (Kahneman & Tversky 1979)
    # Formula: Disposition Ratio = avg_hold_winners / avg_hold_losers
    # Ratio > 1 means traders sell winners too early and hold losers too long
    avg_hold_winners = df[df["is_profit"] == 1]["hold_days"].mean() if wins > 0 else 0
    avg_hold_losers  = df[df["is_profit"] == 0]["hold_days"].mean() if losses > 0 else 0
    disposition_ratio = avg_hold_winners / max(avg_hold_losers, 0.1)
    # Disposition effect score: higher when winners held shorter than losers
    # A ratio < 1 means you hold losers longer — classic disposition effect
    loss_aversion_score = max(0, (1 - disposition_ratio) * 100) if disposition_ratio < 1 else 0

    # ── BIAS 4: Overconfidence — excessive position sizing after winning streaks
    # Proxy: CV (coefficient of variation) of capital deployed — high CV = inconsistent sizing
    cv_capital = df["capital_deployed"].std() / df["capital_deployed"].mean() if df["capital_deployed"].mean() > 0 else 0
    overconfidence_score = min(100, cv_capital * 80)  # Scale CV to 0-100

    # ── BIAS 5: Disposition Effect (Shefrin & Statman 1985)
    # Composite: combines early winner selling with late loser holding
    # Score rises when avg winner hold < avg loser hold (the irrational pattern)
    if avg_hold_losers > avg_hold_winners and wins > 0 and losses > 0:
        disp_score = min(100, ((avg_hold_losers - avg_hold_winners) / max(avg_hold_losers, 1)) * 100)
    else:
        disp_score = 0

    # ── BEHAVIORAL HEALTH SCORE: 100 - weighted average of all bias scores
    # Inversion: high bias = low health score
    bhs = 100 - (0.25*panic_pct + 0.20*revenge_pct + 0.20*loss_aversion_score +
                 0.15*overconfidence_score + 0.20*disp_score)
    bhs = max(0, min(100, bhs))

    # ── KMEANS CLUSTERING: Group trades into 3 behavioral profiles
    # Using: hold_days, pnl_pct, capital_pct, is_panic, is_revenge
    # KMeans: unsupervised — finds natural behavior clusters without labels
    cluster_labels = None
    if total >= BIAS["min_trades_for_ml"]:
        feature_cols = ["hold_days", "pnl_pct", "capital_pct"]
        available = [c for c in feature_cols if c in df.columns]
        X = df[available].fillna(0).values

        # StandardScaler: z-score normalization — ensures all features have equal weight
        # Formula: z = (x - μ) / σ — zero mean, unit variance
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # KMeans with k=3: Disciplined (0), Reactive (1), Impulsive (2)
        # random_state=42: reproducibility — same result every run
        km = KMeans(n_clusters=BIAS["kmeans_clusters"], random_state=42, n_init=10)
        cluster_labels = km.fit_predict(X_scaled)

        # Label clusters by their average PnL: highest = Disciplined, lowest = Impulsive
        cluster_pnl = {}
        for c in range(BIAS["kmeans_clusters"]):
            mask = cluster_labels == c
            cluster_pnl[c] = df.loc[mask, "pnl"].mean() if mask.sum() > 0 else 0

        sorted_clusters = sorted(cluster_pnl, key=cluster_pnl.get, reverse=True)
        label_map = {sorted_clusters[0]: "Disciplined", sorted_clusters[1]: "Reactive",
                     sorted_clusters[2]: "Impulsive"}
        cluster_labels = [label_map[c] for c in cluster_labels]

    return {
        "panic_pct": round(panic_pct, 1),
        "revenge_pct": round(revenge_pct, 1),
        "loss_aversion_score": round(loss_aversion_score, 1),
        "overconfidence_score": round(overconfidence_score, 1),
        "disposition_score": round(disp_score, 1),
        "behavioral_health_score": round(bhs, 1),
        "cluster_labels": cluster_labels,
        "disposition_ratio": round(disposition_ratio, 2),
        "avg_hold_winners": round(avg_hold_winners, 1),
        "avg_hold_losers": round(avg_hold_losers, 1),
    }


def render_panic_module(df: pd.DataFrame):
    """Renders complete Module 2 UI with radar chart, KPI strip, and XAI."""
    biases = compute_biases(df)

    st.markdown("### 😨 Behavioral Bias & Panic Detection")

    # ── KPI STRIP
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Behavioral Health", f"{biases['behavioral_health_score']:.0f}/100")
    c2.metric("Panic Rate", f"{biases['panic_pct']:.1f}%",
              delta="⚠️ High" if biases["panic_pct"] > 30 else "✅ OK", delta_color="inverse")
    c3.metric("Revenge Rate", f"{biases['revenge_pct']:.1f}%")
    c4.metric("Disposition Ratio", f"{biases['disposition_ratio']:.2f}",
              help="< 1.0 = holding losers longer than winners")
    c5.metric("Overconfidence", f"{biases['overconfidence_score']:.0f}/100")

    col1, col2 = st.columns([1, 1])

    with col1:
        # ── RADAR/SPIDER CHART: 5 bias dimensions as behavioral fingerprint
        categories = ["Panic Selling", "Revenge Trading", "Loss Aversion",
                      "Overconfidence", "Disposition Effect"]
        values = [biases["panic_pct"], biases["revenge_pct"], biases["loss_aversion_score"],
                  biases["overconfidence_score"], biases["disposition_score"]]

        fig = go.Figure()
        # Add trader's bias profile
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor=f"rgba(255,82,82,0.25)",
            line_color=THEME["red"], name="Your Biases",
            hovertemplate="<b>%{theta}</b>: %{r:.1f}<extra></extra>",
        ))
        # Add healthy benchmark (all biases = 20 or less)
        benchmark = [20] * 5
        fig.add_trace(go.Scatterpolar(
            r=benchmark + [benchmark[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor=f"rgba(0,200,83,0.1)",
            line_color=THEME["green"], name="Healthy Benchmark",
            line_dash="dash",
        ))
        fig.update_layout(polar=dict(
            bgcolor=THEME["card_bg"],
            radialaxis=dict(visible=True, range=[0, 100], color=THEME["subtext"]),
            angularaxis=dict(color=THEME["text"]),
        ), paper_bgcolor=THEME["bg"], height=320,
           legend=dict(font_color=THEME["text"], bgcolor=THEME["bg"]),
           margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ── KMEANS CLUSTER DISTRIBUTION if enough trades
        if biases["cluster_labels"] is not None:
            from collections import Counter
            counts = Counter(biases["cluster_labels"])
            labels = list(counts.keys())
            vals = list(counts.values())
            colors = {
                "Disciplined": THEME["green"],
                "Reactive": THEME["amber"],
                "Impulsive": THEME["red"]
            }
            pie_fig = go.Figure(go.Pie(
                labels=labels, values=vals,
                marker_colors=[colors.get(l, THEME["blue"]) for l in labels],
                hole=0.5, textinfo="label+percent",
                hovertemplate="<b>%{label}</b>: %{value} trades<extra></extra>",
            ))
            pie_fig.update_layout(paper_bgcolor=THEME["bg"], showlegend=True,
                                  height=320, margin=dict(t=20,b=20,l=10,r=10),
                                  legend=dict(font_color=THEME["text"], bgcolor=THEME["bg"]))
            pie_fig.add_annotation(text="<b>Behavior<br>Profile</b>", x=0.5, y=0.5,
                                   showarrow=False, font_size=13, font_color=THEME["text"])
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info(f"KMeans clustering requires {BIAS['min_trades_for_ml']}+ trades. Upload more data.")

    # ── XAI EXPLANATION
    from explainability.xai import explain_panic
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_panic(biases, df)}")

    # ── ACTION BOX
    worst_bias = max({"Panic Selling": biases["panic_pct"],
                      "Revenge Trading": biases["revenge_pct"],
                      "Loss Aversion": biases["loss_aversion_score"]}.items(),
                     key=lambda x: x[1])
    st.success(f"⚡ **Action:** Your biggest behavioral risk is **{worst_bias[0]}** at {worst_bias[1]:.1f}. Before your next trade, write down your exit rule BEFORE you enter. Traders who pre-commit to exits reduce panic selling by 40%.")


# ── Alias for report.py compatibility
def detect_panic_and_biases(df):
    """Alias for compute_biases() — called by report.py."""
    result = compute_biases(df)
    # Normalize key names
    if "bhs" in result and "behavioral_health_score" not in result:
        result["behavioral_health_score"] = result["bhs"]
    return result
