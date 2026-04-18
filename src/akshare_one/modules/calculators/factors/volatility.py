"""
Volatility factor calculations.
"""

import numpy as np
import pandas as pd

from .base import global_factor_registry
from ...providers.equities.quotes.historical import get_hist_data


def compute_volatility(symbol: str, end_date: str | None = None, window: int = 20, **kwargs) -> float:
    """Annualized Price Volatility factor."""
    df = get_hist_data(symbol, end_date=end_date, count=window)
    if len(df) < window:
        return np.nan
    return df["close"].pct_change().std() * np.sqrt(252)


global_factor_registry.register("volatility", compute_volatility, window=20, description="Annualized Volatility")
