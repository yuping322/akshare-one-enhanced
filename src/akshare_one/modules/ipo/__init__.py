"""
IPO and new stocks (新股次新) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import IPOFactory


def get_new_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get newly listed stocks.

    Returns:
        pd.DataFrame: New stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = IPOFactory.create_router(sources=source)
        df = router.execute("get_new_stocks")
    else:
        provider = IPOFactory.get_provider(source=source)
        df = provider.get_new_stocks()

    return apply_data_filter(df, columns, row_filter)


def get_ipo_info(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get IPO information.

    Returns:
        pd.DataFrame: IPO info
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = IPOFactory.create_router(sources=source)
        df = router.execute("get_ipo_info")
    else:
        provider = IPOFactory.get_provider(source=source)
        df = provider.get_ipo_info()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_new_stocks", "get_ipo_info", "IPOFactory"]
