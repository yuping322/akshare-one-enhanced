"""
Limit Up/Down (涨停池) data module for PV.LimitUpDown.

This module provides interfaces to fetch limit up/down data including:
- Limit up pool (涨停池)
- Limit down pool (跌停池)
- Limit up/down statistics
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import LimitUpDownFactory


@doc_params
def get_limit_up_pool(
    date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit up pool data.

    Args:
        date: Date in YYYY-MM-DD format
    """
    return LimitUpDownFactory.call_provider_method(
        "get_limit_up_pool",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_limit_down_pool(
    date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit down pool data.

    Args:
        date: Date in YYYY-MM-DD format
    """
    return LimitUpDownFactory.call_provider_method(
        "get_limit_down_pool",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_limit_up_stats(
    start_date: str,
    end_date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit up/down statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return LimitUpDownFactory.call_provider_method(
        "get_limit_up_stats",
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_limit_up_pool",
    "get_limit_down_pool",
    "get_limit_up_stats",
    "LimitUpDownFactory",
]
