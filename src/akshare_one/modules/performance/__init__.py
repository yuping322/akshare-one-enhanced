"""
Performance data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, lixinger
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


__all__ = ["get_performance_forecast", "get_performance_express", "PerformanceFactory"]
