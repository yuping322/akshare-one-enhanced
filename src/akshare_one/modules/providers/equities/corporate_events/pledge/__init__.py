"""
Equity pledge (股权质押) data module for PV.Pledge.

This module provides interfaces to fetch equity pledge data including:
- Equity pledge details (shareholder pledge information)
- Equity pledge ratio rankings (stocks ranked by pledge percentage)
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney, lixinger, sina, tushare
from .base import EquityPledgeFactory


@api_endpoint(EquityPledgeFactory)
def get_equity_pledge(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get equity pledge data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(EquityPledgeFactory)
def get_equity_pledge_ratio_rank(
    date: str,
    top_n: int = 100,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get equity pledge ratio ranking.

    Args:
        date: Query date in YYYY-MM-DD format
        top_n: Number of top stocks to return
    """
    pass


__all__ = [
    "get_equity_pledge",
    "get_equity_pledge_ratio_rank",
    "EquityPledgeFactory",
]
