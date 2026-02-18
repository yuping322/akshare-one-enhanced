"""
Suspended stocks (停复牌) data module.
"""

from typing import Any, Literal

import pandas as pd

from .factory import SuspendedFactory


def get_suspended_stocks(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get suspended/halted stocks.

    Returns:
        pd.DataFrame: Suspended stocks with symbol, name, suspend_date, reason, etc.
    """
    from ...client import apply_data_filter

    provider = SuspendedFactory.get_provider(source=source)
    df = provider.get_suspended_stocks()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_suspended_stocks", "SuspendedFactory"]
