# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/upload/validator.py
# Purpose: Column validation and type coercion for all uploaded trade data.
#          Ensures every downstream analytics module receives clean, typed data.
# =============================================================================

import pandas as pd   # Pandas: DataFrame validation and type coercion
import numpy as np    # NumPy: numeric fill and computation
from datetime import datetime


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Validate and coerce all column types in the parsed DataFrame.

    Steps:
    1. Drop rows missing critical fields (stock_symbol, buy_date, pnl_abs)
    2. Parse date columns to datetime objects
    3. Compute hold_days from date difference
    4. Coerce all numeric columns with errors→NaN, then fill NaN with 0
    5. Add is_winner boolean column for convenience
    6. Add sector column from NSE_SECTOR_MAP lookup

    Args:
        df: Parsed DataFrame from broker_parser

    Returns:
        pd.DataFrame — fully validated and typed, or None on critical failure
    """

    if df is None or df.empty:
        return None  # Nothing to validate

    df = df.copy()  # Avoid mutating the input DataFrame in-place

    # ── Step 1: Drop rows with missing critical fields ─────────────────────
    # Without stock_symbol and buy_date, the trade is unidentifiable
    critical_cols = [c for c in ["stock_symbol", "buy_date"] if c in df.columns]
    df.dropna(subset=critical_cols, inplace=True)

    if df.empty:
        return None

    # ── Step 2: Parse date columns → datetime ──────────────────────────────
    # pandas.to_datetime: handles most date string formats automatically
    for date_col in ["buy_date", "sell_date"]:
        if date_col in df.columns:
            # errors='coerce' converts unparseable dates to NaT (not an error)
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True)

    # ── Step 3: Compute hold_days from date difference ─────────────────────
    # hold_days = (sell_date - buy_date).days — calendar days held
    if "buy_date" in df.columns and "sell_date" in df.columns:
        df["hold_days"] = (df["sell_date"] - df["buy_date"]).dt.days
        # Intraday trades (same day) get hold_days = 0; treat as 1 for division safety
        df["hold_days"] = df["hold_days"].fillna(0).astype(int)
        df["hold_days"] = df["hold_days"].clip(lower=0)  # No negative hold periods

    # ── Step 4: Coerce all numeric columns ────────────────────────────────
    numeric_cols = ["buy_price", "sell_price", "quantity", "capital_deployed",
                    "pnl_abs", "pnl_pct", "hold_days"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Step 5: Derived boolean columns ───────────────────────────────────
    # is_winner: True if pnl_abs > 0 — used in win rate calculations everywhere
    df["is_winner"] = df["pnl_abs"] > 0

    # is_loser: convenience inverse — used in loss attribution, panic detection
    df["is_loser"] = df["pnl_abs"] <= 0

    # ── Step 6: Add sector via NSE_SECTOR_MAP lookup ───────────────────────
    from config.settings import NSE_SECTOR_MAP
    # .map() applies dict lookup; fillna("Other") for unknown symbols
    df["sector"] = df["stock_symbol"].str.upper().str.strip().map(NSE_SECTOR_MAP).fillna("Other")

    # ── Step 7: Add year and month columns for temporal analysis ───────────
    if "buy_date" in df.columns:
        df["trade_year"]  = df["buy_date"].dt.year    # Year of entry
        df["trade_month"] = df["buy_date"].dt.month   # Month of entry (1-12)
        df["trade_dow"]   = df["buy_date"].dt.dayofweek  # 0=Mon, 4=Fri — for day-of-week analysis

    # ── Step 8: Ensure capital_deployed is positive and non-zero ───────────
    # Prevents division-by-zero in PnL% computations across all modules
    df["capital_deployed"] = df["capital_deployed"].abs().clip(lower=1.0)

    # Recompute pnl_pct from clean capital and pnl values — Formula: (PnL/Capital)×100
    df["pnl_pct"] = (df["pnl_abs"] / df["capital_deployed"]) * 100

    # ── Step 9: Sort by buy_date ascending — chronological order matters ───
    if "buy_date" in df.columns:
        df = df.sort_values("buy_date").reset_index(drop=True)

    # ── Step 10: Add trade index for visual labeling ───────────────────────
    df["trade_num"] = range(1, len(df) + 1)  # 1-indexed trade number

    return df


def validate_dataframe(df: pd.DataFrame):
    """
    Validate and coerce broker-parsed DataFrame into cleaner-ready standard schema.
    
    Overrides the class above with a streamlined version that:
    1. Accepts broker_parser output (symbol, entry_date, exit_date, pnl, etc.)
    2. Normalizes column names to match cleaner.py expectations
    3. Returns (validated_df, warnings_list) tuple
    
    Args:
        df: DataFrame from broker_parser.detect_and_parse_broker()
    
    Returns:
        Tuple (pd.DataFrame, list[str]) — clean df and any data quality warnings
    """
    warnings = []

    if df is None or df.empty:
        return None, ["Empty file — no trades found"]

    df = df.copy()

    # ── Normalize column names: handle both broker_parser and legacy names
    # broker_parser already outputs standard names (symbol, entry_date, etc.)
    # Legacy validator used: stock_symbol, buy_date, sell_date, pnl_abs
    rename_map = {
        "stock_symbol": "symbol",
        "buy_date": "entry_date",
        "sell_date": "exit_date",
        "buy_price": "entry_price",
        "sell_price": "exit_price",
        "pnl_abs": "pnl",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ── Ensure required columns exist (critical for all analytics)
    required = ["symbol", "entry_date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, [f"Missing required columns: {missing}. Check file format."]

    # ── Parse date columns to datetime
    for col in ["entry_date", "exit_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)

    # ── Compute hold_days if not present
    if "hold_days" not in df.columns:
        if "entry_date" in df.columns and "exit_date" in df.columns:
            df["hold_days"] = (df["exit_date"] - df["entry_date"]).dt.days.fillna(0).astype(int)
            df["hold_days"] = df["hold_days"].clip(lower=0)
        else:
            df["hold_days"] = 5  # Default 5 days if dates unavailable

    # ── Ensure pnl column exists and is numeric
    if "pnl" not in df.columns:
        # Try to compute from prices if available
        if all(c in df.columns for c in ["entry_price", "exit_price", "quantity"]):
            df["pnl"] = (df["exit_price"] - df["entry_price"]) * df["quantity"]
            warnings.append("PnL computed from price difference × quantity.")
        else:
            df["pnl"] = 0.0
            warnings.append("⚠️ PnL column not found — set to 0. Check file format.")

    # ── Coerce numeric columns
    numeric_cols = ["entry_price", "exit_price", "quantity", "capital_deployed", "pnl", "pnl_pct", "hold_days"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Ensure capital_deployed exists
    if "capital_deployed" not in df.columns:
        if "entry_price" in df.columns and "quantity" in df.columns:
            df["capital_deployed"] = (df["entry_price"] * df["quantity"]).abs().clip(lower=1.0)
        else:
            df["capital_deployed"] = 10000.0  # Placeholder capital

    # ── Ensure pnl_pct exists
    if "pnl_pct" not in df.columns or df["pnl_pct"].eq(0).all():
        cap = df["capital_deployed"].replace(0, 1)
        df["pnl_pct"] = (df["pnl"] / cap) * 100

    # ── Ensure sector column
    if "sector" not in df.columns:
        from config.settings import NSE_SECTOR_MAP
        df["sector"] = df["symbol"].str.upper().str.strip().map(NSE_SECTOR_MAP).fillna("Unknown")

    # ── Sort chronologically
    if "entry_date" in df.columns:
        df = df.sort_values("entry_date").reset_index(drop=True)

    # ── Data quality warnings
    null_pnl = df["pnl"].isna().sum()
    if null_pnl > 0:
        warnings.append(f"{null_pnl} trades have missing PnL — excluded from analytics.")

    df.dropna(subset=["entry_date"], inplace=True)

    return df, warnings
