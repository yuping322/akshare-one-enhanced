"""
Factory for creating disclosure data providers.
"""

from ..factory_base import BaseFactory
from .base import DisclosureProvider
from .eastmoney import EastmoneyDisclosureProvider
from .sina import SinaDisclosureProvider


class DisclosureFactory(BaseFactory[DisclosureProvider]):
    """Factory class for creating disclosure data providers."""

    _providers: dict[str, type[DisclosureProvider]] = {
        "eastmoney": EastmoneyDisclosureProvider,
        "sina": SinaDisclosureProvider,
    }
