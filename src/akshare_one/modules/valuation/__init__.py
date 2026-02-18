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
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stock valuation data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sort_by": "pe_ttm"}

    Returns:
        pd.DataFrame: Valuation data with columns:
            - date: Date
            - symbol: Stock symbol
            - close: Closing price
            - pe_ttm: PE (TTM)
            - pe_static: PE (Static)
            - pb: Price to Book
            - ps: Price to Sales
            - pcf: Price to Cash Flow
            - peg: PEG ratio
            - market_cap: Total market cap
            - float_market_cap: Float market cap

    Example:
        >>> df = get_stock_valuation("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    from akshare_one.client import apply_data_filter

    provider = ValuationFactory.get_provider(source=source)
    df = provider.get_stock_valuation(symbol, start_date, end_date)
    return apply_data_filter(df, columns, row_filter)


def get_market_valuation(
    source: Literal["eastmoney", "legu"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get market-wide valuation data.

    Args:
        source: Data source ('eastmoney' or 'legu')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame: Market valuation data with columns:
            - date: Date
            - index_name: Index name
            - pe: PE ratio
            - pb: PB ratio

    Example:
        >>> df = get_market_valuation()
        >>> print(df.head())
    """
    from akshare_one.client import apply_data_filter

    provider = ValuationFactory.get_provider(source=source)
    df = provider.get_market_valuation()
    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_stock_valuation",
    "get_market_valuation",
    "ValuationFactory",
]
