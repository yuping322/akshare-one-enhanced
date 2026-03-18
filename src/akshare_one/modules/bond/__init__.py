"""
Bond (Convertible Bond) data module.

This module provides interfaces to fetch bond data including:
- Convertible bond list and realtime quotes
- Bond historical data
- Bond adjustment logs
"""

from typing import Any, Literal

import pandas as pd

from .factory import BondFactory


def get_bond_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get convertible bond list.

    Args:
        source: Data source ('eastmoney' or 'jsl')
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Bond list
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = BondFactory.create_router(sources=source)
        df = router.execute("get_bond_list")
    else:
        provider = BondFactory.get_provider(source=source)
        df = provider.get_bond_list()

    return apply_data_filter(df, columns, row_filter)


def get_bond_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond historical data.

    Args:
        symbol: Bond symbol (e.g., 'sh113050')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney' recommended)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Historical data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = BondFactory.create_router(sources=source)
        df = router.execute("get_bond_hist", symbol, start_date, end_date)
    else:
        provider = BondFactory.get_provider(source=source)
        df = provider.get_bond_hist(symbol, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


def get_bond_realtime_data(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond realtime quotes.

    Args:
        source: Data source ('jsl' recommended for more details)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Realtime bond data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = BondFactory.create_router(sources=source)
        df = router.execute("get_bond_realtime")
    else:
        provider = BondFactory.get_provider(source=source)
        df = provider.get_bond_realtime()

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_bond_list",
    "get_bond_hist_data",
    "get_bond_realtime_data",
    "BondFactory",
]
