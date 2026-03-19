"""
Shareholder data module.

This module provides interfaces to fetch shareholder data including:
- Shareholder changes (增减持)
- Top shareholders
- Institution holdings
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import ShareholderFactory


@doc_params
def get_shareholder_changes(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "sse",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get shareholder changes (增减持) data.

    Args:
        symbol: Stock symbol (optional, if None returns all)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return ShareholderFactory.call_provider_method(
        "get_shareholder_changes",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_top_shareholders(
    symbol: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get top shareholders of a stock.

    Args:
        symbol: Stock symbol
    """
    return ShareholderFactory.call_provider_method(
        "get_top_shareholders",
        symbol,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_institution_holdings(
    symbol: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get institution holdings of a stock.

    Args:
        symbol: Stock symbol
    """
    return ShareholderFactory.call_provider_method(
        "get_institution_holdings",
        symbol,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_shareholder_changes",
    "get_top_shareholders",
    "get_institution_holdings",
    "ShareholderFactory",
]
