"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/decision_score.py
Module 1: Decision Intelligence Score (DIS) — 0 to 100
Purpose: Measures decision QUALITY independent of profit outcome.
         A trader who made the right call but got unlucky still scores high.
================================================================================
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from config.settings import DIS_WEIGHTS, THEME


def compute_dis(df: pd.DataFrame) -> dict:
    """
    Computes the 5-component Decision Intelligence Score.

    Concept: Multi-criteria decision analysis (MCDA) — weighted composite scoring.
    Formula: DIS = Σ(weight_i × sub_score_i) where Σ weights = 1.0

    Returns:
        Dictionary with total DIS score and all 5 sub-component scores (0–100 each)
    """
    total = len(df)
    wins = df["is_profit"].sum()

    # ── SUB-SCORE 1: Exit Discipline (25% weight)
    # Measures: did the trader avoid premature or panic exits?
    # Formula: 1 - (panic_exits / total_trades) — penalizes emotional exits
    panic_count = df["is_panic"].sum() if "is_panic" in df.columns else 0
    exit_discipline = max(0, (1 - panic_count / total) * 100)

    # ── SUB-SCORE 2: Entry Quality (20% weight)
    # Measures: did profitable trades have good entry timing?
    # Proxy: % of winning trades that were NOT oversized (disciplined conviction sizing)
    wins_not_oversized = ((df["is_profit"] == 1) & (df["is_oversized"] == 0)).sum() if "is_oversized" in df.columns else wins
    entry_quality = (wins_not_oversized / total) * 100

    # ── SUB-SCORE 3: Position Sizing (20% weight)
    # Measures: Coefficient of Variation (CV) of capital deployed
    # Formula: CV = σ / μ — lower CV = more consistent sizing = higher score
    std_cap = df["capital_deployed"].std()
    mean_cap = df["capital_deployed"].mean()
    cv = std_cap / mean_cap if mean_cap > 0 else 1.0  # CV = std/mean (dimensionless)
    position_sizing = max(0, min(100, (1 - min(cv, 1)) * 100))  # Invert: lower CV = better

    # ── SUB-SCORE 4: Patience Score (20% weight)
    # Measures: did the trader hold trades long enough?
    # Benchmark: median hold time vs 25th percentile — rewards those who hold longer
    median_hold = df["hold_days"].median()
    q25_hold = df["hold_days"].quantile(0.25)
    patience_ratio = median_hold / max(q25_hold, 1)
    patience_score = min(100, patience_ratio * 20)  # Normalize: ratio of 5 = 100 pts

    # ── SUB-SCORE 5: Recovery Score (15% weight)
    # Measures: did the trader avoid revenge trading after losses?
    # Formula: 1 - (revenge_trades / loss_trades) — penalizes emotional re-entries
    losses = total - wins
    revenge_count = df["is_revenge"].sum() if "is_revenge" in df.columns else 0
    recovery_score = max(0, (1 - revenge_count / max(losses, 1)) * 100)

    # ── COMPOSITE SCORE: Weighted sum of all sub-components
    # Formula: DIS = Σ(weight_i × score_i) — Linear combination (MCDA principle)
    total_dis = (
        DIS_WEIGHTS["exit_discipline"] * exit_discipline +
        DIS_WEIGHTS["entry_quality"] * entry_quality +
        DIS_WEIGHTS["position_sizing"] * position_sizing +
        DIS_WEIGHTS["patience_score"] * patience_score +
        DIS_WEIGHTS["recovery_score"] * recovery_score
    )

    return {
        "total": round(total_dis, 1),
        "exit_discipline": round(exit_discipline, 1),
        "entry_quality": round(entry_quality, 1),
        "position_sizing": round(position_sizing, 1),
        "patience_score": round(patience_score, 1),
        "recovery_score": round(recovery_score, 1),
        "grade": _grade(total_dis),
    }


def _grade(score: float) -> str:
    """Maps numeric DIS score to a letter grade."""
    if score >= 80: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "F"


