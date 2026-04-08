"""
IPO data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, lixinger
from .base import IPOFactory


@api_endpoint(IPOFactory)
def get_new_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get newly listed stocks.
    """
    pass


@api_endpoint(IPOFactory)
def get_ipo_info(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get IPO information.
    """
    pass


__all__ = ["get_new_stocks", "get_ipo_info", "IPOFactory"]
