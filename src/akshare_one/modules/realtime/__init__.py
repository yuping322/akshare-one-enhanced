from typing import Any, Literal

import pandas as pd

from .factory import RealtimeDataFactory


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney_direct",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
    df = provider.get_current_data()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = ["get_realtime_data", "RealtimeDataFactory"]
