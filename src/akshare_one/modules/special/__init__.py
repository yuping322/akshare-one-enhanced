"""
Special data module for unique market data.

This module provides interfaces to fetch special market data including:
- Chip distribution (筹码分布) - Daily chip distribution analysis
- Broker profit forecast (券商盈利预测) - Broker earnings forecast
- Institutional research (机构调研) - Institutional research records
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import tushare
from .base import SpecialDataFactory


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
    "get_chip_distribution",
    "get_broker_forecast",
    "get_institutional_research",
    "SpecialDataFactory",
]
