"""
Bond (Convertible Bond) data module.

This module provides interfaces to fetch bond data including:
- Convertible bond list and realtime quotes
- Bond historical data
- Bond adjustment logs
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import BondFactory
from . import eastmoney, jsl  # 触发 Provider 注册


@api_endpoint(BondFactory)
def get_bond_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get convertible bond list.
    """
    pass


@api_endpoint(BondFactory)
def get_bond_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get bond historical data.

    Args:
        symbol: Bond symbol (e.g., 'sh113050')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(BondFactory)
def get_bond_realtime_data(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get bond realtime quotes.
    """
    pass


__all__ = [
    "get_bond_list",
    "get_bond_hist_data",
    "get_bond_realtime_data",
    "BondFactory",
]
