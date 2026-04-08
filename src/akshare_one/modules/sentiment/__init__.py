"""
Market sentiment data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import SentimentFactory
from . import eastmoney


@api_endpoint(SentimentFactory, method_name="get_hot_rank")
def get_hot_rank(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get hot stock ranking.
    """
    pass


@api_endpoint(SentimentFactory, method_name="get_stock_comment")
def get_stock_sentiment(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock sentiment data (comments and scores).
    """
    pass


# Macro Sentiment indicators (Internal for akshare-one)
def compute_fed_model(index_code: str = "000300", bond_rate: float = None):
    from ..alpha.sentiment import compute_fed_model as _fed

    return _fed(index_code, bond_rate)


def compute_crowding_ratio(date: str = None):
    from ..alpha.sentiment import compute_crowding_ratio as _crowd

    return _crowd(date)


def compute_graham_index(index_code: str = "000300"):
    from ..alpha.sentiment import compute_graham_index as _graham

    return _graham(index_code)


def compute_below_net_ratio():
    from ..alpha.sentiment import compute_below_net_ratio as _net

    return _net()


__all__ = [
    "get_hot_rank",
    "get_stock_sentiment",
    "SentimentFactory",
    "compute_fed_model",
    "compute_crowding_ratio",
    "compute_graham_index",
    "compute_below_net_ratio",
]
