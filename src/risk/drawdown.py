"""
Drawdown monitoring and circuit breaker.
"""
from __future__ import annotations
import numpy as np


def rolling_max_drawdown(equity_curve: np.ndarray) -> float:
    """Maximum drawdown over an equity curve."""
    peak = np.maximum.accumulate(equity_curve)
    dd = (equity_curve - peak) / np.maximum(peak, 1e-9)
    return float(dd.min())


def current_drawdown(equity_curve: np.ndarray) -> float:
    """Drawdown from the most recent peak."""
    peak = equity_curve.max()
    current = equity_curve[-1]
    return float((current - peak) / max(peak, 1e-9))

