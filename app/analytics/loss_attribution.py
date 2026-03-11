# =============================================================================
# FINTECH555 — Module 4: Loss Attribution
# ML Concepts: Random Forest Classifier, SHAP values, Rule-based classification
# =============================================================================
import pandas as pd
import numpy as np
from config.settings import MIN_TRADES_ML


def compute_loss_attribution(df: pd.DataFrame) -> dict:
    """
    Classify each loss into: Panic Exit, Premature Exit, Poor Entry,
    Position Oversizing, Market Conditions using rule-based + ML classification.
    SHAP: SHapley Additive exPlanations — game theory credit distribution across features
    """
    losers = df[df["is_loser"]].copy()
    if len(losers) == 0:
        return {"categories": {}, "top_losses": pd.DataFrame(), "shap_vals": None}

    # Rule-based classification
    def classify_loss(row):
        if row.get("is_panic_trade", False):            return "Panic Exit"
        if row.get("is_premature_exit", False):         return "Premature Exit"
        if row.get("is_oversized", False):              return "Position Oversizing"
        if row.get("hold_days", 0) <= 1:                return "Poor Entry Timing"
        return "Market Conditions"

    losers["loss_cause"] = losers.apply(classify_loss, axis=1)
    categories = losers.groupby("loss_cause")["pnl_abs"].agg(["count", "sum"]).reset_index()
    categories.columns = ["cause", "count", "total_loss"]

    # Use available columns - handle both old (stock_symbol/buy_date) and new (symbol/entry_date) schemas
    top_cols = []
    for c in ["stock_symbol", "symbol", "buy_date", "entry_date", "pnl_abs", "pnl", "hold_days", "loss_cause"]:
        if c in losers.columns and c not in top_cols:
            top_cols.append(c)
    top_losses = losers.nsmallest(5, "pnl_abs")[top_cols].copy() if "pnl_abs" in losers.columns else losers.head(5)

    # RF + SHAP if enough data
    shap_vals, rf_importance = None, {}
    if len(df) >= MIN_TRADES_ML:
        try:
            from sklearn.ensemble import RandomForestClassifier
            import shap

            feat_cols = [c for c in ["hold_days", "capital_deployed", "pnl_pct", "capital_vs_avg"] if c in df.columns]
            X = df[feat_cols].fillna(0)
            y = df["is_winner"].astype(int)

            rf = RandomForestClassifier(n_estimators=50, random_state=42)
            rf.fit(X, y)

            explainer = shap.TreeExplainer(rf)
            shap_vals = explainer.shap_values(X)
            rf_importance = dict(zip(feat_cols, rf.feature_importances_))
        except Exception:
            pass

    return {
        "categories": categories.to_dict("records"),
        "top_losses": top_losses,
        "shap_vals": shap_vals,
        "rf_importance": rf_importance,
        "total_losses": len(losers),
        "total_loss_amount": round(losers["pnl_abs"].sum(), 0),
    }
