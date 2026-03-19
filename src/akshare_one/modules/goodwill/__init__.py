"""
Goodwill (商誉) data module for PV.Goodwill.

This module provides interfaces to fetch goodwill data including:
- Goodwill data (商誉数据) - balance and ratios
- Goodwill impairment expectations (商誉减值预期) - risk assessment
- Goodwill by industry (行业商誉统计) - industry aggregation
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import GoodwillFactory


@doc_params
def get_goodwill_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get goodwill data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return GoodwillFactory.call_provider_method(
        "get_goodwill_data",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_goodwill_impairment(
    date: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get goodwill impairment expectations.

    Args:
        date: Query date in YYYY-MM-DD format
    """
    return GoodwillFactory.call_provider_method(
        "get_goodwill_impairment",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_goodwill_by_industry(
    date: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get goodwill statistics by industry.

    Args:
        date: Query date in YYYY-MM-DD format
    """
    return GoodwillFactory.call_provider_method(
        "get_goodwill_by_industry",
        date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_goodwill_data",
    "get_goodwill_impairment",
    "get_goodwill_by_industry",
    "GoodwillFactory",
]
