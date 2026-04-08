"""
src/akshare_one/modules/date/
Core date and trade calendar utilities.
"""

import datetime
from datetime import date, timedelta
from datetime import datetime as dt
from functools import lru_cache
from typing import List, Literal, Optional, Union

import akshare as ak
import pandas as pd


@lru_cache(maxsize=1)
def get_all_trade_days():
    """Get all trade days from AkShare."""
    try:
        df = ak.tool_trade_date_hist_sina()
        if df is not None and not df.empty:
            return sorted([pd.to_datetime(d).date() for d in df['trade_date']])
    except Exception:
        pass
    return []

def transform_date(
    date_input: str | date | dt | pd.Timestamp,
    output_type: Literal['date', 'datetime', 'str', 'timestamp'] = 'date'
) -> date | dt | str | pd.Timestamp:
    """Convert various date formats."""
    result_date = None
    if isinstance(date_input, date) and not isinstance(date_input, dt):
        result_date = date_input
    elif isinstance(date_input, dt) or isinstance(date_input, pd.Timestamp):
        result_date = date_input.date()
    elif isinstance(date_input, str):
        date_str = date_input.strip()
        try:
            if '-' in date_str: result_date = dt.strptime(date_str, '%Y-%m-%d').date()
            elif len(date_str) == 8: result_date = dt.strptime(date_str, '%Y%m%d').date()
            else: result_date = pd.to_datetime(date_str).date()
        except ValueError as e:
            raise ValueError(f"Could not parse date string: '{date_input}'") from e
    else:
        raise ValueError(f"Unsupported date type: {type(date_input)}")

    if output_type == 'date': return result_date
    elif output_type == 'datetime': return dt.combine(result_date, dt.min.time())
    elif output_type == 'str': return result_date.strftime('%Y-%m-%d')
    elif output_type == 'timestamp': return pd.Timestamp(result_date)
    return result_date

def get_trade_dates_between(
    start_date: str | date | dt | pd.Timestamp,
    end_date: str | date | dt | pd.Timestamp
) -> list[date]:
    start = transform_date(start_date, 'date')
    end = transform_date(end_date, 'date')
    trade_days = get_all_trade_days()
    return [d for d in trade_days if start <= d <= end]

def is_trade_date(check_date: str | date | dt | pd.Timestamp) -> bool:
    d = transform_date(check_date, 'date')
    return d in get_all_trade_days()

__all__ = ["get_all_trade_days", "transform_date", "get_trade_dates_between", "is_trade_date"]
