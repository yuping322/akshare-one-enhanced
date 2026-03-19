"""
Equity Pledge (股权质押) data module for PV.EquityPledge.

This module provides interfaces to fetch equity pledge data including:
- Equity pledge data (股权质押数据) - shareholder pledge information
- Equity pledge ratio ranking (质押比例排名) - stocks ranked by pledge ratio
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import EquityPledgeFactory


@doc_params
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
    return EquityPledgeFactory.call_provider_method(
        "get_equity_pledge",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
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
        top_n: Number of top stocks to return (default: 100)
    """
    return EquityPledgeFactory.call_provider_method(
        "get_equity_pledge_ratio_rank",
        date,
        top_n,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_equity_pledge",
    "get_equity_pledge_ratio_rank",
    "EquityPledgeFactory",
]
