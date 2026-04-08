"""
Stock basic information module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, sina
from .base import InfoDataFactory


@api_endpoint(InfoDataFactory)
def get_basic_info(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get basic information for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


__all__ = ["get_basic_info", "InfoDataFactory"]
