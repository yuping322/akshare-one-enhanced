"""
Analyst data module.
"""

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import eastmoney
from .base import AnalystFactory


@api_endpoint(AnalystFactory)
def get_analyst_rank(
    source: SourceType = None,
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
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get research reports for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


__all__ = ["get_analyst_rank", "get_research_report", "AnalystFactory"]
