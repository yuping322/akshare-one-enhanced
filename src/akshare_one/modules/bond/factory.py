"""
Factory for creating bond data providers.
"""

from ..factory_base import BaseFactory
from .base import BondProvider
from .eastmoney import EastmoneyBondProvider
from .jsl import JSLBondProvider


class BondFactory(BaseFactory[BondProvider]):
    """Factory class for creating bond data providers."""

    _providers: dict[str, type[BondProvider]] = {
        "eastmoney": EastmoneyBondProvider,
        "jsl": JSLBondProvider,
    }
