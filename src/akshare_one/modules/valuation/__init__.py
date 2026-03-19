"""
Valuation data module.

This module provides interfaces to fetch valuation data including:
- Stock valuation (PE, PB, PS, etc.)
- Market valuation
- Industry valuation
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import ValuationFactory


@doc_params
def get_stock_valuation(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock valuation data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return ValuationFactory.call_provider_method(
        "get_stock_valuation",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_market_valuation(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get market-wide valuation data.
    """
    return ValuationFactory.call_provider_method(
        "get_market_valuation",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_stock_valuation",
    "get_market_valuation",
    "ValuationFactory",
]
