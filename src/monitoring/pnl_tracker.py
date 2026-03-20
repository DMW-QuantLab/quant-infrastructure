"""
PnL tracking and Sharpe calculation.
Writes state to Redis. Read by monitor_server.py and monitor.yml.
"""
from __future__ import annotations
import json
import numpy as np
from datetime import datetime, timezone


def sharpe_ratio(returns: np.ndarray, annualisation_factor: float = 365.0) -> float:
    """
    Annualised Sharpe ratio.
    Returns nan if std is zero (single-trade history).
    """
    if len(returns) < 2:
        return float("nan")
    mu  = returns.mean()
    std = returns.std(ddof=1)
    if std == 0:
        return float("nan")
    return float((mu / std) * np.sqrt(annualisation_factor))


def push_heartbeat(redis_client: object, key: str = "rsa_bot:heartbeat") -> None:
    """Write a UTC timestamp to Redis as a liveness signal."""
    ts = datetime.now(timezone.utc).isoformat()
    redis_client.set(key, ts, ex=120)   # Expires in 2 minutes

