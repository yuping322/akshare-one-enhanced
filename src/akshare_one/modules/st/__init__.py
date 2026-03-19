"""
ST stocks (ST板块) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import STFactory


@doc_params
def get_st_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ST (Special Treatment) stocks.
    """
    return STFactory.call_provider_method(
        "get_st_stocks",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_st_stocks", "STFactory"]
