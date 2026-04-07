"""
Options data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import OptionsDataFactory
from . import sina
from . import eastmoney


@api_endpoint(OptionsDataFactory)
def get_options_chain(
    underlying_symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get options chain for an underlying asset.

    Args:
        underlying_symbol: Underlying asset symbol
    """
    pass


@api_endpoint(OptionsDataFactory)
def get_options_realtime(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get realtime options quote.

    Args:
        symbol: Option symbol
    """
    pass


@api_endpoint(OptionsDataFactory)
def get_options_expirations(
    underlying_symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get available expiration dates for options.

    Args:
        underlying_symbol: Underlying asset symbol
    """
    pass


@api_endpoint(OptionsDataFactory)
def get_options_history(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get historical options quote.

    Args:
        symbol: Option symbol
        start_date: Start date
        end_date: End date
    """
    pass


__all__ = [
    "get_options_chain",
    "get_options_realtime",
    "get_options_expirations",
    "get_options_history",
    "OptionsDataFactory",
]
