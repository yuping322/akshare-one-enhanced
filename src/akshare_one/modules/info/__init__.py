from typing import Any, Literal

import pandas as pd

from .factory import InfoDataFactory


def get_basic_info(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = InfoDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_basic_info()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = ["get_basic_info", "InfoDataFactory"]
