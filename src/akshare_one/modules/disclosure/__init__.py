"""
Disclosure (公告披露) data module for PV.Disclosure.

This module provides interfaces to fetch corporate disclosure data including:
- Corporate announcements and news
- Dividend and distribution data
- Stock repurchase data
- ST/Delist risk warnings
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, efinance, lixinger, sina, tushare
from .base import DisclosureFactory


@api_endpoint(DisclosureFactory)
def get_disclosure_news(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    category: str = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get disclosure news data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        category: Disclosure category ('all', 'dividend', 'repurchase', 'st', 'major_event')
    """
    pass


@api_endpoint(DisclosureFactory)
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
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(DisclosureFactory)
def get_repurchase_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock repurchase data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(DisclosureFactory)
def get_st_delist_data(
    symbol: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ST/delist risk data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
    """
    pass


@api_endpoint(DisclosureFactory)
def get_forecast_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "tushare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance forecast data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(DisclosureFactory)
def get_express_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "tushare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance express (quick report) data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(DisclosureFactory)
def get_all_report_dates(
    source: SourceType = "efinance",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get all financial report dates.

    Returns list of dates for quarterly/annual financial reports.
    """
    pass


__all__ = [
    "get_disclosure_news",
    "get_dividend_data",
    "get_repurchase_data",
    "get_st_delist_data",
    "get_forecast_data",
    "get_express_data",
    "get_all_report_dates",
    "DisclosureFactory",
]
