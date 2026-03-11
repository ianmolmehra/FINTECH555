"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/analytics/streak_analysis.py
Module 12: Streak Analysis — Run-Length Encoding + Post-Streak Behavior
================================================================================
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from itertools import groupby
from config.settings import THEME


def compute_streaks(df: pd.DataFrame) -> dict:
    """
    Detects winning and losing streaks using Run-Length Encoding (RLE).

    Concept: Run-Length Encoding — compress consecutive identical values.
    Formula: RLE([W,W,W,L,L,W]) → [(W,3),(L,2),(W,1)]

    Post-streak behavior: P(Win | last N were losses) — conditional probability.
    Formula: P(A|B) = P(A∩B)/P(B) — Bayes' Theorem applied to trade sequences.
    """
    outcomes = df["is_profit"].values   # Array of 1s (wins) and 0s (losses)

    # ── RLE: group consecutive identical outcomes
    # itertools.groupby groups consecutive equal elements
    streaks = [(key, len(list(group))) for key, group in groupby(outcomes)]

    winning_streaks = [length for result, length in streaks if result == 1]
    losing_streaks  = [length for result, length in streaks if result == 0]

    max_win_streak  = max(winning_streaks) if winning_streaks else 0
    max_loss_streak = max(losing_streaks)  if losing_streaks  else 0

    # ── Post-streak behavior: for each streak length N, what is the win rate of trade N+1?
    post_streak_wr = {}
    for streak_len in range(1, min(max_loss_streak + 1, 8)):
        # Find indices where a losing streak of exactly streak_len ends
        post_trade_outcomes = []
        i = 0
        while i < len(outcomes):
            # Count consecutive losses from index i
            run_len = 0
            j = i
            while j < len(outcomes) and outcomes[j] == 0:
                run_len += 1
                j += 1
            if run_len == streak_len and j < len(outcomes):
                # Trade immediately after this losing streak
                post_trade_outcomes.append(outcomes[j])
            i = j + 1 if j > i else i + 1

        if post_trade_outcomes:
            wr = round(np.mean(post_trade_outcomes) * 100, 1)
            post_streak_wr[streak_len] = {"win_rate": wr, "count": len(post_trade_outcomes)}

    # ── Find sectors involved in the longest winning streak
    # Identify the index range of the longest streak
    cum_pos = 0
    best_start_idx = 0
    current_start = 0
    current_len = 0
    for i, (res, length) in enumerate(streaks):
        if res == 1 and length > current_len:
            current_len = length
            best_start_idx = cum_pos
        cum_pos += length

    streak_trades = df.iloc[best_start_idx: best_start_idx + max_win_streak]
    top_streak_symbols = streak_trades["symbol"].value_counts().head(3).index.tolist() if len(streak_trades) > 0 else []

    return {
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "avg_win_streak": round(np.mean(winning_streaks), 1) if winning_streaks else 0,
        "avg_loss_streak": round(np.mean(losing_streaks), 1) if losing_streaks else 0,
        "post_streak_wr": post_streak_wr,
        "top_streak_symbols": top_streak_symbols,
        "total_streaks": len(streaks),
    }


def render_streak_analysis_module(df: pd.DataFrame):
    """Renders Module 12 with streak table and post-streak behavior heatmap."""
    st.markdown("### 🔥 Streak Analysis")
    streak = compute_streaks(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Longest Win Streak", f"{streak['max_win_streak']} trades")
    c2.metric("Longest Loss Streak", f"{streak['max_loss_streak']} trades")
    c3.metric("Avg Win Streak", f"{streak['avg_win_streak']:.1f}")
    c4.metric("Avg Loss Streak", f"{streak['avg_loss_streak']:.1f}")

    if streak["top_streak_symbols"]:
        st.markdown(f"**🏆 Longest win streak involved:** {', '.join(streak['top_streak_symbols'])}")

    # ── POST-STREAK WIN RATE BAR CHART
    if streak["post_streak_wr"]:
        lengths = list(streak["post_streak_wr"].keys())
        wrs = [streak["post_streak_wr"][l]["win_rate"] for l in lengths]
        counts = [streak["post_streak_wr"][l]["count"] for l in lengths]
        colors = [THEME["green"] if w > 50 else THEME["red"] for w in wrs]

        fig = go.Figure(go.Bar(
            x=[f"After {l} losses" for l in lengths], y=wrs,
            marker_color=colors,
            text=[f"{w:.0f}%<br>(n={c})" for w, c in zip(wrs, counts)],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Win Rate: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=50, line_dash="dash", line_color=THEME["amber"],
                      annotation_text="Random baseline (50%)")
        fig.update_layout(
            title="Win Rate of Trade N+1 After N Consecutive Losses",
            paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
            font_color=THEME["text"], yaxis=dict(range=[0,100], title="Win Rate %"),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    from explainability.xai import explain_streaks
    st.info(f"🧠 **AI Analyst Insight:**\n\n{explain_streaks(streak, df)}")
    st.success(f"⚡ **Action:** After any losing streak of {min(streak['max_loss_streak'], 3)} or more trades, take a mandatory 24-hour break before re-entering the market. Your data shows this pattern costs you money.")


# ── Alias: report.py calls compute_streak_analysis()
def compute_streak_analysis(df):
    """Alias for compute_streaks() — called by report.py."""
    return compute_streaks(df)
