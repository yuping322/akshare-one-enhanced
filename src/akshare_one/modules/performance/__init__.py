"""
Performance data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import baostock, eastmoney, efinance, lixinger
from .base import PerformanceFactory


@api_endpoint(PerformanceFactory)
def get_performance_forecast(
    date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance forecast data.

    Args:
        date: Report date (e.g., '20231231')
    """
    pass


@api_endpoint(PerformanceFactory)
def get_performance_express(
    date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance express data.

    Args:
        date: Report date (e.g., '20231231')
    """
    pass


@api_endpoint(PerformanceFactory, method_name="get_forecast_report")
def get_forecast_report(
    symbol: str,
    start_date: str,
    end_date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance forecast report data for a specific stock.

    Args:
        symbol: Stock symbol (e.g., '600000', '000001')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(PerformanceFactory, method_name="get_performance_express_report")
def get_performance_express_report(
    symbol: str,
    start_date: str,
    end_date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance express report data for a specific stock.

    Args:
        symbol: Stock symbol (e.g., '600000', '000001')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(PerformanceFactory)
def get_all_company_performance(
    date: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get all company performance data for a specific date.

    Args:
        date: Report date (e.g., '20231231', '2023-12-31')
    """
    pass


__all__ = [
    "get_performance_forecast",
    "get_performance_express",
    "get_forecast_report",
    "get_performance_express_report",
    "get_all_company_performance",
    "PerformanceFactory",
]
