"""
Sentiment data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import SentimentFactory


@doc_params
def get_hot_rank(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get hot stock ranking.
    """
    return SentimentFactory.call_provider_method(
        "get_hot_rank",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_stock_sentiment(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock sentiment scores and comments.
    """
    return SentimentFactory.call_provider_method(
        "get_stock_comment",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_hot_rank", "get_stock_sentiment", "SentimentFactory"]
