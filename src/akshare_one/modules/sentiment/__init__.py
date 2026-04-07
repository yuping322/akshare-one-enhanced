"""
Market sentiment data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import SentimentFactory
from . import eastmoney


@api_endpoint(SentimentFactory)
def get_hot_rank(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get hot stock ranking.
    """
    pass


@api_endpoint(SentimentFactory)
def get_stock_sentiment(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock sentiment data.
    """
    pass


__all__ = ["get_hot_rank", "get_stock_sentiment", "SentimentFactory"]
