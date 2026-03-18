"""
Factory for creating ST stocks data providers.
"""

from ..factory_base import BaseFactory
from .base import STProvider
from .eastmoney import EastmoneySTProvider


class STFactory(BaseFactory[STProvider]):
    """Factory for ST stocks data providers."""
    _providers: dict[str, type[STProvider]] = {
        "eastmoney": EastmoneySTProvider,
    }
