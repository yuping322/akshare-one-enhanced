"""
Concept sector (概念板块) data module.
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import ConceptFactory


def get_concept_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get concept sector list.

    Returns:
        pd.DataFrame: Concept list
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = ConceptFactory.create_router(sources=source)
        df = router.execute("get_concept_list")
    else:
        provider = ConceptFactory.get_provider(source=source)
        df = provider.get_concept_list()

    return apply_data_filter(df, columns, row_filter)


def get_concept_stocks(
    concept: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get stocks in a concept sector.

    Args:
        concept: Concept name (e.g., '华为概念')

    Returns:
        pd.DataFrame: Stock list
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = ConceptFactory.create_router(sources=source)
        df = router.execute("get_concept_stocks", concept)
    else:
        provider = ConceptFactory.get_provider(source=source)
        df = provider.get_concept_stocks(concept)

    return apply_data_filter(df, columns, row_filter)


__all__ = ["get_concept_list", "get_concept_stocks", "ConceptFactory"]
