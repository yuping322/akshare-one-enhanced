"""
Block deal (大宗交易) data module for PV.BlockDeal.

This module provides interfaces to fetch block deal data including:
- Individual stock block deal transactions
- Market-wide block deal details
- Block deal summary statistics by date, stock, or broker
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import BlockDealFactory
from . import eastmoney, sina


@api_endpoint(BlockDealFactory)
def get_block_deal(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get block deal transaction details.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(BlockDealFactory)
def get_block_deal_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    group_by: Literal["date", "stock", "broker"] = "date",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get block deal summary statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('date', 'stock', or 'broker')
    """
    pass


__all__ = [
    "get_block_deal",
    "get_block_deal_summary",
    "BlockDealFactory",
]
