"""
Factory for creating index data providers.
"""

from ..factory_base import BaseFactory
from .base import IndexProvider
from .eastmoney import EastmoneyIndexProvider
from .sina import SinaIndexProvider


class IndexFactory(BaseFactory[IndexProvider]):
    """Factory class for creating index data providers."""

    _providers: dict[str, type[IndexProvider]] = {
        "eastmoney": EastmoneyIndexProvider,
        "sina": SinaIndexProvider,
    }
