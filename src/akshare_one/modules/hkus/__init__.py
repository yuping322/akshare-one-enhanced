"""
Hong Kong and US stock data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import HKUSFactory
from . import eastmoney  # 触发 Provider 注册


@api_endpoint(HKUSFactory)
def get_hk_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get HK stock list.
    """
    pass


@api_endpoint(HKUSFactory)
def get_us_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get US stock list.
    """
    pass


__all__ = ["get_hk_stocks", "get_us_stocks", "HKUSFactory"]
