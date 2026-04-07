"""
Base provider class for concept sector data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ConceptProvider(BaseProvider):
    """Base class for concept sector data providers."""

    def get_data_type(self) -> str:
        return "concept"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_concept_list(self, **kwargs) -> pd.DataFrame:
        """Get concept sector list."""
        return self._execute_api_mapped("get_concept_list", **kwargs)

    def get_concept_stocks(self, concept: str, **kwargs) -> pd.DataFrame:
        """Get stocks in a concept sector."""
        return self._execute_api_mapped("get_concept_stocks", concept=concept, **kwargs)


class ConceptFactory(BaseFactory["ConceptProvider"]):
    """Factory class for creating concept sector data providers."""

    _providers: dict[str, type["ConceptProvider"]] = {}
