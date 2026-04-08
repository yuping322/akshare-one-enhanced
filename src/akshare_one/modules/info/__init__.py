"""
Stock basic information module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, efinance, sina, tushare
from .base import InfoDataFactory


@api_endpoint(InfoDataFactory)
def get_basic_info(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get basic information for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(InfoDataFactory)
def get_stock_info(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock basic information (alias for get_basic_info).

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(InfoDataFactory)
def get_quote_snapshot(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock quote snapshot.

    Args:
        symbol: Stock symbol
    """
    pass


__all__ = ["get_basic_info", "get_stock_info", "get_quote_snapshot", "InfoDataFactory"]


@api_endpoint(InfoDataFactory)
def get_daily_basic(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get daily basic indicators (PE, PB, turnover rate, etc.).

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(InfoDataFactory)
def get_suspend_data(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get suspension/resumption data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(InfoDataFactory)
def get_stk_limit(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get daily limit up/down prices.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(InfoDataFactory)
def get_adj_factor(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get adjustment factor data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_basic_info",
    "get_stock_info",
    "get_quote_snapshot",
    "get_daily_basic",
    "get_suspend_data",
    "get_stk_limit",
    "get_adj_factor",
    "InfoDataFactory",
]
