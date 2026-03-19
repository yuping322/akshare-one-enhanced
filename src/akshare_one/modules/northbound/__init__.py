"""
Northbound capital (HSGT) data module for PV.NorthboundHSGT.

This module provides interfaces to fetch northbound capital data including:
- Northbound capital flow (Shanghai/Shenzhen Connect)
- Northbound holdings details
- Northbound capital rankings
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import NorthboundFactory
from . import eastmoney, sina  # 触发 Provider 注册


@api_endpoint(NorthboundFactory)
def get_northbound_flow(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound capital flow data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market type ('sh' for Shanghai, 'sz' for Shenzhen, 'all' for both)
    """
    pass


@api_endpoint(NorthboundFactory)
def get_northbound_holdings(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound holdings details.

    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(NorthboundFactory)
def get_northbound_top_stocks(
    date: str,
    market: Literal["sh", "sz", "all"] = "all",
    top_n: int = 100,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound capital top stocks ranking.

    Args:
        date: Date in YYYY-MM-DD format
        market: Market type ('sh', 'sz', or 'all')
        top_n: Number of top stocks to return
    """
    pass


__all__ = [
    "get_northbound_flow",
    "get_northbound_holdings",
    "get_northbound_top_stocks",
    "NorthboundFactory",
]
