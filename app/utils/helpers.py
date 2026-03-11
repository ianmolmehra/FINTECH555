# ============================================================
# helpers.py — Utility functions used across modules
# ============================================================

import pandas as pd
import numpy as np


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divides safely, returning default if denominator is zero."""
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamps a value between min_val and max_val."""
    return max(min_val, min(max_val, value))


def format_inr(value: float) -> str:
    """Formats a number as Indian Rupee string."""
    return f"₹{value:,.0f}"


def pct_str(value: float, decimals: int = 1) -> str:
    """Formats a float as percentage string."""
    return f"{value:.{decimals}f}%"
