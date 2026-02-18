"""
Factory for creating northbound capital data providers.
"""

from ..factory_base import BaseFactory
from .base import NorthboundProvider
from .eastmoney import EastmoneyNorthboundProvider
from .sina import SinaNorthboundProvider


class NorthboundFactory(BaseFactory[NorthboundProvider]):
    """Factory class for creating northbound capital data providers."""

    _providers: dict[str, type[NorthboundProvider]] = {
        "eastmoney": EastmoneyNorthboundProvider,
        "sina": SinaNorthboundProvider,
    }
