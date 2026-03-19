"""
Disclosure news data module for PV.DisclosureNews.

This module provides interfaces to fetch disclosure and announcement data including:
- General disclosure news
- Dividend data
- Repurchase data
- ST/Delist risk data
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import DisclosureFactory


@doc_params
def get_disclosure_news(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    category: Literal["all", "dividend", "repurchase", "st", "major_event"] = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get disclosure news data.

    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')
    """
    return DisclosureFactory.call_provider_method(
        "get_disclosure_news",
        symbol,
        start_date,
        end_date,
        category,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_dividend_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dividend data.

    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return DisclosureFactory.call_provider_method(
        "get_dividend_data",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_repurchase_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get repurchase data.

    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return DisclosureFactory.call_provider_method(
        "get_repurchase_data",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_disclosure_news",
    "get_dividend_data",
    "get_repurchase_data",
    "DisclosureFactory",
]
