"""
Factory for creating margin financing data providers.
"""

from ..factory_base import BaseFactory
from .base import MarginProvider
from .eastmoney import EastmoneyMarginProvider
from .sina import SinaMarginProvider


class MarginFactory(BaseFactory[MarginProvider]):
    """Factory class for creating margin financing data providers."""

    _providers: dict[str, type[MarginProvider]] = {
        "eastmoney": EastmoneyMarginProvider,
        "sina": SinaMarginProvider,
    }
