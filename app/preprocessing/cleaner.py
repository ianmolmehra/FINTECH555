"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/preprocessing/cleaner.py
Purpose: Feature engineering pipeline — derives all computed columns used by
         every analytics module. Run once after upload, cache the result.
================================================================================
"""

import pandas as pd
import numpy as np
from config.settings import BIAS, NSE_SECTOR_MAP


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master feature engineering function. Derives all behavioral, temporal,
    and financial features used by downstream analytics modules.

    Concept: Feature Engineering — transforming raw data into ML-ready features.
    Principle: All features derived here; modules never re-derive them independently.

    Parameters:
        df: Validated DataFrame from validator.py

    Returns:
        df with 20+ derived feature columns appended
    """
    df = df.copy()  # Functional style — never mutate input

    # ── FEATURE 1: is_profit — binary win/loss label (1=win, 0=loss)
    # This is the supervised learning target variable for all classifiers
    df["is_profit"] = (df["pnl"] > 0).astype(int)

    # ── FEATURE 2: hold_days — number of days between entry and exit
    # Drives patience score, LTCG classification, and hold pattern analysis
    if "hold_days" not in df.columns or df["hold_days"].isna().all():
        df["hold_days"] = (df["exit_date"] - df["entry_date"]).dt.days.clip(lower=0)

    # ── FEATURE 3: capital_deployed — total capital at risk per trade
    # Formula: capital = entry_price × quantity (total position value at open)
    if "capital_deployed" not in df.columns or df["capital_deployed"].isna().all():
        df["capital_deployed"] = df["entry_price"] * df["quantity"]

    # ── FEATURE 4: pnl_pct — return percentage per trade
    # Formula: pnl_pct = (exit - entry) / entry × 100 — measures efficiency of capital use
    if "pnl_pct" not in df.columns or df["pnl_pct"].isna().all():
        df["pnl_pct"] = ((df["exit_price"] - df["entry_price"]) / df["entry_price"]) * 100

    # ── FEATURE 5: capital_pct — position size as % of median capital deployed
    # Coefficient of Variation of capital_pct measures sizing consistency
    median_capital = df["capital_deployed"].median()
    df["capital_pct"] = (df["capital_deployed"] / median_capital) * 100 if median_capital > 0 else 100.0

    # ── FEATURE 6: is_oversized — position > 1.8x average capital
    # BIAS["oversize_multiplier"] = 1.8 from settings — flags position size discipline
    avg_capital = df["capital_deployed"].mean()
    df["is_oversized"] = (df["capital_deployed"] > avg_capital * BIAS["oversize_multiplier"]).astype(int)

    # ── FEATURE 7: is_quick_trade — closed within 30 minutes
    # Short holding period combined with a loss = potential panic exit signal
    # Formula: duration_minutes = hold_days × 1440 (approx, for sub-day trades)
    df["is_quick_trade"] = (df["hold_days"] == 0).astype(int)

    # ── FEATURE 8: is_ltcg — held >= 365 days (qualifies for LTCG tax rate)
    # LTCG threshold from settings.TAX["ltcg_threshold_days"]
    df["is_ltcg"] = (df["hold_days"] >= 365).astype(int)

    # ── FEATURE 9: day_of_week — 0=Monday … 4=Friday
    # Used in time pattern analysis to detect weekday performance bias
    df["day_of_week"] = df["entry_date"].dt.dayofweek
    df["day_name"] = df["entry_date"].dt.day_name()

    # ── FEATURE 10: month_of_year — 1=Jan … 12=Dec (seasonality detection)
    df["month"] = df["entry_date"].dt.month
    df["month_name"] = df["entry_date"].dt.strftime("%b")
    df["year"] = df["entry_date"].dt.year

    # ── FEATURE 11: quarter — Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
    # Used in annual review for quarterly performance breakdown
    df["quarter"] = df["entry_date"].dt.quarter

    # ── FEATURE 12: is_panic_exit — quick trade that resulted in a loss
    # Combined signal: fast exit + loss = behavioral panic signature
    df["is_panic"] = ((df["is_quick_trade"] == 1) & (df["is_profit"] == 0)).astype(int)

    # ── FEATURE 13: pnl_rolling_3 — rolling 3-trade average PnL
    # Rolling window mean: smooths noise to reveal underlying performance trend
    df["pnl_rolling_3"] = df["pnl"].rolling(window=3, min_periods=1).mean()

    # ── FEATURE 14: pnl_cumulative — cumulative portfolio equity curve
    # Running sum of all PnL — used for drawdown and equity curve visualization
    df["pnl_cumulative"] = df["pnl"].cumsum()

    # ── FEATURE 15: portfolio_value — equity curve value (starts at 100 base)
    # Formula: normalized equity = 100 + cumulative returns (percent basis)
    initial_capital_estimate = df["capital_deployed"].sum() * 0.1  # Heuristic
    df["portfolio_value"] = initial_capital_estimate + df["pnl_cumulative"]

    # ── FEATURE 16: is_after_loss — True if the previous trade was a loss
    # Used to detect revenge trading: re-entry immediately after a loss
    df["prev_pnl"] = df["pnl"].shift(1)              # Shift by 1 to get previous trade's PnL
    df["is_after_loss"] = (df["prev_pnl"] < 0).astype(int)

    # ── FEATURE 17: is_revenge — entered after a loss AND resulted in a loss
    # Revenge trade = emotional re-entry that perpetuates the loss cycle
    df["is_revenge"] = ((df["is_after_loss"] == 1) & (df["is_profit"] == 0)).astype(int)

    # ── FEATURE 18: streak_id — identifies consecutive win/loss runs
    # Run-Length Encoding concept: group consecutive identical outcomes
    df["streak_group"] = (df["is_profit"] != df["is_profit"].shift()).cumsum()

    # ── FEATURE 19: sector from NSE_SECTOR_MAP if not already populated
    # Map symbol to sector using the pre-built lookup dictionary in settings
    if df["sector"].eq("Unknown").all():
        df["sector"] = df["symbol"].str.upper().map(NSE_SECTOR_MAP).fillna("Unknown")

    # ── FEATURE 20: log_return — natural log return for GBM / volatility estimation
    # Formula: log_return = ln(exit_price / entry_price) — additive returns for time series
    df["log_return"] = np.log(df["exit_price"] / df["entry_price"].replace(0, np.nan))

    return df


