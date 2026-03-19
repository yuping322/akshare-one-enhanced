"""
IPO and new stocks (新股次新) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import IPOFactory


@doc_params
def get_new_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get newly listed stocks.
    """
    return IPOFactory.call_provider_method(
        "get_new_stocks",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_ipo_info(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get IPO information.
    """
    return IPOFactory.call_provider_method(
        "get_ipo_info",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_new_stocks", "get_ipo_info", "IPOFactory"]
