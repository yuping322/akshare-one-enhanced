"""
Northbound capital (HSGT) data module for PV.NorthboundHSGT.

This module provides interfaces to fetch northbound capital data including:
- Northbound capital flow (Shanghai/Shenzhen Connect)
- Northbound holdings details
- Northbound capital rankings
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import NorthboundFactory


def get_northbound_flow(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get northbound capital flow data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market type ('sh' for Shanghai, 'sz' for Shenzhen, 'all' for both)
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized northbound flow data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = NorthboundFactory.create_router(sources=source)
        df = router.execute("get_northbound_flow", start_date, end_date, market)
    else:
        provider = NorthboundFactory.get_provider(source=source)
        df = provider.get_northbound_flow(start_date, end_date, market)

    return apply_data_filter(df, columns, row_filter)


def get_northbound_holdings(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get northbound holdings details.

    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized northbound holdings data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = NorthboundFactory.create_router(sources=source)
        df = router.execute("get_northbound_holdings", symbol, start_date, end_date)
    else:
        provider = NorthboundFactory.get_provider(source=source)
        df = provider.get_northbound_holdings(symbol, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


def get_northbound_top_stocks(
    date: str,
    market: Literal["sh", "sz", "all"] = "all",
    top_n: int = 100,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get northbound capital top stocks ranking.

    Args:
        date: Date in YYYY-MM-DD format
        market: Market type ('sh', 'sz', or 'all')
        top_n: Number of top stocks to return
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized top stocks data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = NorthboundFactory.create_router(sources=source)
        df = router.execute("get_northbound_top_stocks", date, market, top_n)
    else:
        provider = NorthboundFactory.get_provider(source=source)
        df = provider.get_northbound_top_stocks(date, market, top_n)

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_northbound_flow",
    "get_northbound_holdings",
    "get_northbound_top_stocks",
    "NorthboundFactory",
]
