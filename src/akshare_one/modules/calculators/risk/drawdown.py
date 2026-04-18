"""
Drawdown calculations.
"""

import numpy as np
import pandas as pd


def compute_drawdown_series(returns: pd.Series) -> pd.Series:
    """Calculate drawdown series from returns."""
    cum_ret = (1 + returns).cumprod()
    running_max = cum_ret.cummax()
    return (cum_ret - running_max) / running_max


def compute_max_drawdown(returns: pd.Series) -> tuple[float, pd.Timestamp | None, pd.Timestamp | None]:
    """Calculate maximum drawdown and its start/end dates."""
    cum_ret = (1 + returns).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max

    mdd = drawdown.min()
    end_idx = drawdown.idxmin()

    start_idx = cum_ret[:end_idx].idxmax() if end_idx is not None else None

    return mdd, start_idx, end_idx


def compute_recovery_time(returns: pd.Series) -> pd.Series:
    """Calculate days to recover from each drawdown."""
    cum_ret = (1 + returns).cumprod()
    running_max = cum_ret.cummax()
    in_drawdown = cum_ret < running_max

    recovery_days = pd.Series(np.nan, index=returns.index)
    peak_date = None

    for i, (date, is_dd) in enumerate(in_drawdown.items()):
        if is_dd and peak_date is None:
            peak_date = date
        elif not is_dd and peak_date is not None:
            recovery_days[date] = (date - peak_date).days if hasattr(date, "days") else i
            peak_date = None

    return recovery_days
