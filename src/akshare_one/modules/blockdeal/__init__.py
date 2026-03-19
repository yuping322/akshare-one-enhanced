"""
Block deal data module for PV.BlockDeal.

This module provides interfaces to fetch block deal (大宗交易) data including:
- Block deal details (individual stock and market-wide)
- Block deal summary statistics
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import BlockDealFactory


@doc_params
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
    return BlockDealFactory.call_provider_method(
        "get_block_deal",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_block_deal_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    group_by: Literal["stock", "date", "broker"] = "stock",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get block deal summary statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('stock', 'date', or 'broker')
    """
    return BlockDealFactory.call_provider_method(
        "get_block_deal_summary",
        start_date,
        end_date,
        group_by,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_block_deal",
    "get_block_deal_summary",
    "BlockDealFactory",
]
