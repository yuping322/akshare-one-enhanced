"""
src/akshare_one/modules/alpha/signals.py
Market timing and stock selection signals.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Union, List, Optional, Dict
from ..historical import get_hist_data

def compute_rsrs(high: pd.Series, low: pd.Series, n: int = 18, m: int = 600) -> pd.Series:
    """Calculate RSRS (Resistance Support Relative Strength) signal."""
    beta_series = pd.Series(index=high.index, data=np.nan)
    for i in range(n, len(high)):
        h_win = high.iloc[i-n+1:i+1]
        l_win = low.iloc[i-n+1:i+1]
        x = sm.add_constant(l_win.values)
        y = h_win.values
        res = sm.OLS(y, x).fit()
        beta_series.iloc[i] = res.params[1]
    
    beta_mean = beta_series.rolling(window=m).mean()
    beta_std = beta_series.rolling(window=m).std()
    z_score = (beta_series - beta_mean) / beta_std
    return beta_series * z_score

def compute_ma_cross(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    """Moving Average Crossover signal (1: Golden Cross, -1: Death Cross)."""
    ma_f = close.rolling(fast).mean()
    ma_s = close.rolling(slow).mean()
    diff = ma_f - ma_s
    signal = pd.Series(0, index=close.index)
    signal[(diff > 0) & (diff.shift(1) <= 0)] = 1
    signal[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return signal

def compute_breakthrough(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
    """Price Breakthrough signal (1: Breakout Up, -1: Breakout Down)."""
    h_max = high.shift(1).rolling(window).max()
    l_min = low.shift(1).rolling(window).min()
    signal = pd.Series(0, index=close.index)
    signal[close > h_max] = 1
    signal[close < l_min] = -1
    return signal

def get_signal_for_sec(symbol: str, signal_type: str = "rsrs", end_date: Optional[str] = None, **kwargs) -> int:
    """Get the latest signal for a security."""
    df = get_hist_data(symbol, end_date=end_date, count= kwargs.get('lookback', 1000))
    if df.empty: return 0
    
    if signal_type == "rsrs":
        res = compute_rsrs(df['high'], df['low'], n=kwargs.get('n', 18), m=kwargs.get('m', 600))
        val = res.iloc[-1]
        if val > 0.8: return 1
        if val < -0.8: return -1
    elif signal_type == "ma_cross":
        res = compute_ma_cross(df['close'])
        return int(res.iloc[-1])
    elif signal_type == "breakout":
        res = compute_breakthrough(df['high'], df['low'], df['close'])
        return int(res.iloc[-1])
    return 0

__all__ = ["compute_rsrs", "compute_ma_cross", "compute_breakthrough", "get_signal_for_sec"]
