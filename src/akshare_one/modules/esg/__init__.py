"""
ESG (ESG 评级) data module for PV.ESG.

This module provides interfaces to fetch ESG rating data including:
- ESG rating (ESG 评分) - comprehensive ESG scores
- ESG rating rank (ESG 评级排名) - industry rankings
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import ESGFactory


@doc_params
def get_esg_rating(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
    page: int = 1,
    page_size: int | None = 1,
) -> pd.DataFrame:
    """
    Get ESG rating data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        page: Page number to return (default: 1)
        page_size: Number of items per page (default: 1)
    """
    return ESGFactory.call_provider_method(
        "get_esg_rating",
        symbol,
        start_date,
        end_date,
        page,
        page_size,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_esg_rating_rank(
    date: str,
    industry: str | None = None,
    top_n: int = 100,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ESG rating rankings.

    Args:
        date: Query date in YYYY-MM-DD format
        industry: Industry filter (optional)
        top_n: Number of top stocks to return (default: 100)
    """
    return ESGFactory.call_provider_method(
        "get_esg_rating_rank",
        date,
        industry,
        top_n,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_esg_rating",
    "get_esg_rating_rank",
    "ESGFactory",
]
