"""
Factory for creating shareholder data providers.
"""

from ..factory_base import BaseFactory
from .base import ShareholderProvider
from .eastmoney import EastmoneyShareholderProvider
from .sse import SSEShareholderProvider


class ShareholderFactory(BaseFactory[ShareholderProvider]):
    """Factory class for creating shareholder data providers."""

    _providers: dict[str, type[ShareholderProvider]] = {
        "eastmoney": EastmoneyShareholderProvider,
        "sse": SSEShareholderProvider,
    }
