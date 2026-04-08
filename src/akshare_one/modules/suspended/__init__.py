"""
Suspended (停复牌) stocks module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney
from .base import SuspendedFactory


@api_endpoint(SuspendedFactory)
def get_suspended_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get suspended/halted stocks.
    """
    pass


__all__ = ["get_suspended_stocks", "SuspendedFactory"]
