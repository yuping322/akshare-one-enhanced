from typing import Any, Literal

import pandas as pd

from .factory import InsiderDataFactory


def get_inner_trade_data(
    symbol: str,
    source: Literal["xueqiu", "eastmoney"] = "xueqiu",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = InsiderDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_inner_trade_data()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = ["get_inner_trade_data", "InsiderDataFactory"]
