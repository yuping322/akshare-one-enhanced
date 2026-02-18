"""
Analyst data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import AnalystFactory


def get_analyst_rank(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get analyst ranking.

    Args:
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sort_by": "return_ytd"}

    Returns:
        pd.DataFrame: Analyst ranking with returns and industry info.
    """
    from akshare_one.client import apply_data_filter

    provider = AnalystFactory.get_provider(source=source)
    df = provider.get_analyst_rank()
    return apply_data_filter(df, columns, row_filter)


def get_research_report(
    symbol: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get research reports for a stock.

    Args:
        symbol: Stock symbol (e.g., '600000')
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame: Research reports with title, rating, institution, etc.
    """
    from akshare_one.client import apply_data_filter

    provider = AnalystFactory.get_provider(source=source)
    df = provider.get_research_report(symbol)
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_analyst_rank", "get_research_report", "AnalystFactory"]
