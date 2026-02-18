"""
Factory for creating ESG rating data providers.
"""

from ..factory_base import BaseFactory
from .base import ESGProvider
from .eastmoney import EastmoneyESGProvider
from .sina import SinaESGProvider


class ESGFactory(BaseFactory[ESGProvider]):
    """Factory class for creating ESG rating data providers."""

    _providers: dict[str, type[ESGProvider]] = {
        "eastmoney": EastmoneyESGProvider,
        "sina": SinaESGProvider,
    }
