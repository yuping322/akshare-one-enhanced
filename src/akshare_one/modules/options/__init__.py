"""
Options data module.
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import OptionsDataFactory


@doc_params
def get_options_chain(
    underlying_symbol: str,
    option_type: Literal["call", "put"] | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get options chain data.

    Args:
        underlying_symbol: Underlying stock/ETF symbol (e.g., '510300')
        option_type: Option type ('call', 'put', or None for all)
    """
    return OptionsDataFactory.call_provider_method(
        "get_options_chain",
        source=source,
        columns=columns,
        row_filter=row_filter,
        underlying_symbol=underlying_symbol,
        option_type=option_type,
    )


@doc_params
def get_options_realtime(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get realtime options quote data.

    Args:
        symbol: Option symbol (e.g., '10004005')
    """
    return OptionsDataFactory.call_provider_method(
        "get_options_realtime",
        symbol,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_options_history(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get historical options data.

    Args:
        symbol: Option symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    return OptionsDataFactory.call_provider_method(
        "get_options_history",
        symbol,
        start_date,
        end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_options_chain",
    "get_options_realtime",
    "get_options_history",
    "OptionsDataFactory",
]
