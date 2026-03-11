# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/utils/bootstrap.py
# Purpose: Bootstrap Confidence Interval utilities used across multiple modules.
#          Bootstrap CI: non-parametric method to estimate uncertainty around
#          any statistic without assuming a normal distribution.
# =============================================================================

import numpy as np
from typing import Tuple, Callable


def bootstrap_ci(data: np.ndarray,
                 statistic: Callable = np.mean,
                 n_bootstraps: int = 1000,
                 confidence: float = 0.95,
                 random_seed: int = 42) -> Tuple[float, float, float]:
    """
    Compute Bootstrap Confidence Interval for any statistic.

    Concept: Bootstrap resampling — draw N samples WITH replacement from the
    data, compute the statistic on each resample, then take the percentile
    bounds of the resulting distribution as the confidence interval.

    Formula: CI = [percentile(bootstrap_stats, (1-α)/2 * 100),
                   percentile(bootstrap_stats, (1+α)/2 * 100)]

    This is the Central Limit Theorem application — the bootstrap distribution
    approximates the sampling distribution of the statistic.

    Args:
        data:         1D array of observed values (e.g., PnL per trade)
        statistic:    Function to compute on each bootstrap sample (default: mean)
        n_bootstraps: Number of resampling iterations (1000 = standard practice)
        confidence:   CI level (0.95 = 95% confidence interval, industry standard)
        random_seed:  For reproducibility — same seed = same bootstrap samples

    Returns:
        Tuple of (point_estimate, lower_bound, upper_bound)
    """
    np.random.seed(random_seed)  # Seed for reproducible bootstrap samples
    n = len(data)

    if n == 0:
        return 0.0, 0.0, 0.0  # Guard: empty data returns zeros

    # ── Compute the point estimate (observed statistic on full data)
    point_estimate = statistic(data)  # e.g., mean win rate on actual trades

    # ── Bootstrap resampling loop: draw n_bootstraps samples with replacement
    bootstrap_stats = np.zeros(n_bootstraps)
    for i in range(n_bootstraps):
        # Resample WITH replacement — this is the key bootstrap operation
        # np.random.choice with replace=True simulates drawing new datasets
        resample = np.random.choice(data, size=n, replace=True)
        # Compute the statistic on each resample (e.g., mean of resampled PnL)
        bootstrap_stats[i] = statistic(resample)

    # ── Percentile method for CI bounds — no normality assumption needed
    alpha = 1.0 - confidence  # e.g., alpha = 0.05 for 95% CI
    lower = np.percentile(bootstrap_stats, alpha / 2 * 100)   # 2.5th percentile
    upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)  # 97.5th percentile

    return float(point_estimate), float(lower), float(upper)


def bootstrap_win_rate_ci(wins: int, total: int,
                          n_bootstraps: int = 1000,
                          confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Bootstrap CI specifically for win rate (Bernoulli data: 0s and 1s).

    Concept: Win rate is a proportion p = wins/total. Bootstrap treats each
    trade as a Bernoulli trial (1=win, 0=loss) and resamples the outcome array.

    Args:
        wins:   Number of winning trades.
        total:  Total number of trades.
        confidence: CI level (default 0.95).

    Returns:
        Tuple of (win_rate, lower_bound, upper_bound) as percentages.
    """
    if total == 0:
        return 0.0, 0.0, 0.0

    # ── Create binary outcome array: 1 for each win, 0 for each loss
    outcomes = np.array([1] * wins + [0] * (total - wins))  # Bernoulli outcomes

    # ── Bootstrap CI on the mean (mean of 0/1 array = win rate)
    point_est, lower, upper = bootstrap_ci(
        outcomes, statistic=np.mean, n_bootstraps=n_bootstraps, confidence=confidence
    )

    # ── Convert from decimal fraction to percentage
    return point_est * 100, lower * 100, upper * 100


def bootstrap_sharpe_ci(pnl_array: np.ndarray,
                        risk_free_rate: float = 0.0,
                        n_bootstraps: int = 1000,
                        confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Bootstrap CI for Sharpe Ratio.

    Sharpe Ratio Formula: SR = (E[R] - Rf) / σ(R) * sqrt(252)
    Bootstrap CI handles the non-normality of trade PnL distributions.

    Args:
        pnl_array: 1D array of per-trade PnL values.
        risk_free_rate: Daily risk-free rate (default 0 for simplicity).
        n_bootstraps: Resampling iterations.
        confidence: CI level.

    Returns:
        Tuple of (sharpe, lower_bound, upper_bound).
    """
    def sharpe_statistic(arr: np.ndarray) -> float:
        """Compute annualized Sharpe Ratio for a PnL array."""
        std = np.std(arr)
        if std == 0:
            return 0.0
        # Sharpe Ratio: annualized = (mean_return - rf) / std * sqrt(252)
        return (np.mean(arr) - risk_free_rate) / std * np.sqrt(252)

    return bootstrap_ci(pnl_array, statistic=sharpe_statistic,
                        n_bootstraps=n_bootstraps, confidence=confidence)
