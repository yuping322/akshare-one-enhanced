"""
Factory for creating concept sector data providers.
"""

from ..factory_base import BaseFactory
from .base import ConceptProvider
from .eastmoney import EastmoneyConceptProvider


class ConceptFactory(BaseFactory[ConceptProvider]):
    """Factory for concept sector data providers."""
    _providers: dict[str, type[ConceptProvider]] = {
        "eastmoney": EastmoneyConceptProvider,
    }
