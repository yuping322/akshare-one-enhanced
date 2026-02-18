"""
Factory for creating analyst data providers.
"""

from ..factory_base import BaseFactory
from .base import AnalystProvider
from .eastmoney import EastmoneyAnalystProvider


class AnalystFactory(BaseFactory[AnalystProvider]):
    """Factory class for creating analyst data providers."""

    _providers: dict[str, type[AnalystProvider]] = {
        "eastmoney": EastmoneyAnalystProvider,
    }
