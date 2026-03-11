# =============================================================================
# FINTECH555 — Module 10: Prediction Engine
# ML Concepts: Gradient Boosting, Ridge Regression, k-NN Regression
# =============================================================================
import pandas as pd
import numpy as np
from config.settings import BIAS


def compute_predictions(df: pd.DataFrame) -> dict:
    """
    Three predictive models from trader's own historical data.
    GBM: F_m(x) = F_{m-1}(x) + gamma × h_m(x) — sequential ensemble
    Ridge: minimizes MSE + lambda×||w||² — L2 regularization prevents overfitting
    k-NN: predicts by averaging k most similar historical trades (Euclidean distance)
    """
    if len(df) < BIAS["min_trades_for_ml"]:
        return {"next_win_prob": 0.5, "next_hold_rec": 10, "accuracy": 0.5,
                "feature_imp": {}, "n_trades": len(df), "sufficient_data": False}

    feat_cols = [c for c in ["hold_days", "capital_deployed", "capital_vs_avg",
                              "trade_dow", "pnl_pct"] if c in df.columns]
    X = df[feat_cols].fillna(0).values
    y = df["is_winner"].astype(int).values

    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import Ridge
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    # GBM: F_m(x) = F_{m-1}(x) + γ × h_m(x) — each tree corrects prior errors
    gbc = GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, random_state=42)
    cv  = cross_val_score(gbc, X_sc, y, cv=min(5, len(df)//4), scoring="accuracy")
    gbc.fit(X_sc, y)
    last_3 = X_sc[-3:].mean(axis=0).reshape(1, -1)
    next_win_prob = float(gbc.predict_proba(last_3)[0][1])
    feature_imp   = dict(zip(feat_cols, gbc.feature_importances_))

    # k-NN: predict hold duration from similar past trades
    y_hold = df["hold_days"].values
    knn = KNeighborsRegressor(n_neighbors=min(5, len(df)-1))
    knn.fit(X_sc, y_hold)
    next_hold = float(knn.predict(last_3)[0])

    return {
        "next_win_prob":    round(next_win_prob * 100, 1),
        "next_hold_rec":    round(next_hold, 0),
        "accuracy":         round(cv.mean(), 3),
        "feature_imp":      feature_imp,
        "n_trades":         len(df),
        "sufficient_data":  True,
    }
