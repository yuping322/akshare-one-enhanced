"""
Trading calendar alignment.
"""

import pandas as pd

from ...core.calendar import get_trade_dates_between


def filter_trade_days(dates: list[str] | pd.DatetimeIndex) -> list[str]:
    """Filter dates to only include trade days."""
    if not dates:
        return []
    start = min(dates)
    end = max(dates)
    if isinstance(start, pd.Timestamp):
        start = start.strftime("%Y-%m-%d")
    if isinstance(end, pd.Timestamp):
        end = end.strftime("%Y-%m-%d")
    trade_days = get_trade_dates_between(start, end)
    if isinstance(dates, pd.DatetimeIndex):
        date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    else:
        date_strs = list(dates)
    return [d for d in trade_days if d in date_strs]


def align_to_calendar(df: pd.DataFrame, date_col: str = "date", fill_method: str = "ffill") -> pd.DataFrame:
    """Align DataFrame to trade calendar."""
    if df is None or df.empty:
        return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
    s_date = df[date_col].min()
    e_date = df[date_col].max()
    trade_days = get_trade_dates_between(s_date, e_date)
    df = df.set_index(date_col).reindex(trade_days)
    if fill_method == "ffill":
        df = df.ffill()
    elif fill_method == "bfill":
        df = df.bfill()
    return df.reset_index().rename(columns={"index": date_col})
