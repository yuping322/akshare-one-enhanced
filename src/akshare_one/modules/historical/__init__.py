from typing import Any, Literal

import pandas as pd

from .factory import HistoricalDataFactory


def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get historical stock data.

    Args:
        symbol: Stock symbol
        interval: Data interval
        interval_multiplier: Interval multiplier
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        adjust: Adjustment type
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Historical data
    """
    from ...client import apply_data_filter

    params = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }

    if isinstance(source, list) or source is None:
        router = HistoricalDataFactory.create_router(sources=source, **params)
        df = router.execute("get_hist_data")
    else:
        provider = HistoricalDataFactory.get_provider(source=source, **params)
        df = provider.get_hist_data()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_hist_data", "HistoricalDataFactory"]
