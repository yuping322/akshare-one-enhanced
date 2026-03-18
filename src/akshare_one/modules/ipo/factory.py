"""
Factory for creating IPO data providers.
"""

from ..factory_base import BaseFactory
from .base import IPOProvider
from .eastmoney import EastmoneyIPOProvider


class IPOFactory(BaseFactory[IPOProvider]):
    """Factory for IPO data providers."""
    _providers: dict[str, type[IPOProvider]] = {
        "eastmoney": EastmoneyIPOProvider,
    }
