"""
Bond (可转债) data module for PV.Bond.

This module provides interfaces to fetch bond data including:
- Convertible bond list
- Bond historical price data
- Bond realtime quotes
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import BondFactory
from . import eastmoney, jsl


@api_endpoint(BondFactory)
def get_bond_list(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get convertible bond list.
    """
    pass


@api_endpoint(BondFactory)
def get_bond_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get bond historical data.

    Args:
        symbol: Bond symbol (e.g., '110001')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(BondFactory)
def get_bond_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(BondFactory)
def get_bond_realtime(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get bond realtime quotes.
    """
    pass


@api_endpoint(BondFactory)
def get_bond_realtime_data(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


__all__ = [
    "get_bond_list",
    "get_bond_hist",
    "get_bond_hist_data",
    "get_bond_realtime",
    "get_bond_realtime_data",
    "BondFactory",
]
