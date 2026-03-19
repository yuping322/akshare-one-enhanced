"""
Margin Financing (融资融券) data module for PV.MarginFinancing.

This module provides interfaces to fetch margin financing data including:
- Margin financing data (融资融券数据) - individual stocks and market-wide
- Margin financing summary (融资融券汇总) - market aggregation
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import MarginFactory


@doc_params
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
    return MarginFactory.call_provider_method(
        "get_margin_data",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
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
        market: Market ('sh' for Shanghai, 'sz' for Shenzhen, 'all' for both)
    """
    return MarginFactory.call_provider_method(
        "get_margin_summary",
        start_date,
        end_date,
        market,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_margin_data",
    "get_margin_summary",
    "MarginFactory",
]
