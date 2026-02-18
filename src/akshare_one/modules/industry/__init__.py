"""
Industry sector (行业板块) data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import IndustryFactory


def get_industry_list(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get industry sector list.

    Returns:
        pd.DataFrame: Industry list with rank, name, code, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = IndustryFactory.get_provider(source=source)
    df = provider.get_industry_list()
    return apply_data_filter(df, columns, row_filter)


def get_industry_stocks(
    industry: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stocks in an industry sector.

    Args:
        industry: Industry name (e.g., '银行', '房地产')

    Returns:
        pd.DataFrame: Stock list with symbol, name, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = IndustryFactory.get_provider(source=source)
    df = provider.get_industry_stocks(industry)
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_industry_list", "get_industry_stocks", "IndustryFactory"]
