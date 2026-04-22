"""Concept sector providers."""

from typing import Any

import pandas as pd

from .base import ConceptFactory, ConceptProvider
from .eastmoney import EastmoneyConceptProvider


def get_concept_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get concept sector list."""
    from .....http_client import apply_data_filter

    if isinstance(source, list) or source is None:
        from .....modules.core.router import MultiSourceRouter

        providers = []
        for s in source or ["eastmoney"]:
            try:
                providers.append((s, ConceptFactory.get_provider(source=s)))
            except Exception:
                pass
        router = MultiSourceRouter(providers)
        df = router.execute("get_concept_list")
    else:
        provider = ConceptFactory.get_provider(source=source)
        df = provider.get_concept_list()

    return apply_data_filter(df, columns, row_filter)


def get_concept_stocks(
    concept_id: str,
    source: str = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get stocks in a concept sector."""
    from .....http_client import apply_data_filter

    provider = ConceptFactory.get_provider(source=source, concept_id=concept_id)
    df = provider.get_concept_stocks(concept_id)
    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "ConceptFactory",
    "ConceptProvider",
    "EastmoneyConceptProvider",
    "get_concept_list",
    "get_concept_stocks",
]
