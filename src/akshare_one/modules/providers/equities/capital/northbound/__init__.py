"""
Northbound Capital (北向资金) data module for PV.Northbound.

This module provides interfaces to fetch northbound capital data including:
- Daily northbound capital flow (net inflow)
- Northbound holdings by stock or date
- Top stocks traded by northbound capital
"""

from typing import Literal

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney, sina, tushare
from .base import NorthboundFactory


@api_endpoint(NorthboundFactory)
def get_northbound_flow(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["all", "sh", "sz"] = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound capital flow data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market type ('all', 'sh', 'sz')
    """
    pass


@api_endpoint(NorthboundFactory)
def get_northbound_holdings(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound holdings details.

    Args:
        symbol: Stock symbol. If None, returns latest for all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(NorthboundFactory)
def get_northbound_top_stocks(
    date: str | None = None,
    market: Literal["all", "sh", "sz"] = "all",
    top_n: int = 100,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get northbound capital top stocks ranking.

    Args:
        date: Query date in YYYY-MM-DD format. If None, returns latest.
        market: Market type ('all', 'sh', 'sz')
        top_n: Number of top stocks to return
    """
    pass


__all__ = [
    "get_northbound_flow",
    "get_northbound_holdings",
    "get_northbound_top_stocks",
    "NorthboundFactory",
]
