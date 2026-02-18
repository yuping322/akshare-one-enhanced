"""
Factory for creating goodwill data providers.
"""

from ..factory_base import BaseFactory
from .base import GoodwillProvider
from .eastmoney import EastmoneyGoodwillProvider
from .sina import SinaGoodwillProvider


class GoodwillFactory(BaseFactory[GoodwillProvider]):
    """Factory class for creating goodwill data providers."""

    _providers: dict[str, type[GoodwillProvider]] = {
        "eastmoney": EastmoneyGoodwillProvider,
        "sina": SinaGoodwillProvider,
    }
