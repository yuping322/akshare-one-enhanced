"""
Shareholder data module for PV.Shareholder.

This module provides interfaces to fetch shareholder-related data including:
- Shareholder changes (增减持)
- Top shareholders (十大股东/十大流通股东)
- Institution holdings (机构持股)
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney, efinance, lixinger, tushare
from .base import ShareholderFactory


@api_endpoint(ShareholderFactory)
def get_shareholder_changes(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get shareholder changes (增减持) data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(ShareholderFactory)
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
    pass


@api_endpoint(ShareholderFactory)
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
    pass


@api_endpoint(ShareholderFactory)
def get_top10_shareholders(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get top 10 shareholders of a stock.

    Args:
        symbol: Stock symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(ShareholderFactory)
def get_top10_float_shareholders(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get top 10 float shareholders of a stock.

    Args:
        symbol: Stock symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(ShareholderFactory)
def get_fund_shareholders(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund shareholders of a stock.

    Args:
        symbol: Stock symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(ShareholderFactory)
def get_top10_stock_holder_info(
    stock_code: str,
    top: int = 10,
    source: SourceType = "efinance",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get top 10 stock holder information.

    Args:
        stock_code: Stock code (e.g., '600000')
        top: Number of top holders to return
    """
    pass


@api_endpoint(ShareholderFactory)
def get_latest_holder_number(
    date: str,
    source: SourceType = "efinance",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get latest holder number for all stocks.

    Args:
        date: Date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_shareholder_changes",
    "get_top_shareholders",
    "get_institution_holdings",
    "get_top10_shareholders",
    "get_top10_float_shareholders",
    "get_fund_shareholders",
    "get_top10_stock_holder_info",
    "get_latest_holder_number",
    "ShareholderFactory",
]
