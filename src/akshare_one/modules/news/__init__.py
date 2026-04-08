"""
Financial news and market intelligence module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, sina
from .base import NewsDataFactory


@api_endpoint(NewsDataFactory)
def get_news_data(
    symbol: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get financial news for a stock or the market.

    Args:
        symbol: Stock symbol. If None, returns market news.
    """
    pass


__all__ = ["get_news_data", "NewsDataFactory"]
