"""
ESG rating (环境、社会与治理) data module for PV.ESG.

This module provides interfaces to fetch ESG rating data including:
- Individual stock ESG ratings and history
- ESG rating rankings by date and industry
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import ESGFactory
from . import eastmoney, sina


@api_endpoint(ESGFactory)
def get_esg_rating(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ESG rating data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns latest for all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(ESGFactory)
def get_esg_rating_rank(
    date: str | None = None,
    industry: str | None = None,
    top_n: int = 100,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ESG rating rankings.

    Args:
        date: Query date in YYYY-MM-DD format. If None, returns latest.
        industry: Industry name to filter by.
        top_n: Number of top stocks to return.
    """
    pass


__all__ = [
    "get_esg_rating",
    "get_esg_rating_rank",
    "ESGFactory",
]
