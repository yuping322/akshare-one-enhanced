"""
Realtime market data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, eastmoney_direct, efinance, tickflow, xueqiu
from .base import RealtimeDataFactory


@api_endpoint(RealtimeDataFactory)
def get_current_data(
    symbol: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get realtime market data for a stock or all stocks.

    Args:
        symbol: Stock symbol. If None, returns all stocks.
    """
    pass


__all__ = ["get_current_data", "RealtimeDataFactory"]
