"""
Hong Kong and US stock data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import HKUSFactory


def get_hk_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get Hong Kong stock list.

    Returns:
        pd.DataFrame: HK stocks with symbol, name, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = HKUSFactory.get_provider(source=source)
    df = provider.get_hk_stocks()
    return apply_data_filter(df, columns, row_filter)


def get_us_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get US stock list.

    Returns:
        pd.DataFrame: US stocks with symbol, name, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = HKUSFactory.get_provider(source=source)
    df = provider.get_us_stocks()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_hk_stocks", "get_us_stocks", "HKUSFactory"]
