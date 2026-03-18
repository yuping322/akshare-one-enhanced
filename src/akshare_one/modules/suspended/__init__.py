"""
Suspended stocks (停复牌) data module.
"""

from typing import Any, Literal

import pandas as pd

from .factory import SuspendedFactory


def get_suspended_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get suspended/halted stocks.

    Returns:
        pd.DataFrame: Suspended stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = SuspendedFactory.create_router(sources=source)
        df = router.execute("get_suspended_stocks")
    else:
        provider = SuspendedFactory.get_provider(source=source)
        df = provider.get_suspended_stocks()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_suspended_stocks", "SuspendedFactory"]
