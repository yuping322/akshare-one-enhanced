"""
Restricted stock release (限售解禁) data module for PV.Restricted.

This module provides interfaces to fetch restricted stock release data including:
- Restricted release details (date, quantity, ratio, holder type)
- Restricted release calendar (aggregated schedule by date)
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import RestrictedReleaseFactory
from . import eastmoney, sina


@api_endpoint(RestrictedReleaseFactory)
def get_restricted_release(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get restricted stock release data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(RestrictedReleaseFactory)
def get_restricted_release_calendar(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get restricted stock release calendar.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_restricted_release",
    "get_restricted_release_calendar",
    "RestrictedReleaseFactory",
]
