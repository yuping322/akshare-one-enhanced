from typing import Any, Literal

import pandas as pd

from .factory import NewsDataFactory


def get_news_data(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = NewsDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_news_data()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = ["get_news_data", "NewsDataFactory"]
