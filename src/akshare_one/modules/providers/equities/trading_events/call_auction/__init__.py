"""
Call Auction (集合竞价) data provider.

This module provides interfaces to fetch call auction data including:
- Single stock call auction data
- Batch call auction data for multiple stocks
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import netease
from .base import CallAuctionFactory


@api_endpoint(CallAuctionFactory)
def get_call_auction(
    symbol: str,
    source: SourceType = "netease",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get call auction data for a single stock.

    Args:
        symbol: Stock symbol (6-digit code, e.g., '600000', '000001')
    """
    pass


@api_endpoint(CallAuctionFactory)
def get_call_auction_batch(
    symbols: list[str],
    source: SourceType = "netease",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get call auction data for multiple stocks.

    Args:
        symbols: List of stock symbols (6-digit codes)
    """
    pass


__all__ = [
    "get_call_auction",
    "get_call_auction_batch",
    "CallAuctionFactory",
]
