# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/charts.py
# Purpose: All Plotly chart builders for every module visualization.
#          Dark FinTech theme applied to every chart.
# =============================================================================

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from config.settings import CHART_BG, CHART_GREEN, CHART_AMBER, CHART_RED, CHART_BLUE, CHART_GOLD, THEME

# ── Standard dark layout applied to every chart ───────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(color="#C8E6C9", family="Inter"),
    margin=dict(t=40, b=40, l=40, r=40),
)

# ── Safe rgba helpers — Plotly only accepts rgba(), not hex+opacity ────────
def _rgba(hex_color: str, alpha: float = 0.2) -> str:
    """Convert #RRGGBB hex to rgba(r,g,b,alpha) string for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

GREEN_RGBA  = _rgba(CHART_GREEN, 0.15)
AMBER_RGBA  = _rgba(CHART_AMBER, 0.15)
RED_RGBA    = _rgba(CHART_RED,   0.15)
GREEN_RGBA2 = _rgba(CHART_GREEN, 0.10)


def dis_donut(sub_scores: dict, total_score: float, grade: str) -> go.Figure:
    """Donut chart for Decision Intelligence Score."""
    labels = list(sub_scores.keys())
    values = list(sub_scores.values())
    maxes  = [20, 25, 15, 20, 20]
    colors = [CHART_GREEN if v/mx >= 0.6 else CHART_AMBER if v/mx >= 0.35 else CHART_RED
              for v, mx in zip(values, maxes)]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="%{label}: %{value:.1f} pts<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{total_score}</b><br><span style='font-size:11px'>{grade[:1]}</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=28, color=CHART_GREEN),
        xanchor="center", yanchor="middle",
    )
    fig.update_layout(**DARK_LAYOUT, title="Decision Intelligence Score", showlegend=True,
                      legend=dict(bgcolor="rgba(0,0,0,0)"))
    return fig


def horizontal_bars(labels: list, values: list, maxes: list, title: str = "") -> go.Figure:
    """Horizontal bar chart for sub-component breakdowns."""
    colors = [CHART_GREEN if v/mx >= 0.6 else CHART_AMBER if v/mx >= 0.35 else CHART_RED
              for v, mx in zip(values, maxes)]
    fig = go.Figure(go.Bar(
        y=labels, x=values, orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}/{mx}" for v, mx in zip(values, maxes)],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=labels, x=maxes, orientation="h",
        marker_color="rgba(255,255,255,0.08)",
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(**DARK_LAYOUT, title=title, barmode="overlay",
                      xaxis=dict(gridcolor="#1B3020"), yaxis=dict(gridcolor="#1B3020"))
    return fig


def radar_chart(categories: list, values: list, title: str = "Behavioral Fingerprint") -> go.Figure:
    """Radar/Spider chart for multi-dimensional analysis."""
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(0,200,83,0.15)",
        line=dict(color=CHART_GREEN, width=2),
        marker=dict(color=CHART_GREEN, size=8),
        hovertemplate="%{theta}: %{r:.1f}<extra></extra>",
    ))
    fig.update_layout(**DARK_LAYOUT, title=title,
                      polar=dict(
                          bgcolor="#0D1A0D",
                          radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2E4A2E"),
                          angularaxis=dict(gridcolor="#2E4A2E"),
                      ))
    return fig


def gauge_chart(value: float, title: str, min_val: float = 0, max_val: float = 100,
                threshold_green: float = 65, threshold_red: float = 35) -> go.Figure:
    """Gauge chart for single-metric visualization."""
    color = CHART_GREEN if value >= threshold_green else CHART_AMBER if value >= threshold_red else CHART_RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"color": "#C8E6C9", "size": 14}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#81C784"},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": "#0D1A0D",
            "borderwidth": 2, "bordercolor": "#2E7D32",
            "steps": [
                {"range": [min_val, threshold_red],    "color": "#1A0A0A"},
                {"range": [threshold_red, threshold_green], "color": "#1A1A0A"},
                {"range": [threshold_green, max_val],  "color": "#0A1A0A"},
            ],
        },
    ))
    fig.update_layout(**DARK_LAYOUT, height=260)
    return fig


def butterfly_chart(labels: list, actual: list, simulated: list, title: str = "Patience Gap") -> go.Figure:
    """Diverging/Butterfly bar chart for actual vs simulated PnL comparison."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Actual PnL", y=labels, x=actual, orientation="h",
        marker_color=CHART_RED,
        hovertemplate="%{y} Actual: ₹%{x:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Simulated PnL", y=labels, x=simulated, orientation="h",
        marker_color=CHART_GREEN,
        hovertemplate="%{y} Simulated: ₹%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**DARK_LAYOUT, title=title, barmode="overlay",
                      xaxis=dict(title="PnL (₹)", gridcolor="#1B3020"),
                      yaxis=dict(gridcolor="#1B3020"))
    return fig


