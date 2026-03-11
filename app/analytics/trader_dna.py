# =============================================================================
# FINTECH555 — Module 5: Trader DNA Profile
# ML Concepts: Multi-dimensional scoring matrix, Radar chart profiling
# =============================================================================
import pandas as pd
import numpy as np


def compute_trader_dna(df: pd.DataFrame, dis_result: dict, panic_result: dict) -> dict:
    """
    6-dimensional scoring matrix classifying trader archetype.
    Dimensions: Precision, Patience, Consistency, Risk Control, Adaptability, Sector Mastery
    Archetypes: Precision Trader, Trend Follower, Impulsive, Defensive, Opportunistic
    """
    if len(df) == 0:
        return _empty_dna()

    # ── Normalize columns — handle any column name variant
    df = df.copy()
    if "is_winner" not in df.columns and "is_profit" in df.columns:
        df["is_winner"] = df["is_profit"].astype(bool)
    if "is_winner" not in df.columns and "pnl" in df.columns:
        df["is_winner"] = (df["pnl"] > 0)

    if "capital_deployed" not in df.columns:
        if "entry_price" in df.columns and "quantity" in df.columns:
            df["capital_deployed"] = df["entry_price"] * df["quantity"]
        else:
            df["capital_deployed"] = 10000

    if "hold_days" not in df.columns:
        df["hold_days"] = 7

    n        = len(df)
    avg_hold = df["hold_days"].mean()
    win_rate = df["is_winner"].mean() * 100

    # ── Dimension 1: Precision (0-100) — win rate weighted by patience
    precision = min(100, win_rate * min(1.5, max(0.5, avg_hold / 15)))

    # ── Dimension 2: Patience (0-100) — avg hold days (30 days = full score)
    patience = min(100, (avg_hold / 30) * 100)

    # ── Dimension 3: Consistency (0-100) — low CV of position sizing = consistent
    cap_mean    = df["capital_deployed"].mean()
    cap_std     = df["capital_deployed"].std()
    cv          = cap_std / max(1, cap_mean)
    consistency = max(0, min(100, 100 - cv * 60))

    # ── Dimension 4: Risk Control (0-100) — from panic module behavioral health
    risk_control = panic_result.get("behavioral_health_score",
                   panic_result.get("bhs", max(0, min(100, win_rate * 1.2))))

    # ── Dimension 5: Adaptability (0-100) — improvement in win rate over time
    early        = df.iloc[:n//3]["is_winner"].mean() if n >= 6 else 0.5
    late         = df.iloc[-n//3:]["is_winner"].mean() if n >= 6 else 0.5
    adaptability = min(100, max(0, (late - early + 0.5) * 100))

    # ── Dimension 6: Sector Mastery (0-100) — best sector win rate
    if "sector" in df.columns and df["sector"].nunique() > 1:
        sector_wr     = df.groupby("sector")["is_winner"].mean()
        sector_mastery = min(100, sector_wr.max() * 100)
    else:
        sector_mastery = min(100, win_rate * 1.1)

    dims = {
        "Precision":      round(precision, 1),
        "Patience":       round(patience, 1),
        "Consistency":    round(consistency, 1),
        "Risk Control":   round(risk_control, 1),
        "Adaptability":   round(adaptability, 1),
        "Sector Mastery": round(sector_mastery, 1),
    }

    # ── Archetype classification
    if precision > 65 and consistency > 65:      archetype = "Precision Trader"
    elif patience > 65 and adaptability > 60:    archetype = "Trend Follower"
    elif adaptability < 35 and consistency < 40: archetype = "Impulsive"
    elif risk_control > 70 and patience > 50:    archetype = "Defensive"
    else:                                         archetype = "Opportunistic"

    style_map = {
        "Precision Trader": "Focus on high-conviction entries with strict stop-losses.",
        "Trend Follower":   "Ride momentum with trailing stops and patience.",
        "Impulsive":        "Slow down — trade fewer, higher-quality setups.",
        "Defensive":        "Increase position size on your strongest setups.",
        "Opportunistic":    "Swing trading with defined exits.",
    }

    return {
        "dimensions":        dims,
        "archetype":         archetype,
        "recommended_style": style_map.get(archetype, ""),
        "n_trades":          n,
        # ── Flat keys for report.py kpi_strip
        "precision":         dims["Precision"],
        "patience":          dims["Patience"],
        "consistency":       dims["Consistency"],
        "risk_control":      dims["Risk Control"],
        "adaptability":      dims["Adaptability"],
        "sector_mastery":    dims["Sector Mastery"],
    }


def _empty_dna() -> dict:
    empty_dims = {
        "Precision": 0, "Patience": 0, "Consistency": 0,
        "Risk Control": 0, "Adaptability": 0, "Sector Mastery": 0,
    }
    return {
        "dimensions":        empty_dims,
        "archetype":         "Unknown",
        "recommended_style": "Upload more trades to unlock your DNA profile.",
        "n_trades":          0,
        "precision": 0, "patience": 0, "consistency": 0,
        "risk_control": 0, "adaptability": 0, "sector_mastery": 0,
    }


def profile_trader_dna(df, panic_result=None):
    """Alias for compute_trader_dna() — called by report.py."""
    return compute_trader_dna(df, {}, panic_result or {})