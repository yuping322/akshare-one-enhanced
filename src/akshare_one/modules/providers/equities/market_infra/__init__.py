"""
Market infrastructure module - exchanges, instruments, universes.
"""

import pandas as pd

from ....core.base import ColumnsType, FilterType, SourceType
from ....core.factory import api_endpoint
from . import baostock
from . import tickflow
from .base import ExchangeFactory, InstrumentFactory, UniverseFactory


@api_endpoint(InstrumentFactory)
def get_instruments(
    symbols: str | list[str] | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get instrument metadata.

    Args:
        symbols: Instrument symbols (single or list)
    """
    pass


@api_endpoint(ExchangeFactory)
def get_exchanges(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get exchange list.
    """
    pass


@api_endpoint(ExchangeFactory)
def get_exchange_instruments(
    exchange: str,
    type: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get instruments for a specific exchange.

    Args:
        exchange: Exchange code (SH, SZ, BJ, US, HK)
        type: Instrument type filter (stock, etf, index, etc.)
    """
    pass


@api_endpoint(UniverseFactory)
def get_universes(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get universe (标的池) list.
    """
    pass


@api_endpoint(UniverseFactory)
def get_universe_detail(
    universe_id: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get universe detail.

    Args:
        universe_id: Universe ID
    """
    pass


__all__ = [
    "get_instruments",
    "get_exchanges",
    "get_exchange_instruments",
    "get_universes",
    "get_universe_detail",
    "InstrumentFactory",
    "ExchangeFactory",
    "UniverseFactory",
]
