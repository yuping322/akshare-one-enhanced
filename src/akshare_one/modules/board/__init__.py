"""
Special boards (科创板/创业板) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import BoardFactory


def get_kcb_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get KCB (科创板) stocks.

    Returns:
        pd.DataFrame: KCB stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = BoardFactory.create_router(sources=source)
        df = router.execute("get_kcb_stocks")
    else:
        provider = BoardFactory.get_provider(source=source)
        df = provider.get_kcb_stocks()

    return apply_data_filter(df, columns, row_filter)


def get_cyb_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get CYB (创业板) stocks.

    Returns:
        pd.DataFrame: CYB stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = BoardFactory.create_router(sources=source)
        df = router.execute("get_cyb_stocks")
    else:
        provider = BoardFactory.get_provider(source=source)
        df = provider.get_cyb_stocks()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_kcb_stocks", "get_cyb_stocks", "BoardFactory"]
