"""
Hong Kong and US stock data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import HKUSFactory


def get_hk_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get HK stock list.

    Returns:
        pd.DataFrame: HK stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = HKUSFactory.create_router(sources=source)
        df = router.execute("get_hk_stocks")
    else:
        provider = HKUSFactory.get_provider(source=source)
        df = provider.get_hk_stocks()

    return apply_data_filter(df, columns, row_filter)


def get_us_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get US stock list.

    Returns:
        pd.DataFrame: US stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = HKUSFactory.create_router(sources=source)
        df = router.execute("get_us_stocks")
    else:
        provider = HKUSFactory.get_provider(source=source)
        df = provider.get_us_stocks()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_hk_stocks", "get_us_stocks", "HKUSFactory"]