def area_drawdown(dd_df: pd.DataFrame) -> go.Figure:
    """Area chart showing portfolio equity curve with drawdown shading."""
    if dd_df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dd_df["trade_num"], y=dd_df["portfolio_value"],
        name="Portfolio Value", line=dict(color=CHART_GREEN, width=2),
        fill=None, hovertemplate="Trade %{x}: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=dd_df["trade_num"], y=dd_df["running_max"],
        name="Peak Value", line=dict(color=CHART_AMBER, width=1, dash="dash"),
        hovertemplate="Peak: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=dd_df["trade_num"], y=dd_df["portfolio_value"],
        fill="tonexty", fillcolor="rgba(255,82,82,0.15)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.update_layout(**DARK_LAYOUT, title="Portfolio Equity Curve & Drawdown",
                      xaxis=dict(title="Trade Number", gridcolor="#1B3020"),
                      yaxis=dict(title="Portfolio Value (₹)", gridcolor="#1B3020"))
    return fig


def treemap_sectors(sector_stats: pd.DataFrame) -> go.Figure:
    """Plotly Treemap: size = trade count, color = win rate."""
    if sector_stats.empty:
        return go.Figure()
    fig = px.treemap(
        sector_stats, path=["sector"], values="trade_count", color="win_rate",
        color_continuous_scale=[[0, CHART_RED], [0.5, CHART_AMBER], [1, CHART_GREEN]],
        color_continuous_midpoint=50,
        hover_data={"win_rate": ":.1f", "avg_pnl": ":,.0f", "roi_pct": ":.2f"},
    )
    fig.update_layout(**DARK_LAYOUT, title="Sector Skill Heatmap (Size=Trades, Color=Win Rate)")
    return fig


def bayesian_evolution(evol_df: pd.DataFrame) -> go.Figure:
    """Line chart showing Bayesian win rate estimate evolving with each trade."""
    if evol_df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evol_df["trade_num"], y=evol_df["bayesian_estimate"],
        name="Bayesian Estimate", line=dict(color=CHART_GREEN, width=2),
        hovertemplate="Trade %{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=evol_df["trade_num"].tolist() + evol_df["trade_num"].tolist()[::-1],
        y=evol_df["ci_upper"].tolist() + evol_df["ci_lower"].tolist()[::-1],
        fill="toself", fillcolor="rgba(0,200,83,0.1)", line=dict(width=0),
        name="95% Credible Interval", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=evol_df["trade_num"], y=evol_df["freq_estimate"],
        name="Frequentist Estimate", line=dict(color=CHART_AMBER, width=1, dash="dot"),
    ))
    fig.update_layout(**DARK_LAYOUT, title="Bayesian Win Rate — Belief Evolution",
                      xaxis=dict(title="Trade Number"),
                      yaxis=dict(title="Win Rate Estimate (%)", range=[0, 100]))
    return fig


def efficient_frontier_plot(frontier_df: pd.DataFrame, actual_alloc: dict) -> go.Figure:
    """Scatter plot of portfolio risk-return with efficient frontier overlay."""
    if frontier_df.empty:
        return go.Figure()
    fig = px.scatter(
        frontier_df, x="risk", y="return", color="sharpe",
        color_continuous_scale="RdYlGn",
        labels={"risk": "Risk (Volatility %)", "return": "Expected Return %", "sharpe": "Sharpe"},
        hover_data={"risk": ":.2f", "return": ":.2f", "sharpe": ":.3f"},
    )
    fig.update_layout(**DARK_LAYOUT, title="Efficient Frontier — Sector Portfolio Optimization")
    return fig


