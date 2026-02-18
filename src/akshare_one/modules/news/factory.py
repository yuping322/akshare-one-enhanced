"""
Factory for creating news data providers.
"""

from ..factory_base import BaseFactory
from .base import NewsDataProvider
from .eastmoney import EastMoneyNews
from .sina import SinaNews


class NewsDataFactory(BaseFactory[NewsDataProvider]):
    """Factory class for creating news data providers."""

    _providers: dict[str, type[NewsDataProvider]] = {
        "eastmoney": EastMoneyNews,
        "sina": SinaNews,
    }
