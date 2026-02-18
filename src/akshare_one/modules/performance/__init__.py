"""
Performance data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import PerformanceFactory


def get_performance_forecast(
    date: str = "20240331",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get performance forecast (业绩预告) data.

    Args:
        date: Report date in YYYYMMDD format (e.g., '20240331')
        source: Data source
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame with columns: symbol, name, indicator, change, forecast_value, etc.
    """
    from akshare_one.client import apply_data_filter

    provider = PerformanceFactory.get_provider(source=source)
    df = provider.get_performance_forecast(date)
    return apply_data_filter(df, columns, row_filter)


def get_performance_express(
    date: str = "20240331",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get performance express (业绩快报) data.

    Args:
        date: Report date in YYYYMMDD format
        source: Data source
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame with columns: symbol, name, eps, revenue, net_profit, etc.
    """
    from akshare_one.client import apply_data_filter

    provider = PerformanceFactory.get_provider(source=source)
    df = provider.get_performance_express(date)
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_performance_forecast", "get_performance_express", "PerformanceFactory"]
