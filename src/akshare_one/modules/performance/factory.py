"""
Factory for creating performance data providers.
"""

from ..factory_base import BaseFactory
from .base import PerformanceProvider
from .eastmoney import EastmoneyPerformanceProvider


class PerformanceFactory(BaseFactory[PerformanceProvider]):
    """Factory class for creating performance data providers."""

    _providers: dict[str, type[PerformanceProvider]] = {
        "eastmoney": EastmoneyPerformanceProvider,
    }