# ── Alias for backward compatibility with report.py import
# enrich_dataframe is the same as engineer_features — both transform raw df
def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Alias for engineer_features(). Called by report.py.
    Runs full feature engineering PLUS backward-compatible column aliases.
    Returns enriched DataFrame with 30+ derived columns ready for all modules.
    """
    enriched = engineer_features(df)       # Run 20+ feature derivations
    return normalize_columns(enriched)     # Add backward-compat aliases (is_winner, pnl_abs, etc.)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure backward-compatible column aliases exist after feature engineering.
    Adds is_winner (alias for is_profit) and pnl_abs (alias for abs(pnl)).
    Called automatically by enrich_dataframe() for full compatibility.
    """
    df = df.copy()
    # is_panic_trade: alias for is_panic — used in loss_attribution and annual_review
    if "is_panic_trade" not in df.columns and "is_panic" in df.columns:
        df["is_panic_trade"] = df["is_panic"]
    # is_loser: True if trade was unprofitable — alias for NOT is_profit
    if "is_loser" not in df.columns and "is_profit" in df.columns:
        df["is_loser"] = (~df["is_profit"].astype(bool))
    # is_winner: True if trade was profitable — alias for is_profit
    if "is_winner" not in df.columns and "is_profit" in df.columns:
        df["is_winner"] = df["is_profit"].astype(bool)
    # pnl_abs: absolute PnL value — used in loss attribution and tax modules
    if "pnl_abs" not in df.columns and "pnl" in df.columns:
        df["pnl_abs"] = df["pnl"].abs()
    # stock_symbol: alias for symbol — used in legacy broker_parser outputs
    if "stock_symbol" not in df.columns and "symbol" in df.columns:
        df["stock_symbol"] = df["symbol"]
    # buy_date: alias for entry_date — used in some modules
    if "buy_date" not in df.columns and "entry_date" in df.columns:
        df["buy_date"] = df["entry_date"]
    # sell_date: alias for exit_date
    if "sell_date" not in df.columns and "exit_date" in df.columns:
        df["sell_date"] = df["exit_date"]
    # buy_price / sell_price aliases
    if "buy_price" not in df.columns and "entry_price" in df.columns:
        df["buy_price"] = df["entry_price"]
    if "sell_price" not in df.columns and "exit_price" in df.columns:
        df["sell_price"] = df["exit_price"]
    # trade_year for annual_review
    if "trade_year" not in df.columns and "year" in df.columns:
        df["trade_year"] = df["year"]
    if "trade_month" not in df.columns and "month" in df.columns:
        df["trade_month"] = df["month"]
    return df
