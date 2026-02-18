"""
Factory for creating info data providers.
"""

from ..factory_base import BaseFactory
from .base import InfoDataProvider
from .eastmoney import EastmoneyInfo
from .sina import SinaInfo


class InfoDataFactory(BaseFactory[InfoDataProvider]):
    """Factory class for creating info data providers."""

    _providers: dict[str, type[InfoDataProvider]] = {
        "eastmoney": EastmoneyInfo,
        "sina": SinaInfo,
    }
