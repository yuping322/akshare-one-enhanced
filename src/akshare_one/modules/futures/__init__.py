from typing import Any

import pandas as pd

from .factory import FuturesHistoricalFactory, FuturesRealtimeFactory


def get_futures_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get futures historical data.

    Args:
        symbol: Futures symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Historical data
    """
    return FuturesHistoricalFactory.call_provider_method(
        "get_historical_data",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


def get_futures_realtime_data(
    symbol: str | None = None,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get futures realtime quotes.

    Args:
        symbol: Futures symbol (optional)
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Realtime data
    """
    # Create extra row filter if symbol is provided
    if symbol:
        row_filter = row_filter or {}
        if "query" in row_filter:
            row_filter["query"] = f"({row_filter['query']}) and symbol == '{symbol}'"
        else:
            row_filter["query"] = f"symbol == '{symbol}'"

    return FuturesRealtimeFactory.call_provider_method(
        "get_realtime_data",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_futures_hist_data",
    "get_futures_realtime_data",
    "FuturesHistoricalFactory",
    "FuturesRealtimeFactory",
]
