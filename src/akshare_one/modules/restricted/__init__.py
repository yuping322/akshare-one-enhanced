"""
Restricted Release (限售解禁) data module for PV.RestrictedRelease.

This module provides interfaces to fetch restricted stock release data including:
- Restricted release data (限售解禁数据) - detailed release information
- Restricted release calendar (解禁日历) - aggregated release schedule
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import RestrictedReleaseFactory


@doc_params
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
    return RestrictedReleaseFactory.call_provider_method(
        "get_restricted_release",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
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
    return RestrictedReleaseFactory.call_provider_method(
        "get_restricted_release_calendar",
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_restricted_release",
    "get_restricted_release_calendar",
    "RestrictedReleaseFactory",
]
