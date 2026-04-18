"""
Value factor calculations (PE/PB ratios).
"""

import numpy as np
import pandas as pd

from .base import global_factor_registry
from ...providers.equities.fundamentals.valuation import get_stock_valuation


def compute_pb_ratio(symbol: str, end_date: str | None = None, count: int = 1, **kwargs) -> float | pd.Series:
    """PB Ratio factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or "pb" not in df.columns:
        return np.nan
    res = df.tail(count)["pb"]
    return res.iloc[0] if count == 1 else res


def compute_pe_ratio(symbol: str, end_date: str | None = None, count: int = 1, **kwargs) -> float | pd.Series:
    """PE Ratio factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or "pe" not in df.columns:
        return np.nan
    res = df.tail(count)["pe"]
    return res.iloc[0] if count == 1 else res


global_factor_registry.register("pb_ratio", compute_pb_ratio, description="Price to Book Ratio")
global_factor_registry.register("pe_ratio", compute_pe_ratio, description="Price to Earnings Ratio")
