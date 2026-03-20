"""
Unit tests for Kelly sizing primitives.
"""
import numpy as np
import pytest
from src.risk.kelly import fractional_kelly


def test_kelly_positive_ev():
    # p=0.6, b=1.0 (evens bet) → full Kelly = 0.2
    fk = fractional_kelly(p_win=0.6, b_net_odds=1.0, fraction=1.0)
    assert abs(fk - 0.2) < 1e-6


def test_fractional_kelly_quarter():
    fk = fractional_kelly(p_win=0.6, b_net_odds=1.0, fraction=0.25)
    assert abs(fk - 0.05) < 1e-6


def test_kelly_zero_on_negative_ev():
    fk = fractional_kelly(p_win=0.4, b_net_odds=1.0, fraction=0.25)
    assert fk == 0.0


def test_kelly_zero_on_bad_odds():
    fk = fractional_kelly(p_win=0.9, b_net_odds=0.0, fraction=0.25)
    assert fk == 0.0

