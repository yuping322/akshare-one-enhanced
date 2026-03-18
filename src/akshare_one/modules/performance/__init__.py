"""
Performance data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import PerformanceFactory


def get_performance_forecast(
    date: str = "20240331",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get performance forecast (业绩预告) data.

    Args:
        date: Report date in YYYYMMDD format (e.g., '20240331')
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Performance forecast data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = PerformanceFactory.create_router(sources=source)
        df = router.execute("get_performance_forecast", date)
    else:
        provider = PerformanceFactory.get_provider(source=source)
        df = provider.get_performance_forecast(date)

    return apply_data_filter(df, columns, row_filter)


def get_performance_express(
    date: str = "20240331",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get performance express (业绩快报) data.

    Args:
        date: Report date in YYYYMMDD format
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Performance express data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = PerformanceFactory.create_router(sources=source)
        df = router.execute("get_performance_express", date)
    else:
        provider = PerformanceFactory.get_provider(source=source)
        df = provider.get_performance_express(date)

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_performance_forecast", "get_performance_express", "PerformanceFactory"]
