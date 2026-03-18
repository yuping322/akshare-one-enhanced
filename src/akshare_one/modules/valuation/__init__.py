"""
Valuation data module.

This module provides interfaces to fetch valuation data including:
- Stock valuation (PE, PB, PS, etc.)
- Market valuation
- Industry valuation
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import ValuationFactory


def get_stock_valuation(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stock valuation data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Valuation data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = ValuationFactory.create_router(sources=source)
        df = router.execute("get_stock_valuation", symbol, start_date, end_date)
    else:
        provider = ValuationFactory.get_provider(source=source)
        df = provider.get_stock_valuation(symbol, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


def get_market_valuation(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get market-wide valuation data.

    Args:
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Market valuation data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = ValuationFactory.create_router(sources=source)
        df = router.execute("get_market_valuation")
    else:
        provider = ValuationFactory.get_provider(source=source)
        df = provider.get_market_valuation()

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_stock_valuation",
    "get_market_valuation",
    "ValuationFactory",
]
