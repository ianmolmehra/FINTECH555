# =============================================================================
# FINTECH555 — Module 8: Tax Intelligence
# ML Concepts: LTCG/STCG classification, Tax Optimization Score
# =============================================================================
import pandas as pd
import numpy as np
from config.settings import TAX


def compute_tax(df: pd.DataFrame) -> dict:
    """
    Compute Indian capital gains tax liability and optimization score.
    STCG: < 365 days held → 15% tax (Section 111A)
    LTCG: >= 365 days held → 10% above Rs. 1,00,000 exemption (Section 112A)
    Tax Optimization Score 0-100: measures LTCG conversion ratio
    """
    # ── Extract tax constants from settings.TAX dict
    STCG_RATE         = TAX["stcg_rate"]           # 15% Short-Term Capital Gains
    LTCG_RATE         = TAX["ltcg_rate"]           # 10% Long-Term Capital Gains
    LTCG_EXEMPTION    = TAX["ltcg_exemption"]      # Rs. 1,00,000 annual exemption
    LTCG_HOLDING_DAYS = TAX["ltcg_threshold_days"] # 365 days threshold
    if len(df) == 0:
        return {"total_tax": 0, "stcg_tax": 0, "ltcg_tax": 0,
                "total_tax_paid": 0, "after_tax_pnl": 0,
                "tax_score": 0, "tax_opt_score": 0, "monthly_tax": pd.DataFrame(), "summary": {}}

    # ── Column name normalization — handle both old (is_winner/pnl_abs) and new (is_profit/pnl) schemas
    if "is_winner" not in df.columns and "is_profit" in df.columns:
        df = df.copy()
        df["is_winner"] = df["is_profit"].astype(bool)  # Alias is_profit → is_winner
    if "pnl_abs" not in df.columns and "pnl" in df.columns:
        df = df.copy()
        df["pnl_abs"] = df["pnl"].abs()  # pnl_abs = absolute value of pnl

    winners = df[df["is_winner"]].copy()
    winners["is_ltcg"] = winners["hold_days"] >= LTCG_HOLDING_DAYS

    stcg_gains = winners[~winners["is_ltcg"]]["pnl_abs"].sum()
    ltcg_gains = winners[winners["is_ltcg"]]["pnl_abs"].sum()
    ltcg_taxable = max(0, ltcg_gains - LTCG_EXEMPTION)  # First 1L exempt

    stcg_tax = stcg_gains * STCG_RATE
    ltcg_tax = ltcg_taxable * LTCG_RATE
    total_tax = stcg_tax + ltcg_tax

    # Tax Optimization Score: what fraction of gains are LTCG (lower taxed)?
    total_gains = max(1, stcg_gains + ltcg_gains)
    ltcg_ratio  = ltcg_gains / total_gains
    tax_score   = round(ltcg_ratio * 100, 1)

    if "trade_year" in df.columns and "trade_month" in df.columns:
        monthly = winners.groupby(["trade_year", "trade_month"]).agg(
            stcg=("pnl_abs", lambda x: x[~winners.loc[x.index, "is_ltcg"]].sum()),
            ltcg=("pnl_abs", lambda x: x[winners.loc[x.index, "is_ltcg"]].sum()),
        ).reset_index()
    else:
        monthly = pd.DataFrame()

    return {
        "total_tax": round(total_tax, 0), "stcg_tax": round(stcg_tax, 0),
        "ltcg_tax": round(ltcg_tax, 0), "stcg_gains": round(stcg_gains, 0),
        "ltcg_gains": round(ltcg_gains, 0), "ltcg_taxable": round(ltcg_taxable, 0),
        "ltcg_exemption_used": round(min(LTCG_EXEMPTION, ltcg_gains), 0),
        "tax_score": tax_score, "ltcg_ratio": round(ltcg_ratio * 100, 1),
        "monthly_tax": monthly, "n_stcg_trades": int((~winners["is_ltcg"]).sum()),
        "n_ltcg_trades": int(winners["is_ltcg"].sum()),
        "total_tax_paid": round(total_tax, 0),
        "after_tax_pnl": round(df["pnl"].sum() - total_tax, 0) if "pnl" in df.columns else 0,
        "tax_opt_score": tax_score,
        "monthly_tax": monthly,
    }


# ── Alias for report.py compatibility
def compute_tax_insights(df):
    """Alias for compute_tax() — called by report.py."""
    result = compute_tax(df)
    # Normalize key names
    if "total_tax" in result and "total_tax_paid" not in result:
        result["total_tax_paid"] = result["total_tax"]
    if "after_tax" in result and "after_tax_pnl" not in result:
        result["after_tax_pnl"] = result["after_tax"]
    if "stcg" in result and "stcg_tax" not in result:
        result["stcg_tax"] = result["stcg"]
    if "ltcg" in result and "ltcg_tax" not in result:
        result["ltcg_tax"] = result["ltcg"]
    return result
