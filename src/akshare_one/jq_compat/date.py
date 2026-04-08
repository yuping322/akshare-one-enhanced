import datetime
from datetime import date, datetime as dt, timedelta
from typing import Union, Literal, Optional, List
import pandas as pd
from ..modules.date import (
    get_all_trade_days as _get_all_trade_days_ak,
    transform_date as _transform_date_ak,
    get_trade_dates_between as _get_trade_dates_between_ak,
    is_trade_date as _is_trade_date_ak,
)

def get_all_trade_days():
    return _get_all_trade_days_ak()

def transform_date(date_input, output_type='date'):
    return _transform_date_ak(date_input, output_type)

def get_shifted_date(
    base_date: Union[str, date, dt, pd.Timestamp],
    days: int,
    days_type: Literal['T', 'D'] = 'T'
) -> date:
    """Shift date by trading days (T) or calendar days (D)."""
    base = transform_date(base_date, 'date')
    if days_type == 'D':
        return base + timedelta(days=days)
    elif days_type == 'T':
        trade_days = get_all_trade_days()
        if not trade_days: return base + timedelta(days=days)
        if base in trade_days: idx = trade_days.index(base)
        else:
            if days > 0:
                idx = -1
                for i, d in enumerate(trade_days):
                    if d > base:
                        idx = i
                        days -= 1
                        break
            else:
                idx = -1
                for i in range(len(trade_days)-1, -1, -1):
                    if trade_days[i] < base:
                        idx = i
                        days += 1
                        break
        if idx != -1:
            new_idx = idx + days
            if 0 <= new_idx < len(trade_days): return trade_days[new_idx]
        raise ValueError("Shifted date out of range")
    raise ValueError(f"Unsupported days_type: {days_type}")

def get_previous_trade_date(base_date: Union[str, date, dt, pd.Timestamp], n: int = 1) -> date:
    return get_shifted_date(base_date, -n, 'T')

def get_next_trade_date(base_date: Union[str, date, dt, pd.Timestamp], n: int = 1) -> date:
    return get_shifted_date(base_date, n, 'T')

def is_trade_date(check_date: Union[str, date, dt, pd.Timestamp]) -> bool:
    return _is_trade_date_ak(check_date)

def get_trade_dates_between(start_date, end_date) -> List[date]:
    return _get_trade_dates_between_ak(start_date, end_date)

def count_trade_dates_between(start_date, end_date) -> int:
    return len(get_trade_dates_between(start_date, end_date))

def clear_trade_days_cache():
    _get_all_trade_days_ak.cache_clear()

__all__ = [
    'get_shifted_date', 'get_previous_trade_date', 'get_next_trade_date',
    'transform_date', 'is_trade_date', 'get_trade_dates_between',
    'count_trade_dates_between', 'clear_trade_days_cache',
]
