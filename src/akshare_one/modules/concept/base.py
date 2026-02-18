"""
Base provider class for concept sector data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class ConceptProvider(BaseProvider):
    """Abstract base class for concept sector data providers."""

    def get_data_type(self) -> str:
        return "concept"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_concept_list(self) -> pd.DataFrame:
        """Get concept sector list."""
        pass

    @abstractmethod
    def get_concept_stocks(self, concept: str) -> pd.DataFrame:
        """Get stocks in a concept sector."""
        pass
