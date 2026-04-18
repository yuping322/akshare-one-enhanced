"""
Volatility and ATR risk calculations.
"""

import numpy as np
import pandas as pd


def compute_annual_volatility(returns: pd.Series, window: int = 252) -> float:
    """Calculate annualized volatility."""
    return returns.std() * np.sqrt(window)


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def detect_volatility_regime(
    returns: pd.Series, window: int = 60, high_threshold: float = 0.3, low_threshold: float = 0.15
) -> pd.Series:
    """Detect volatility regime (high/normal/low)."""
    rolling_vol = returns.rolling(window).std() * np.sqrt(252)
    regime = pd.Series("normal", index=returns.index)
    regime[rolling_vol > high_threshold] = "high"
    regime[rolling_vol < low_threshold] = "low"
    return regime
