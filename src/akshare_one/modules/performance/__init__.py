"""
Performance data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import PerformanceFactory


@doc_params
def get_performance_forecast(
    date: str = "20240331",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance forecast (业绩预告) data.

    Args:
        date: Report date in YYYYMMDD format (e.g., '20240331')
    """
    return PerformanceFactory.call_provider_method(
        "get_performance_forecast",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_performance_express(
    date: str = "20240331",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get performance express (业绩快报) data.

    Args:
        date: Report date in YYYYMMDD format
    """
    return PerformanceFactory.call_provider_method(
        "get_performance_express",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_performance_forecast", "get_performance_express", "PerformanceFactory"]
