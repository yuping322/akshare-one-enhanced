"""
Special boards (科创板/创业板) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import BoardFactory


@doc_params
def get_kcb_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get KCB (科创板) stocks.
    """
    return BoardFactory.call_provider_method(
        "get_kcb_stocks",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_cyb_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get CYB (创业板) stocks.
    """
    return BoardFactory.call_provider_method(
        "get_cyb_stocks",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_kcb_stocks", "get_cyb_stocks", "BoardFactory"]
