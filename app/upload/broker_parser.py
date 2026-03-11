"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/upload/broker_parser.py
Purpose: Universal auto-detection — works with ANY broker file format.
         Uses keyword fuzzy matching to identify columns by meaning, not name.
         No manual mapping needed. Handles BUY/SELL order logs too.
================================================================================
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional, Dict


# ── KEYWORD MAP — for each standard field, list all possible column name variants
# The parser scores each column against these keywords and picks the best match.
FIELD_KEYWORDS = {
    "symbol": [
        "symbol", "scrip", "stock", "ticker", "script", "name",
        "stock_name", "scripname", "instrument", "security", "asset"
    ],
    "trade_type": [
        "type", "trade_type", "buy_sell", "buysell", "action",
        "transaction_type", "order_type", "side", "direction", "b/s"
    ],
    "quantity": [
        "quantity", "qty", "units", "shares", "lot", "volume",
        "no_of_shares", "no._of_shares", "lots", "amount_of_shares"
    ],
    "value": [
        "value", "amount", "net_amount", "total", "turnover",
        "trade_value", "consideration", "net_value", "gross_value"
    ],
    "price": [
        "price", "rate", "tradeprice", "trade_price", "avg_price",
        "average_price", "execution_price", "ltp", "close_price"
    ],
    "entry_price": [
        "buy_price", "entry_price", "purchase_price", "avg_buy_price",
        "buying_price", "cost_price", "open_price"
    ],
    "exit_price": [
        "sell_price", "exit_price", "selling_price", "avg_sell_price",
        "sale_price", "close_price", "closing_price"
    ],
    "date": [
        "date", "time", "datetime", "trade_date", "order_date",
        "execution_date", "transaction_date", "timestamp",
        "execution_date_and_time", "trade_time", "order_time"
    ],
    "entry_date": [
        "buy_date", "entry_date", "purchase_date", "open_date", "from_date"
    ],
    "exit_date": [
        "sell_date", "exit_date", "sale_date", "close_date", "to_date"
    ],
    "pnl": [
        "pnl", "profit", "loss", "p&l", "net_profit", "gain",
        "profit_loss", "realized_pnl", "net_gain", "return"
    ],
    "sector": [
        "sector", "industry", "segment", "category", "group"
    ],
    "hold_days": [
        "hold_days", "holding_days", "days_held", "duration", "holding_period"
    ],
    "isin": ["isin"],
    "exchange": ["exchange", "market", "bse", "nse"],
}


def _find_real_header_row(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Scans rows top-to-bottom to find the actual column header row.
    Some broker files have client name, date range, etc. at the top.
    Detects header by counting how many cells match known financial keywords.
    """
    ALL_KEYWORDS = set()
    for kws in FIELD_KEYWORDS.values():
        ALL_KEYWORDS.update(kws)

    for i, row in raw_df.iterrows():
        row_vals = [str(v).strip().lower().replace(" ", "_") for v in row.values if v is not None]
        matches = sum(1 for v in row_vals if any(kw in v for kw in ALL_KEYWORDS))
        if matches >= 3:
            new_df = raw_df.iloc[i + 1:].copy()
            new_df.columns = [str(v).strip() for v in raw_df.iloc[i].values]
            new_df = new_df.dropna(how="all").reset_index(drop=True)
            return new_df
    return raw_df


def _score_column(col_name: str, keywords: list) -> int:
    """
    Scores how well a column name matches a list of keywords.
    Uses substring matching so partial matches count too.
    e.g. 'execution_date_and_time' matches keyword 'date' → score 1
    """
    col = col_name.lower().replace(" ", "_")
    score = 0
    for kw in keywords:
        if kw == col:          score += 10   # exact match
        elif kw in col:        score += 5    # substring match
        elif col in kw:        score += 3    # reverse substring
    return score


def _auto_detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    For each standard field, find the best matching column in the DataFrame.
    Returns mapping: {standard_field -> actual_column_name}
    Uses a greedy scoring approach — each column can only be assigned once.
    """
    cols = list(df.columns)
    used = set()
    mapping = {}

    # Priority order — most important fields first
    priority_fields = [
        "symbol", "trade_type", "quantity", "entry_date", "exit_date",
        "date", "entry_price", "exit_price", "price", "value",
        "pnl", "sector", "hold_days", "isin", "exchange"
    ]

    for field in priority_fields:
        keywords = FIELD_KEYWORDS.get(field, [field])
        best_col   = None
        best_score = 0

        for col in cols:
            if col in used:
                continue
            score = _score_column(col, keywords)
            if score > best_score:
                best_score = score
                best_col   = col

        if best_col and best_score >= 3:
            mapping[field] = best_col
            used.add(best_col)

    return mapping


def _pair_buy_sell_orders(df: pd.DataFrame, field_map: Dict[str, str]) -> pd.DataFrame:
    """
    Converts a BUY/SELL order log into paired completed trades using FIFO.
    Works with any column names — uses the field_map from auto-detection.
    """
    sym_col   = field_map.get("symbol")
    type_col  = field_map.get("trade_type")
    qty_col   = field_map.get("quantity")
    val_col   = field_map.get("value") or field_map.get("price")
    date_col  = field_map.get("entry_date") or field_map.get("date")

    if not all([sym_col, type_col, qty_col, val_col, date_col]):
        return pd.DataFrame()

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=[date_col, sym_col]).sort_values(date_col).reset_index(drop=True)
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce").fillna(0)

    # Per-share price: if value looks like total (large number), divide by qty
    df["_price"] = df.apply(
        lambda r: r[val_col] / r[qty_col] if r[qty_col] > 1 and r[val_col] > r[qty_col] else r[val_col],
        axis=1
    )
    df["_type"] = df[type_col].astype(str).str.strip().str.upper()

    buys   = {}
    trades = []

    for _, row in df.iterrows():
        sym   = str(row[sym_col]).strip().upper()
        qty   = float(row[qty_col])
        price = float(row["_price"])
        dt    = row[date_col]
        typ   = row["_type"]

        if typ in ["BUY", "B", "P", "PURCHASE"]:
            buys.setdefault(sym, []).append({"date": dt, "price": price, "qty": qty})

        elif typ in ["SELL", "S", "SALE"] and buys.get(sym):
            buy = buys[sym].pop(0)
            matched_qty = min(qty, buy["qty"])
            pnl         = (price - buy["price"]) * matched_qty
            hold_days   = max(1, (dt - buy["date"]).days)
            trades.append({
                "symbol":           sym,
                "entry_date":       buy["date"].date(),
                "exit_date":        dt.date(),
                "entry_price":      round(buy["price"], 2),
                "exit_price":       round(price, 2),
                "quantity":         matched_qty,
                "pnl":              round(pnl, 2),
                "pnl_pct":          round((price - buy["price"]) / max(buy["price"], 1) * 100, 2),
                "hold_days":        hold_days,
                "capital_deployed": round(buy["price"] * matched_qty, 2),
            })

    return pd.DataFrame(trades) if trades else pd.DataFrame()