# =============================================================================
# CHART ALIASES — used by report.py
# =============================================================================

def chart_cumulative_pnl(df: pd.DataFrame) -> go.Figure:
    """Cumulative PnL equity curve chart."""
    fig = go.Figure()
    y = df["pnl"].cumsum() if "pnl" in df.columns else pd.Series([0])
    fig.add_trace(go.Scatter(
        y=y, mode="lines", fill="tozeroy",
        line=dict(color=CHART_GREEN, width=2),
        fillcolor="rgba(0,200,83,0.15)",
        name="Cumulative PnL",
    ))
    fig.update_layout(
        title="📈 Cumulative PnL Equity Curve",
        template="plotly_dark", paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG, font=dict(color="#E8F5E9"),
        xaxis_title="Trade #", yaxis_title="PnL (₹)",
        height=300, margin=dict(l=40, r=20, t=45, b=40),
    )
    return fig


def chart_dis_breakdown(dis: dict) -> go.Figure:
    """Decision Intelligence Score gauge chart."""
    score = dis.get("score", dis.get("total", 50))
    grade = dis.get("grade", "C")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"color": CHART_GREEN, "size": 32}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#E8F5E9"},
            "bar":  {"color": CHART_GREEN},
            "steps": [
                {"range": [0, 35],   "color": "#1A0A0A"},
                {"range": [35, 65],  "color": "#1A1A0A"},
                {"range": [65, 100], "color": "#0A1A0A"},
            ],
        },
        title={"text": f"Decision Intelligence Score — Grade {grade}",
               "font": {"color": "#E8F5E9"}},
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG,
        height=280, margin=dict(l=30, r=30, t=50, b=30),
    )
    return fig


def chart_panic_radar(panic: dict) -> go.Figure:
    """Behavioral radar chart for 5 bias dimensions."""
    categories = ["Panic Selling", "Revenge Trading", "Loss Aversion",
                  "Overconfidence", "Disposition Effect"]
    values = [
        panic.get("panic_pct", 20),
        panic.get("revenge_pct", 15),
        panic.get("loss_aversion_score", 30),
        panic.get("overconfidence_score", 30),
        panic.get("disposition_score", 25),
    ]
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(255,82,82,0.2)",
        line=dict(color=CHART_RED, width=2),
        name="Behavioral Biases",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=CHART_BG,
            radialaxis=dict(visible=True, range=[0, 100], color="#E8F5E9"),
            angularaxis=dict(color="#E8F5E9"),
        ),
        title="😨 Behavioral Bias Radar",
        template="plotly_dark", paper_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"),
        height=320, margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def chart_loss_attribution_pie(loss: dict) -> go.Figure:
    """Loss attribution donut chart."""
    causes = loss.get("causes", {})
    if not causes:
        causes = {"Panic Exit": 30, "Premature Exit": 25, "Poor Entry": 20,
                  "Oversizing": 15, "Market Conditions": 10}
    labels = list(causes.keys())
    values = list(causes.values())
    colors = [CHART_RED, CHART_AMBER, "#FF9800", "#CE93D8", "#448AFF"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=colors[:len(labels)]),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="📉 Loss Attribution Breakdown",
        template="plotly_dark", paper_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"),
        height=300, margin=dict(l=20, r=20, t=45, b=20),
    )
    return fig


def chart_patience_simulation(sim: dict) -> go.Figure:
    """Diverging bar chart for patience gap scenarios."""
    scenarios = sim.get("scenario_pnl", {})
    if not scenarios:
        return go.Figure()
    actual = sim.get("actual_pnl", 0)
    labels = list(scenarios.keys())
    deltas = [scenarios[k] - actual for k in labels]
    colors = [CHART_GREEN if d >= 0 else CHART_RED for d in deltas]
    fig = go.Figure(go.Bar(
        x=deltas, y=labels, orientation="h",
        marker=dict(color=colors),
        text=[f"₹{d:+,.0f}" for d in deltas],
        textposition="outside",
        hovertemplate="%{y}: %{x:+,.0f} vs actual<extra></extra>",
    ))
    fig.update_layout(
        title="⏳ Patience Gap — Simulated vs Actual PnL",
        template="plotly_dark", paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG, font=dict(color="#E8F5E9"),
        xaxis_title="Difference from Actual PnL (₹)",
        height=320, margin=dict(l=120, r=60, t=45, b=40),
    )
    return fig


