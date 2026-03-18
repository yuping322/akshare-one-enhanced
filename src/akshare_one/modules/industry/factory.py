"""
Factory for creating industry sector data providers.
"""

from ..factory_base import BaseFactory
from .base import IndustryProvider
from .eastmoney import EastmoneyIndustryProvider


class IndustryFactory(BaseFactory[IndustryProvider]):
    """Factory for industry sector data providers."""
    _providers: dict[str, type[IndustryProvider]] = {
        "eastmoney": EastmoneyIndustryProvider,
    }
