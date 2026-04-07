"""
ST (Special Treatment) stocks module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import STFactory
from . import eastmoney


@api_endpoint(STFactory)
def get_st_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ST (Special Treatment) stocks.
    """
    pass


__all__ = ["get_st_stocks", "STFactory"]
