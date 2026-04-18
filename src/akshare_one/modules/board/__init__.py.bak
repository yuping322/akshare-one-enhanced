"""
Board (科创板/创业板) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, efinance
from .base import BoardFactory


@api_endpoint(BoardFactory)
def get_kcb_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get KCB (科创板) stocks.
    """
    pass


@api_endpoint(BoardFactory)
def get_cyb_stocks(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get CYB (创业板) stocks.
    """
    pass


@api_endpoint(BoardFactory)
def get_belong_board(
    stock_code: str,
    source: SourceType = "efinance",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get which boards/concepts a stock belongs to.

    Args:
        stock_code: Stock code (e.g., '600000', '000001')
    """
    pass


__all__ = ["get_kcb_stocks", "get_cyb_stocks", "get_belong_board", "BoardFactory"]
