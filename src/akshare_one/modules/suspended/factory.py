"""
Factory for creating suspended stocks data providers.
"""

from ..factory_base import BaseFactory
from .base import SuspendedProvider
from .eastmoney import EastmoneySuspendedProvider


class SuspendedFactory(BaseFactory[SuspendedProvider]):
    """Factory for suspended stocks data providers."""
    _providers: dict[str, type[SuspendedProvider]] = {
        "eastmoney": EastmoneySuspendedProvider,
    }
