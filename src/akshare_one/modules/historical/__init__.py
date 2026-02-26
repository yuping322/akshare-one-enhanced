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
    source: Literal["eastmoney", "eastmoney_direct", "sina", "tencent", "netease"] = "eastmoney_direct",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = HistoricalDataFactory.get_provider(
        source,
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    df = provider.get_hist_data()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = ["get_hist_data", "HistoricalDataFactory"]
