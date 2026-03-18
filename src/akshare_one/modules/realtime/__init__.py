from typing import Any, Literal

import pandas as pd

from .factory import RealtimeDataFactory


def get_realtime_data(
    symbol: str | None = None,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get realtime stock data.

    Args:
        symbol: Stock symbol
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Realtime data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = RealtimeDataFactory.create_router(sources=source, symbol=symbol)
        df = router.execute("get_current_data")
    else:
        provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
        df = provider.get_current_data()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_realtime_data", "RealtimeDataFactory"]
