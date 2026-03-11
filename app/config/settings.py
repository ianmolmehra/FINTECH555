"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/config/settings.py
Purpose: Central configuration hub — all thresholds, tax rates, constants,
         chart colors, and behavioral benchmark parameters.
================================================================================
"""

# ── CHART THEME — Dark FinTech color palette ─────────────────────────────────
THEME = {
    "bg": "#0A0F0A", "card_bg": "#111811", "panel_bg": "#141F14",
    "green": "#00C853", "amber": "#FFD600", "red": "#FF5252",
    "blue": "#448AFF", "purple": "#CE93D8",
    "text": "#E8F5E9", "subtext": "#81C784", "grid": "#1B2B1B",
}

# ── CHART COLOR CONSTANTS — used by charts.py ────────────────────────────────
CHART_BG    = "#0A0F0A"
CHART_GREEN = "#00C853"
CHART_AMBER = "#FFD600"
CHART_RED   = "#FF5252"
CHART_BLUE  = "#448AFF"
CHART_GOLD  = "#FFB300"

# ── ML CONFIG ─────────────────────────────────────────────────────────────────
MIN_TRADES_ML = 15         # Minimum trades required before running ML models

# ── INDIAN CAPITAL GAINS TAX — FY2024-25 rates ───────────────────────────────
TAX = {
    "stcg_rate": 0.15,
    "ltcg_rate": 0.10,
    "ltcg_threshold_days": 365,
    "ltcg_exemption": 100000,
    "cess_rate": 0.04,
}

# Flat constants for modules that import them directly
STCG_RATE         = 0.15
LTCG_RATE         = 0.10
LTCG_HOLDING_DAYS = 365
LTCG_EXEMPTION    = 100000

# ── BEHAVIORAL BIAS THRESHOLDS ───────────────────────────────────────────────
BIAS = {
    "panic_threshold_minutes": 30,
    "revenge_window_hours": 4,
    "oversize_multiplier": 1.8,
    "disposition_ratio_threshold": 1.5,
    "min_trades_for_ml": 10,
    "kmeans_clusters": 3,
}

# ── DECISION INTELLIGENCE SCORE — sub-component weights (sum = 1.0) ─────────
DIS_WEIGHTS = {
    "exit_discipline": 0.25,
    "entry_quality": 0.20,
    "position_sizing": 0.20,
    "patience_score": 0.20,
    "recovery_score": 0.15,
}

# ── TRADER DNA ────────────────────────────────────────────────────────────────
DNA_DIMENSIONS = ["Precision","Patience","Consistency","Risk Control","Adaptability","Sector Mastery"]
DNA_ARCHETYPES = {
    "Precision Trader": {"min_precision": 65, "min_consistency": 60},
    "Trend Follower":   {"min_patience": 65,  "min_adaptability": 55},
    "Impulsive":        {"max_patience": 35,  "max_consistency": 40},
    "Defensive":        {"min_risk_control": 70, "max_precision": 55},
    "Opportunistic":    {"min_sector_mastery": 70, "min_adaptability": 60},
}

# ── KELLY CRITERION ───────────────────────────────────────────────────────────
KELLY = {
    "max_full_kelly": 0.40,
    "half_kelly_factor": 0.50,
    "min_trades_required": 15,
}

# ── MONTE CARLO SIMULATION PARAMETERS ────────────────────────────────────────
MONTE_CARLO = {
    "simulations": 1000,
    "extension_days": [2, 5, 10, 15, 30],
    "stoploss_levels": [-0.02, -0.05, -0.10],
    "annualization_factor": 252,
    "risk_free_rate": 0.065,
}

# ── PEER BENCHMARKS ───────────────────────────────────────────────────────────
PEER_BENCHMARKS = {
    "win_rate":       {"mu": 48.0, "sigma": 12.0},
    "avg_hold_days":  {"mu": 14.0, "sigma": 20.0},
    "panic_rate":     {"mu": 42.0, "sigma": 15.0},
    "max_drawdown":   {"mu": 28.0, "sigma": 10.0},
    "sharpe_ratio":   {"mu": 0.45, "sigma": 0.60},
    "dis_score":      {"mu": 45.0, "sigma": 15.0},
    "tax_efficiency": {"mu": 35.0, "sigma": 18.0},
}

# ── NSE STOCK → SECTOR MAP ────────────────────────────────────────────────────
NSE_SECTOR_MAP = {
    "HDFCBANK":"Banking","ICICIBANK":"Banking","SBIN":"Banking","KOTAKBANK":"Banking",
    "AXISBANK":"Banking","INDUSINDBK":"Banking","BANDHANBNK":"Banking","FEDERALBNK":"Banking",
    "HDFC":"Finance","BAJFINANCE":"Finance","BAJAJFINSV":"Finance","MUTHOOTFIN":"Finance",
    "TCS":"IT","INFY":"IT","WIPRO":"IT","HCLTECH":"IT","TECHM":"IT","LTIM":"IT",
    "PERSISTENT":"IT","COFORGE":"IT","MPHASIS":"IT","OFSS":"IT",
    "SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma","DIVISLAB":"Pharma",
    "BIOCON":"Pharma","AUROPHARMA":"Pharma","LUPIN":"Pharma","TORNTPHARM":"Pharma",
    "MARUTI":"Auto","TATAMOTORS":"Auto","M&M":"Auto","BAJAJ-AUTO":"Auto",
    "HEROMOTOCO":"Auto","EICHERMOT":"Auto","BOSCHLTD":"Auto",
    "RELIANCE":"Energy","ONGC":"Energy","BPCL":"Energy","IOC":"Energy",
    "HINDPETRO":"Energy","GAIL":"Energy","POWERGRID":"Energy","NTPC":"Energy",
    "HINDUNILVR":"FMCG","ITC":"FMCG","NESTLEIND":"FMCG","BRITANNIA":"FMCG",
    "DABUR":"FMCG","MARICO":"FMCG","GODREJCP":"FMCG","COLPAL":"FMCG",
    "TATASTEEL":"Metals","JSWSTEEL":"Metals","HINDALCO":"Metals","COALINDIA":"Metals",
    "VEDL":"Metals","NMDC":"Metals","SAIL":"Metals",
    "ULTRACEMCO":"Cement","SHREECEM":"Cement","AMBUJACEM":"Cement","ACC":"Cement",
    "LT":"Infrastructure","ADANIPORTS":"Infrastructure","GMRINFRA":"Infrastructure",
    "TITAN":"Consumer","TATACONSUM":"Consumer","DMART":"Consumer","PAGEIND":"Consumer",
    "BHARTIARTL":"Telecom","IDEA":"Telecom",
}

# ── GRADE THRESHOLDS ──────────────────────────────────────────────────────────
GRADE_THRESHOLDS = {"A": 80, "B": 65, "C": 50, "D": 35, "F": 0}

# ── TRADE TAG TAXONOMY ────────────────────────────────────────────────────────
TAG_TAXONOMY = {
    "✅ Clean Win":       "#00C853",
    "💎 Diamond Hold":    "#00BCD4",
    "⚡ Quick Strike":    "#FFEB3B",
    "😨 Panic Exit":      "#FF5252",
    "🔁 Revenge Trade":   "#FF7043",
    "📏 Oversized":       "#FF9800",
    "🎯 Precision Entry": "#69F0AE",
    "📉 Premature Exit":  "#FFA726",
    "🏆 Best Trade":      "#FFD700",
    "💀 Worst Trade":     "#B71C1C",
    "🔄 Recovery Trade":  "#7C4DFF",
}

# ── EFFICIENT FRONTIER ────────────────────────────────────────────────────────
FRONTIER = {
    "min_sectors": 3, "min_trades_per_sector": 3,
    "num_portfolios": 5000, "weight_min": 0.05, "weight_max": 0.60,
}

# ── BAYESIAN WIN RATE ─────────────────────────────────────────────────────────
BAYESIAN = {
    "prior_alpha": 1,
    "prior_beta": 1,
    "credible_interval": 0.95,
    "stability_threshold": 0.05,
}