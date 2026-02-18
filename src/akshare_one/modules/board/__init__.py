"""
Special boards (科创板/创业板) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import BoardFactory


def get_kcb_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get KCB (科创板) stocks.

    Returns:
        pd.DataFrame: KCB stocks with symbol, name, price, change_pct, etc.
    """
    from ...__init__ import apply_data_filter

    provider = BoardFactory.get_provider(source=source)
    df = provider.get_kcb_stocks()
    return apply_data_filter(df, columns, row_filter)


def get_cyb_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get CYB (创业板) stocks.

    Returns:
        pd.DataFrame: CYB stocks with symbol, name, price, change_pct, etc.
    """
    from ...__init__ import apply_data_filter

    provider = BoardFactory.get_provider(source=source)
    df = provider.get_cyb_stocks()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_kcb_stocks", "get_cyb_stocks", "BoardFactory"]
