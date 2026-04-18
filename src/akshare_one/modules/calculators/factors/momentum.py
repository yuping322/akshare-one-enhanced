"""
Momentum factor calculations.
"""

import numpy as np
import pandas as pd

from .base import global_factor_registry
from ...providers.equities.quotes.historical import get_hist_data


def compute_momentum(symbol: str, end_date: str | None = None, window: int = 20, **kwargs) -> float:
    """Price Momentum factor."""
    df = get_hist_data(symbol, end_date=end_date, count=window + 1)
    if len(df) < window:
        return np.nan
    return (df["close"].iloc[-1] / df["close"].iloc[0]) - 1


global_factor_registry.register("momentum", compute_momentum, window=20, description="N-day Price Momentum")
