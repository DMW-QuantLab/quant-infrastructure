"""
Kelly Criterion — core sizing primitives.
Used by both quant-research (backtesting) and strategy-engines (live).
"""
from __future__ import annotations
import numpy as np


def fractional_kelly(
    p_win: float,
    b_net_odds: float,
    fraction: float = 0.25,
) -> float:
    """
    Fractional Kelly bet size.

    Args:
        p_win:      True win probability
        b_net_odds: Net odds (profit per unit risked) = (1/P_S - 1) for RSA
        fraction:   Kelly multiplier — default 0.25 (quarter-Kelly)
    Returns:
        Optimal fraction of bankroll, floored at 0
    """
    q = 1.0 - p_win
    if b_net_odds <= 0:
        return 0.0
    full_kelly = (p_win * b_net_odds - q) / b_net_odds
    return float(max(0.0, fraction * full_kelly))


def multi_asset_kelly(
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    fraction: float = 0.25,
) -> np.ndarray:
    """
    Multi-asset fractional Kelly: maximise E[log W].
    Returns position sizes as fraction of bankroll.
    Requires: cov matrix invertible, no short positions (floor at 0).
    """
    try:
        cov_inv = np.linalg.inv(covariance_matrix)
    except np.linalg.LinAlgError:
        return np.zeros(len(expected_returns))
    sizes = fraction * cov_inv @ expected_returns
    return np.maximum(sizes, 0.0)

