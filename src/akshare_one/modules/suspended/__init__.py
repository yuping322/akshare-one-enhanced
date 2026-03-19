"""
Suspended stocks (停复牌) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import SuspendedFactory


@doc_params
def get_suspended_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get suspended/halted stocks.
    """
    return SuspendedFactory.call_provider_method(
        "get_suspended_stocks",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_suspended_stocks", "SuspendedFactory"]
