"""
src/akshare_one/modules/alpha/factors.py
Factor calculation implementations.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Optional, Dict
from .base import global_factor_registry, safe_divide, align_to_trade_days
from ..historical import get_hist_data
from ..valuation import get_stock_valuation

def compute_market_cap(symbol: str, end_date: Optional[str] = None, count: int = 1, **kwargs) -> Union[float, pd.Series]:
    """Total Market Cap factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or 'market_cap' not in df.columns: return np.nan
    res = df.tail(count)['market_cap']
    return res.iloc[0] if count == 1 else res

def compute_pb_ratio(symbol: str, end_date: Optional[str] = None, count: int = 1, **kwargs) -> Union[float, pd.Series]:
    """PB Ratio factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or 'pb' not in df.columns: return np.nan
    res = df.tail(count)['pb']
    return res.iloc[0] if count == 1 else res

def compute_pe_ratio(symbol: str, end_date: Optional[str] = None, count: int = 1, **kwargs) -> Union[float, pd.Series]:
    """PE Ratio factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or 'pe' not in df.columns: return np.nan
    res = df.tail(count)['pe']
    return res.iloc[0] if count == 1 else res

def compute_momentum(symbol: str, end_date: Optional[str] = None, window: int = 20, **kwargs) -> float:
    """Price Momentum factor."""
    df = get_hist_data(symbol, end_date=end_date, count=window + 1)
    if len(df) < window: return np.nan
    return (df['close'].iloc[-1] / df['close'].iloc[0]) - 1

def compute_volatility(symbol: str, end_date: Optional[str] = None, window: int = 20, **kwargs) -> float:
    """Price Volatility factor."""
    df = get_hist_data(symbol, end_date=end_date, count=window)
    if len(df) < window: return np.nan
    return df['close'].pct_change().std() * np.sqrt(252)

# Registration
global_factor_registry.register("market_cap", compute_market_cap, description="Total Market Cap")
global_factor_registry.register("pb_ratio", compute_pb_ratio, description="Price to Book Ratio")
global_factor_registry.register("pe_ratio", compute_pe_ratio, description="Price to Earnings Ratio")
global_factor_registry.register("momentum", compute_momentum, window=20, description="N-day Price Momentum")
global_factor_registry.register("volatility", compute_volatility, window=20, description="Annualized Volatility")

def get_factor_values(securities: List[str], factor_names: List[str], end_date: str, count: int = 1) -> pd.DataFrame:
    """Calculate multiple factors for a list of securities."""
    results = {}
    for sec in securities:
        sec_results = {}
        for name in factor_names:
            func = global_factor_registry.get(name)
            if func:
                try:
                    val = func(sec, end_date=end_date, count=count)
                    sec_results[name] = val
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Factor '{name}' calculation failed for '{sec}': {e}")
                    sec_results[name] = np.nan
        results[sec] = sec_results
    return pd.DataFrame(results).T

__all__ = ["compute_market_cap", "compute_pb_ratio", "compute_momentum", "get_factor_values"]
