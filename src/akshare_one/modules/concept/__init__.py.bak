"""
Concept sector (概念板块) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney
from .base import ConceptFactory


@api_endpoint(ConceptFactory)
def get_concept_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get concept sector list.
    """
    pass


@api_endpoint(ConceptFactory)
def get_concept_stocks(
    concept: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stocks in a concept sector.

    Args:
        concept: Concept name or code
    """
    pass


__all__ = ["get_concept_list", "get_concept_stocks", "ConceptFactory"]
