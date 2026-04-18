"""
Insider trading (内部持股变动) data module for PV.Insider.

This module provides interfaces to fetch insider trading data including:
- Individual stock insider trade records
- Market-wide insider trading summary
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney, lixinger, xueqiu
from .base import InsiderDataFactory


@api_endpoint(InsiderDataFactory)
def get_inner_trade_data(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get insider trade data for a stock.

    Args:
        symbol: Stock symbol (e.g., '600000')
    """
    pass


__all__ = ["get_inner_trade_data", "InsiderDataFactory"]
