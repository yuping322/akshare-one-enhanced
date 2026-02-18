"""
Concept sector (概念板块) data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import ConceptFactory


def get_concept_list(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get concept sector list.

    Returns:
        pd.DataFrame: Concept list with rank, name, code, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = ConceptFactory.get_provider(source=source)
    df = provider.get_concept_list()
    return apply_data_filter(df, columns, row_filter)


def get_concept_stocks(
    concept: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stocks in a concept sector.

    Args:
        concept: Concept name (e.g., '云计算', '人工智能')

    Returns:
        pd.DataFrame: Stock list with symbol, name, price, change_pct, etc.
    """
    from ...client import apply_data_filter

    provider = ConceptFactory.get_provider(source=source)
    df = provider.get_concept_stocks(concept)
    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_concept_list", "get_concept_stocks", "ConceptFactory"]
