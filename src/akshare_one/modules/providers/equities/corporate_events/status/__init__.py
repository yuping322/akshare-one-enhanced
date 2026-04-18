"""
Combined status module for ST, suspended, and special stocks.

This module provides interfaces to fetch:
- ST (Special Treatment) stocks
- Suspended/halted stocks
- Special market data (chip distribution, broker forecast, institutional research)
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney_st, eastmoney_suspended, tushare_special
from .st import STFactory
from .suspended import SuspendedFactory
from .special import SpecialDataFactory


@api_endpoint(STFactory)
def get_st_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ST (Special Treatment) stocks.
    """
    pass


@api_endpoint(SuspendedFactory)
def get_suspended_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get suspended/halted stocks.
    """
    pass


@api_endpoint(SpecialDataFactory)
def get_chip_distribution(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "tushare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get chip distribution data (筹码分布).

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(SpecialDataFactory)
def get_broker_forecast(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "tushare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get broker profit forecast data (券商盈利预测).

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(SpecialDataFactory)
def get_institutional_research(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "tushare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get institutional research data (机构调研).

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_st_stocks",
    "get_suspended_stocks",
    "get_chip_distribution",
    "get_broker_forecast",
    "get_institutional_research",
    "STFactory",
    "SuspendedFactory",
    "SpecialDataFactory",
]
