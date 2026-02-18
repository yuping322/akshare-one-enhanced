"""
Factory for creating dragon tiger list data providers.
"""

from ..factory_base import BaseFactory
from .base import DragonTigerProvider
from .eastmoney import EastmoneyDragonTigerProvider
from .sina import SinaLHBProvider


class DragonTigerFactory(BaseFactory[DragonTigerProvider]):
    """Factory class for creating dragon tiger list data providers."""

    _providers: dict[str, type[DragonTigerProvider]] = {
        "eastmoney": EastmoneyDragonTigerProvider,
        "sina": SinaLHBProvider,
    }
