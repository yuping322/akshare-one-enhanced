"""
Sentiment data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import SentimentFactory


def get_hot_rank(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get hot stock ranking.

    Args:
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame: Hot stocks with rank, symbol, name, price, etc.
    """
    from akshare_one.client import apply_data_filter

    provider = SentimentFactory.get_provider(source=source)
    df = provider.get_hot_rank()
    return apply_data_filter(df, columns, row_filter)


def get_stock_sentiment(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stock sentiment scores and comments.

    Args:
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"query": "score > 50"}

    Returns:
        pd.DataFrame: Stocks with sentiment scores and attention index.
    """
    from akshare_one.client import apply_data_filter

    provider = SentimentFactory.get_provider(source=source)
    df = provider.get_stock_comment()
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_hot_rank", "get_stock_sentiment", "SentimentFactory"]
