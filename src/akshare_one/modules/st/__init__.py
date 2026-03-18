"""
ST stocks (ST板块) data module.
"""

from typing import Literal
import pandas as pd
from typing import Any

from .factory import STFactory


def get_st_stocks(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ST (Special Treatment) stocks.

    Returns:
        pd.DataFrame: ST stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = STFactory.create_router(sources=source)
        df = router.execute("get_st_stocks")
    else:
        provider = STFactory.get_provider(source=source)
        df = provider.get_st_stocks()

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_st_stocks", "STFactory"]
