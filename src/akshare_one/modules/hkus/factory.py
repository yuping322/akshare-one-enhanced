"""
Factory for creating HK/US stock data providers.
"""

from ..factory_base import BaseFactory
from .base import HKUSProvider
from .eastmoney import EastmoneyHKUSProvider


class HKUSFactory(BaseFactory[HKUSProvider]):
    """Factory for HK/US stock data providers."""
    _providers: dict[str, type[HKUSProvider]] = {
        "eastmoney": EastmoneyHKUSProvider,
    }
