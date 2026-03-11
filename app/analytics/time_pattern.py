"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/time_pattern.py
Module 13: Time & Day Pattern Analysis
Purpose: Detects performance patterns by day of week and month of year.
         Uses Chi-squared test for statistical significance.
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy import stats
from config.settings import THEME

DAY_NAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday"]


def compute_time_patterns(df: pd.DataFrame) -> dict:
    """
    Computes win rates and avg PnL by day of week and month of year.

    Concept: Chi-squared test — checks if win rate distribution across days is uniform.
    H0: Win rate is the same on all days (null hypothesis = no pattern).
    Formula: χ² = Σ[(Observed - Expected)² / Expected]
    Reject H0 when p < 0.05 → there IS a statistically significant day-of-week pattern.
    """
    # ── Day of week stats (only weekdays: Mon=0 ... Fri=4)
    day_group = df.groupby("day_of_week").agg(
        win_rate=("is_profit", "mean"),
        avg_pnl=("pnl", "mean"),
        count=("pnl", "count"),
    ).reindex(range(5)).fillna(0)
    day_group["day_name"] = DAY_NAMES[:len(day_group)]
    day_group["win_rate_pct"] = day_group["win_rate"] * 100

    # ── Chi-squared test on win counts across days
    observed_wins = []
    for d in range(5):
        day_df = df[df["day_of_week"] == d]
        observed_wins.append(day_df["is_profit"].sum())
    observed_wins = np.array(observed_wins)
    total_obs = observed_wins.sum()
    expected = np.full(5, total_obs / 5)  # H0: equal distribution across days
    if total_obs > 0:
        chi2, p_val = stats.chisquare(observed_wins + 0.01, expected + 0.01)
    else:
        chi2, p_val = 0.0, 1.0

    # ── Month of year stats
    month_group = df.groupby("month").agg(
        win_rate=("is_profit","mean"),
        avg_pnl=("pnl","mean"),
        count=("pnl","count"),
    ).reindex(range(1,13)).fillna(0)
    month_group["win_rate_pct"] = month_group["win_rate"] * 100

    best_day_idx = int(day_group["win_rate_pct"].idxmax()) if day_group["win_rate_pct"].sum() > 0 else 2
    worst_day_idx = int(day_group["win_rate_pct"].idxmin()) if day_group["win_rate_pct"].sum() > 0 else 0
    best_day = DAY_NAMES[best_day_idx] if best_day_idx < 5 else "Wednesday"
    worst_day = DAY_NAMES[worst_day_idx] if worst_day_idx < 5 else "Monday"

    return {
        "day_group": day_group,
        "month_group": month_group,
        "chi2": round(chi2, 2),
        "p_value": round(p_val, 4),
        "significant": p_val < 0.05,
        "best_day": best_day,
        "worst_day": worst_day,
        "best_day_wr": round(day_group["win_rate_pct"].max(), 1),
        "worst_day_wr": round(day_group["win_rate_pct"].min(), 1),
    }


def render_time_pattern_module(df: pd.DataFrame):
    """Renders Module 13 with weekday heatmap and monthly bar chart."""
    st.markdown("### 📅 Time & Day Pattern Analysis")
    tp = compute_time_patterns(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Trading Day", tp["best_day"], delta=f"{tp['best_day_wr']:.0f}% win rate")
    c2.metric("Worst Trading Day", tp["worst_day"], delta=f"{tp['worst_day_wr']:.0f}% win rate", delta_color="inverse")
    c3.metric("Chi² Statistic", f"{tp['chi2']:.2f}")
    c4.metric("p-value", f"{tp['p_value']:.4f}",
              delta="Significant ✅" if tp["significant"] else "Not significant",
              delta_color="normal" if tp["significant"] else "off")

    col1, col2 = st.columns([1, 1])

    with col1:
        day_df = tp["day_group"]
        colors = [THEME["green"] if wr > 55 else THEME["amber"] if wr > 40 else THEME["red"]
                  for wr in day_df["win_rate_pct"]]
        fig = go.Figure(go.Bar(
            x=DAY_NAMES[:len(day_df)], y=day_df["win_rate_pct"].values,
            marker_color=colors,
            hovertemplate="<b>%{x}</b><br>Win Rate: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=50, line_dash="dash", line_color=THEME["amber"])
        fig.update_layout(title="Win Rate by Day of Week",
                          paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                          font_color=THEME["text"], yaxis=dict(range=[0,100]),
                          height=280, margin=dict(t=30,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        import calendar
        month_df = tp["month_group"]
        month_names = [calendar.month_abbr[i] for i in range(1, 13)]
        m_colors = [THEME["green"] if wr > 55 else THEME["amber"] if wr > 40 else THEME["red"]
                    for wr in month_df["win_rate_pct"]]
        fig2 = go.Figure(go.Bar(
            x=month_names, y=month_df["win_rate_pct"].values,
            marker_color=m_colors,
            hovertemplate="<b>%{x}</b><br>Win Rate: %{y:.1f}%<extra></extra>",
        ))
        fig2.add_hline(y=50, line_dash="dash", line_color=THEME["amber"])
        fig2.update_layout(title="Win Rate by Month",
                           paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
                           font_color=THEME["text"], yaxis=dict(range=[0,100]),
                           height=280, margin=dict(t=30,b=10,l=10,r=10))
        st.plotly_chart(fig2, use_container_width=True)

    from explainability.xai import explain_time_patterns
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_time_patterns(tp, df)}")
    sig_text = f"(statistically significant, χ²={tp['chi2']:.1f}, p={tp['p_value']:.4f})" if tp["significant"] else "(not yet statistically significant — need more trades)"
    st.success(f"⚡ **Action:** Avoid opening new positions on **{tp['worst_day']}** {sig_text}. Your best day is **{tp['best_day']}** at {tp['best_day_wr']:.0f}% win rate — schedule high-conviction trades for that day.")
