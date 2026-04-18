"""
Moving average crossover signal.
"""

import pandas as pd


def compute_ma_cross(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    """Moving Average Crossover signal (1: Golden Cross, -1: Death Cross)."""
    ma_f = close.rolling(fast).mean()
    ma_s = close.rolling(slow).mean()
    diff = ma_f - ma_s
    signal = pd.Series(0, index=close.index)
    signal[(diff > 0) & (diff.shift(1) <= 0)] = 1
    signal[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return signal
