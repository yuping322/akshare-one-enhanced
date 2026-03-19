"""
Analyst data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import AnalystFactory
from . import eastmoney  # 触发 Provider 注册


@api_endpoint(AnalystFactory)
def get_analyst_rank(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get analyst ranking.
    """
    pass


@api_endpoint(AnalystFactory)
def get_research_report(
    symbol: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get research reports for a stock.

    Args:
        symbol: Stock symbol (e.g., '600000')
    """
    pass


__all__ = ["get_analyst_rank", "get_research_report", "AnalystFactory"]
