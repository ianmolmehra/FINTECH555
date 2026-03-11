# =============================================================================
# FINTECH555 — Module 9: Annual Review & Year-over-Year Comparison
# ML Concepts: YoY trend analysis, Report Card grading
# =============================================================================
import pandas as pd
import numpy as np


def compute_annual_review(df: pd.DataFrame) -> dict:
    """
    Year-over-year comparison of all key metrics.
    Assigns letter grades A/B/C/D/F per dimension per year.
    """
    if "trade_year" not in df.columns and "year" in df.columns:
        df = df.copy()
        df["trade_year"] = df["year"]
    if "trade_year" not in df.columns:
        return {"annual_stats": pd.DataFrame(), "grades": {}}

    annual = df.groupby("trade_year").agg(
        trade_count=("is_profit", "count"),
        win_rate=("is_profit", "mean"),
        avg_hold=("hold_days", "mean"),
        total_pnl=("pnl", "sum"),
        panic_rate=("is_panic_trade", "mean") if "is_panic_trade" in df.columns else ("is_winner", "mean"),
    ).reset_index()
    annual["win_rate"] = (annual["win_rate"] * 100).round(1)
    annual["avg_hold"] = annual["avg_hold"].round(1)

    def grade(val, thresholds):
        a, b, c, d = thresholds
        if val >= a:  return "A"
        elif val >= b: return "B"
        elif val >= c: return "C"
        elif val >= d: return "D"
        else:          return "F"

    grades = {}
    for _, row in annual.iterrows():
        yr = row["trade_year"]
        grades[yr] = {
            "Win Rate":  grade(row["win_rate"], [65, 55, 45, 35]),
            "Avg Hold":  grade(row["avg_hold"], [35, 20, 10, 5]),
            "Total PnL": grade(row["total_pnl"], [50000, 20000, 0, -20000]),
        }

    return {"annual_stats": annual, "grades": grades}
