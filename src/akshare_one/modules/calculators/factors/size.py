"""
Size factor calculations (Market Cap).
"""

import numpy as np
import pandas as pd

from .base import global_factor_registry
from ...providers.equities.fundamentals.valuation import get_stock_valuation


def compute_market_cap(symbol: str, end_date: str | None = None, count: int = 1, **kwargs) -> float | pd.Series:
    """Total Market Cap factor."""
    df = get_stock_valuation(symbol, end_date=end_date)
    if df.empty or "market_cap" not in df.columns:
        return np.nan
    res = df.tail(count)["market_cap"]
    return res.iloc[0] if count == 1 else res


global_factor_registry.register("market_cap", compute_market_cap, description="Total Market Cap")