def detect_and_parse_broker(
    raw_df: pd.DataFrame
) -> Tuple[Optional[pd.DataFrame], str, Dict]:
    """
    Universal broker parser — works with any file format automatically.

    Steps:
    1. Find the real header row (skips metadata at top of file)
    2. Auto-detect what each column means using keyword scoring
    3. If it looks like a BUY/SELL log → pair orders into completed trades
    4. If it already has entry/exit prices → use directly
    5. Last resort → show manual mapping UI
    """
    # Step 1: Find the real header row
    raw_df = _find_real_header_row(raw_df)
    raw_df = raw_df.dropna(how="all")
    raw_df.columns = [str(c).strip() for c in raw_df.columns]

    # Step 2: Auto-detect columns
    field_map = _auto_detect_columns(raw_df)

    # Step 3: Check if it's a BUY/SELL order log
    type_col = field_map.get("trade_type")
    if type_col and type_col in raw_df.columns:
        unique_types = raw_df[type_col].astype(str).str.upper().str.strip().unique()
        is_order_log = any(t in ["BUY", "SELL", "B", "S", "PURCHASE", "SALE"]
                           for t in unique_types)
        has_no_exit  = "exit_price" not in field_map and "exit_date" not in field_map

        if is_order_log and has_no_exit:
            paired = _pair_buy_sell_orders(raw_df, field_map)
            if not paired.empty:
                st.success(
                    f"✅ Auto-detected order history format — "
                    f"matched **{len(paired)} completed trades** from BUY/SELL orders."
                )
                return paired, "Auto-Detected (Order Log)", field_map

    # Step 4: Already has entry + exit — rename and return directly
    rename = {}
    for std_field, actual_col in field_map.items():
        if actual_col in raw_df.columns:
            rename[actual_col] = std_field

    if rename:
        result = raw_df.rename(columns=rename)
        # Consolidate date columns
        if "entry_date" not in result.columns and "date" in result.columns:
            result["entry_date"] = result["date"]
        # Consolidate price columns
        if "entry_price" not in result.columns and "price" in result.columns:
            result["entry_price"] = result["price"]
        broker_name = "Auto-Detected"
        st.success(f"✅ Auto-detected columns: {list(rename.values())}")
        return result, broker_name, field_map

    # Step 5: Last resort — manual mapping
    st.warning("⚠️ Could not auto-detect columns. Please map manually below.")
    return _render_manual_mapping_ui(raw_df), "Manual", {}


def _render_manual_mapping_ui(raw_df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Fallback manual mapping UI — only shown if auto-detection fails."""
    st.markdown("#### 🔧 Manual Column Mapping")
    st.markdown("Match your file's columns to the fields below:")

    standard_fields = {
        "symbol":      "Stock Symbol (e.g. RELIANCE, TCS)",
        "entry_date":  "Trade Entry / Buy Date",
        "exit_date":   "Trade Exit / Sell Date",
        "entry_price": "Entry / Buy Price per share",
        "exit_price":  "Exit / Sell Price per share",
        "quantity":    "Number of shares / units",
        "pnl":         "Profit or Loss amount (₹)",
    }

    available_cols = ["-- Not in file --"] + list(raw_df.columns)
    user_mapping   = {}

    for std_field, description in standard_fields.items():
        selected = st.selectbox(
            label=f"`{std_field}` — {description}",
            options=available_cols,
            key=f"manual_map_{std_field}"
        )
        if selected != "-- Not in file --":
            user_mapping[selected] = std_field

    if st.button("✅ Apply Mapping"):
        if len(user_mapping) < 4:
            st.error("Please map at least: symbol, entry_date, entry_price, quantity")
            return None
        mapped_df = raw_df.rename(columns=user_mapping)
        st.success("Column mapping applied!")
        return mapped_df

    return None