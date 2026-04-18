"""
Price breakout signal.
"""

import pandas as pd

from ...providers.equities.quotes.historical import get_hist_data
from .rsrs import compute_rsrs
from .crossover import compute_ma_cross


def compute_breakthrough(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
    """Price Breakthrough signal (1: Breakout Up, -1: Breakout Down)."""
    h_max = high.shift(1).rolling(window).max()
    l_min = low.shift(1).rolling(window).min()
    signal = pd.Series(0, index=close.index)
    signal[close > h_max] = 1
    signal[close < l_min] = -1
    return signal


def get_signal_for_sec(symbol: str, signal_type: str = "rsrs", end_date: str | None = None, **kwargs) -> int:
    """Get the latest signal for a security."""
    df = get_hist_data(symbol, end_date=end_date, count=kwargs.get("lookback", 1000))
    if df.empty:
        return 0

    if signal_type == "rsrs":
        res = compute_rsrs(df["high"], df["low"], n=kwargs.get("n", 18), m=kwargs.get("m", 600))
        val = res.iloc[-1]
        if val > 0.8:
            return 1
        if val < -0.8:
            return -1
    elif signal_type == "ma_cross":
        res = compute_ma_cross(df["close"])
        return int(res.iloc[-1])
    elif signal_type == "breakout":
        res = compute_breakthrough(df["high"], df["low"], df["close"])
        return int(res.iloc[-1])
    return 0