def chart_sector_heatmap(sector: dict) -> go.Figure:
    """Treemap: size=trade count, color=win rate."""
    sector_stats = sector.get("sector_stats", pd.DataFrame())
    if sector_stats.empty:
        return go.Figure()
    fig = px.treemap(
        sector_stats, path=["sector"], values="trade_count", color="win_rate",
        color_continuous_scale=[[0, CHART_RED], [0.5, CHART_AMBER], [1, CHART_GREEN]],
        title="🌡️ Sector Skill Heatmap",
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"),
        height=350, margin=dict(l=10, r=10, t=45, b=10),
    )
    return fig


def chart_skill_vs_luck(skill: dict) -> go.Figure:
    """Skill vs Luck gauge chart."""
    skill_pct = skill.get("skill_pct", 50)
    color = CHART_GREEN if skill_pct >= 55 else CHART_AMBER
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=skill_pct,
        delta={"reference": 50, "suffix": "% vs random"},
        number={"suffix": "% Skill", "font": {"color": CHART_GREEN, "size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#E8F5E9"},
            "bar":  {"color": color},
            "threshold": {"line": {"color": CHART_AMBER, "width": 3}, "value": 50},
        },
        title={"text": "Skill % (> 50% = statistically skilled)",
               "font": {"color": "#E8F5E9"}},
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG,
        height=280, margin=dict(l=30, r=30, t=50, b=30),
    )
    return fig


def chart_monthly_pnl(df: pd.DataFrame) -> go.Figure:
    """Monthly PnL bar chart."""
    if "pnl" not in df.columns:
        return go.Figure()
    date_col = "exit_date" if "exit_date" in df.columns else "entry_date"
    if date_col not in df.columns:
        return go.Figure()
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["_label"] = df[date_col].dt.strftime("%Y-%m")
    monthly = df.groupby("_label")["pnl"].sum().reset_index()
    colors  = [CHART_GREEN if v >= 0 else CHART_RED for v in monthly["pnl"]]
    fig = go.Figure(go.Bar(
        x=monthly["_label"], y=monthly["pnl"],
        marker=dict(color=colors),
        text=[f"₹{v:,.0f}" for v in monthly["pnl"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="📅 Monthly PnL",
        template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"), xaxis_tickangle=-45,
        height=300, margin=dict(l=40, r=20, t=45, b=60),
    )
    return fig


def chart_hold_distribution(df: pd.DataFrame) -> go.Figure:
    """Hold days histogram."""
    if "hold_days" not in df.columns:
        return go.Figure()
    fig = px.histogram(
        df, x="hold_days", nbins=30,
        title="⏱️ Hold Duration Distribution",
        color_discrete_sequence=[CHART_GREEN],
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"), xaxis_title="Hold Days", yaxis_title="Trade Count",
        height=280, margin=dict(l=40, r=20, t=45, b=40),
    )
    return fig


def chart_dna_scores(dna: dict) -> go.Figure:
    """Trader DNA radar chart — 6 dimensions."""
    dims = ["Precision", "Patience", "Consistency", "Risk Control", "Adaptability", "Sector Mastery"]
    keys = ["precision", "patience", "consistency", "risk_control", "adaptability", "sector_mastery"]
    values = [dna.get(k, dna.get(d, 50)) for k, d in zip(keys, dims)]
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=dims + [dims[0]],
        fill="toself",
        fillcolor="rgba(0,200,83,0.2)",
        line=dict(color=CHART_GREEN, width=2),
        name=dna.get("archetype", "Trader DNA"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=CHART_BG,
            radialaxis=dict(visible=True, range=[0, 100], color="#E8F5E9"),
            angularaxis=dict(color="#E8F5E9"),
        ),
        title=f"🧬 Trader DNA — {dna.get('archetype', 'Profile')}",
        template="plotly_dark", paper_bgcolor=CHART_BG,
        font=dict(color="#E8F5E9"),
        height=320, margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig