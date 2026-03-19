"""
Concept sector (概念板块) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import ConceptFactory


@doc_params
def get_concept_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get concept sector list.
    """
    return ConceptFactory.call_provider_method(
        "get_concept_list",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_concept_stocks(
    concept: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stocks in a concept sector.

    Args:
        concept: Concept name (e.g., '华为概念')
    """
    return ConceptFactory.call_provider_method(
        "get_concept_stocks",
        concept,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_concept_list", "get_concept_stocks", "ConceptFactory"]
