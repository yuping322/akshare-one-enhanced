"""
Factory for creating insider data providers.
"""

from ..factory_base import BaseFactory
from .base import InsiderDataProvider
from .eastmoney import EastmoneyInsiderProvider
from .xueqiu import XueQiuInsider


class InsiderDataFactory(BaseFactory[InsiderDataProvider]):
    """Factory class for creating insider data providers."""

    _providers: dict[str, type[InsiderDataProvider]] = {
        "xueqiu": XueQiuInsider,
        "eastmoney": EastmoneyInsiderProvider,
    }
