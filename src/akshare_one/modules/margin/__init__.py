"""
Margin financing (融资融券) data module for PV.Margin.

This module provides interfaces to fetch margin financing data including:
- Margin financing data for individual stocks and whole market
- Margin financing summary (market totals by exchange)
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, lixinger, sina
from .base import MarginFactory


@api_endpoint(MarginFactory)
def get_margin_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get margin financing data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MarginFactory)
def get_margin_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get margin financing summary data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market identifier ('sh', 'sz', or 'all')
    """
    pass


__all__ = [
    "get_margin_data",
    "get_margin_summary",
    "MarginFactory",
]
