"""
Factory for creating ETF data providers.
"""

from ..factory_base import BaseFactory
from .base import ETFProvider
from .eastmoney import EastmoneyETFProvider
from .sina import SinaETFProvider


class ETFFactory(BaseFactory[ETFProvider]):
    """Factory class for creating ETF data providers."""

    _providers: dict[str, type[ETFProvider]] = {
        "eastmoney": EastmoneyETFProvider,
        "sina": SinaETFProvider,
    }
