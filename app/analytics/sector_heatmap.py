# =============================================================================
# FINTECH555 — Module 7: Sector Skill Heatmap
# ML Concepts: Treemap visualization, Gini Coefficient, Herfindahl Index
# =============================================================================
import pandas as pd
import numpy as np


def compute_sector_heatmap(df: pd.DataFrame) -> dict:
    """
    Analyze performance by sector with concentration measures.
    Gini Coefficient: G = 1 - Σ(f_i × (S_i + S_{i-1})) — measures profit inequality
    Herfindahl Index: H = Σ(market_share_i²) — sector concentration (higher = more concentrated)
    """
    if len(df) == 0 or "sector" not in df.columns:
        return {"sector_stats": pd.DataFrame(), "gini": 0, "herfindahl": 0}

    sector_stats = df.groupby("sector").agg(
        trade_count=("is_profit", "count"),
        win_count=("is_profit", "sum"),
        total_pnl=("pnl", "sum"),
        avg_pnl=("pnl_abs", "mean"),
        total_capital=("capital_deployed", "sum"),
    ).reset_index()
    sector_stats["win_rate"] = (sector_stats["win_count"] / sector_stats["trade_count"] * 100).round(1)
    sector_stats["roi_pct"]  = (sector_stats["total_pnl"] / sector_stats["total_capital"] * 100).round(2)

    # Gini Coefficient: measures inequality in profit distribution across sectors
    profits = np.sort(sector_stats["total_pnl"].values)
    profits = profits[profits > 0]  # Only profitable sectors
    if len(profits) > 1:
        n = len(profits)
        cumulative = np.cumsum(profits)
        total = profits.sum()
        lorenz = cumulative / total
        lorenz = np.concatenate([[0], lorenz])
        freq   = np.linspace(0, 1, n + 1)
        # Gini = 1 - 2 × area under Lorenz curve (trapezoidal approximation)
        gini = 1 - 2 * np.trapz(lorenz, freq)
    else:
        gini = 0

    # Herfindahl-Hirschman Index: H = Σ(market_share_i²)
    # HHI > 0.25 = highly concentrated sector exposure
    total_trades = sector_stats["trade_count"].sum()
    shares = (sector_stats["trade_count"] / total_trades).values
    herfindahl = round(float(np.sum(shares**2)), 4)

    return {
        "sector_stats": sector_stats,
        "gini": round(float(gini), 4),
        "herfindahl": herfindahl,
        "best_sector": sector_stats.loc[sector_stats["win_rate"].idxmax(), "sector"] if len(sector_stats) > 0 else "N/A",
        "worst_sector": sector_stats.loc[sector_stats["win_rate"].idxmin(), "sector"] if len(sector_stats) > 0 else "N/A",
        "top_sector": sector_stats.loc[sector_stats["win_rate"].idxmax(), "sector"] if len(sector_stats) > 0 else "N/A",
        "weakest_sector": sector_stats.loc[sector_stats["win_rate"].idxmin(), "sector"] if len(sector_stats) > 0 else "N/A",
    }


def _get_worst_sector(sector_stats):
    """Helper: get worst sector by win rate."""
    if sector_stats.empty:
        return "N/A"
    return sector_stats.loc[sector_stats["win_rate"].idxmin(), "sector"]
