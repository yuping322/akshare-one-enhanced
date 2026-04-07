"""
ETF (交易型开放式指数基金) data module for PV.ETF.

This module provides interfaces to fetch ETF data including:
- ETF historical price data
- ETF realtime quotes (spot)
- ETF listings by category
- Fund manager information
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import ETFFactory
from . import eastmoney, sina


@api_endpoint(ETFFactory)
def get_etf_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: str = "daily",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ETF historical data.

    Args:
        symbol: ETF symbol (e.g., '510050')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('daily', 'weekly', 'monthly')
    """
    pass


@api_endpoint(ETFFactory)
def get_etf_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: str = "daily",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(ETFFactory)
def get_etf_spot(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get all ETF realtime quotes.
    """
    pass


@api_endpoint(ETFFactory)
def get_etf_realtime_data(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(ETFFactory)
def get_etf_list(
    category: str = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ETF list.

    Args:
        category: ETF category ('all', 'equity', 'bond', 'commodity', 'cross_border')
    """
    pass


@api_endpoint(ETFFactory)
def get_fund_manager(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund manager information.
    """
    pass


@api_endpoint(ETFFactory)
def get_fund_manager_info(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(ETFFactory)
def get_fund_rating_data(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


__all__ = [
    "get_etf_hist",
    "get_etf_hist_data",
    "get_etf_spot",
    "get_etf_realtime_data",
    "get_etf_list",
    "get_fund_manager",
    "get_fund_manager_info",
    "get_fund_rating_data",
    "ETFFactory",
]
