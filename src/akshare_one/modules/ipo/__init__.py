"""
IPO and new stocks (新股次新) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import IPOFactory


def get_new_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get newly listed stocks.

    Returns:
        pd.DataFrame: New stocks with symbol, name, price, change_pct, etc.
    """
    from ...__init__ import apply_data_filter

    provider = IPOFactory.get_provider(source=source)
    df = provider.get_new_stocks()
    return apply_data_filter(df, columns, row_filter)


def get_ipo_info(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get IPO information.

    Returns:
        pd.DataFrame: IPO info with symbol, name, issue_price, subscription_date, etc.
    """
    from ...__init__ import apply_data_filter

    provider = IPOFactory.get_provider(source=source)
    df = provider.get_ipo_info()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_new_stocks", "get_ipo_info", "IPOFactory"]