def render_dis_module(df: pd.DataFrame):
    """
    Renders the complete Module 1 UI: KPI strip, donut chart, sub-component bars,
    XAI explanation, action box, and What-If improvement slider.
    """
    dis = compute_dis(df)

    # ── KPI STRIP: 4 key numbers as metric cards
    st.markdown("### 🎯 Decision Intelligence Score")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DIS Score", f"{dis['total']}/100", delta=dis["grade"])
    c2.metric("Exit Discipline", f"{dis['exit_discipline']:.1f}")
    c3.metric("Position Sizing", f"{dis['position_sizing']:.1f}")
    c4.metric("Recovery Score", f"{dis['recovery_score']:.1f}")

    col_chart, col_bars = st.columns([1, 1])

    with col_chart:
        # ── MAIN VISUALIZATION: Donut chart with DIS score in the center
        # Center text shows both score number AND grade — per specification
        fig = go.Figure(go.Pie(
            values=[dis["total"], 100 - dis["total"]],
            labels=["DIS Score", "Gap"],
            hole=0.65,
            marker_colors=[THEME["green"] if dis["total"] >= 65 else THEME["amber"] if dis["total"] >= 45 else THEME["red"], THEME["grid"]],
            textinfo="none",
            hovertemplate="<b>%{label}</b>: %{value:.1f}<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{dis['total']}</b><br>Grade {dis['grade']}",
                           x=0.5, y=0.5, font_size=22, showarrow=False,
                           font_color=THEME["text"])
        fig.update_layout(paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                          showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                          height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_bars:
        # ── SUB-COMPONENT BARS: horizontal color-coded bars showing each sub-score
        components = {
            "Exit Discipline": dis["exit_discipline"],
            "Entry Quality": dis["entry_quality"],
            "Position Sizing": dis["position_sizing"],
            "Patience": dis["patience_score"],
            "Recovery": dis["recovery_score"],
        }
        bar_fig = go.Figure()
        for name, val in components.items():
            color = THEME["green"] if val >= 65 else THEME["amber"] if val >= 45 else THEME["red"]
            bar_fig.add_trace(go.Bar(
                x=[val], y=[f"{name} ({val:.0f}/100)"], orientation="h",
                marker_color=color,
                hovertemplate=f"<b>{name}</b>: {val:.1f}/100<extra></extra>",
            ))
        bar_fig.update_layout(
            paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
            showlegend=False, xaxis=dict(range=[0, 100], color=THEME["subtext"]),
            yaxis=dict(color=THEME["text"]), height=280,
            margin=dict(t=10, b=10, l=10, r=10),
            barmode="overlay",
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # ── XAI EXPLANATION CARD: Multi-condition analyst voice
    from explainability.xai import explain_dis
    explanation = explain_dis(dis, df)
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explanation}")

    # ── ACTION BOX: specific, measurable recommendation
    worst_component = min(components, key=components.get)
    st.success(f"⚡ **Action:** Focus on improving **{worst_component}** — your weakest dimension at {components[worst_component]:.0f}/100. A 10-point improvement here adds {10 * DIS_WEIGHTS.get(worst_component.lower().replace(' ','_'), 0.2):.1f} points to your DIS.")

    # ── WHAT-IF SLIDER: shows impact of improving a component
    st.markdown("#### 🎛️ What-If Improvement Simulator")
    slider_col = st.selectbox("Select component to improve:", list(components.keys()))
    improvement = st.slider("Improvement (points):", 0, 30, 10)
    
    # Recalculate DIS with the hypothetical improvement
    # Formula: new_DIS = old_DIS + improvement × component_weight
    weight_map = {"Exit Discipline": 0.25, "Entry Quality": 0.20, "Position Sizing": 0.20,
                  "Patience": 0.20, "Recovery": 0.15}
    projected = dis["total"] + improvement * weight_map.get(slider_col, 0.20)
    projected = min(projected, 100)
    st.metric(f"Projected DIS if {slider_col} improves by {improvement} pts:",
              f"{projected:.1f}", delta=f"+{projected - dis['total']:.1f}")


# ── Alias for report.py compatibility
def compute_decision_intelligence_score(df):
    """Alias for compute_dis() — called by report.py."""
    result = compute_dis(df)
    # Normalize key names: report.py uses 'score', 'grade', 'sub_scores', 'exit_discipline', etc.
    if "total" in result and "score" not in result:
        result["score"] = result["total"]
    if "components" in result and "sub_scores" not in result:
        result["sub_scores"] = result["components"]
        # Extract individual sub-scores for report.py
        comps = result.get("components", {})
        result["exit_discipline"]  = comps.get("Exit Discipline", comps.get("exit_discipline", 0))
        result["entry_quality"]    = comps.get("Entry Quality", comps.get("entry_quality", 0))
        result["sizing_control"]   = comps.get("Position Sizing", comps.get("sizing_control", 0))
        result["patience_score"]   = comps.get("Patience", comps.get("patience_score", 0))
        result["recovery_score"]   = comps.get("Recovery Rate", comps.get("recovery_score", 0))
    return result
