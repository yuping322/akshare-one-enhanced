"""
ST stocks (ST板块) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import STFactory


def get_st_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ST (Special Treatment) stocks.

    Returns:
        pd.DataFrame: ST stocks with symbol, name, price, change_pct, etc.
    """
    from ...__init__ import apply_data_filter

    provider = STFactory.get_provider(source=source)
    df = provider.get_st_stocks()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_st_stocks", "STFactory"]
