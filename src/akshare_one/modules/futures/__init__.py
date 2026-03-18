from typing import Any, Literal

import pandas as pd

from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .factory import FuturesHistoricalFactory, FuturesRealtimeFactory
from .sina import SinaFuturesHistorical, SinaFuturesRealtime


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
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FuturesHistoricalFactory.create_router(sources=source)
        df = router.execute("get_historical_data", symbol, start_date, end_date)
    else:
        provider = FuturesHistoricalFactory.get_provider(source=source)
        df = provider.get_historical_data(symbol, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


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
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FuturesRealtimeFactory.create_router(sources=source)
        df = router.execute("get_realtime_data")
    else:
        provider = FuturesRealtimeFactory.get_provider(source=source)
        df = provider.get_realtime_data()

    if symbol:
        df = df[df["symbol"] == symbol]

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_futures_hist_data",
    "get_futures_realtime_data",
    "HistoricalFuturesDataProvider",
    "RealtimeFuturesDataProvider",
    "FuturesHistoricalFactory",
    "FuturesRealtimeFactory",
]
