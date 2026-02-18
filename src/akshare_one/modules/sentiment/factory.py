"""
Factory for creating sentiment data providers.
"""

from ..factory_base import BaseFactory
from .base import SentimentProvider
from .eastmoney import EastmoneySentimentProvider


class SentimentFactory(BaseFactory[SentimentProvider]):
    """Factory class for creating sentiment data providers."""

    _providers: dict[str, type[SentimentProvider]] = {
        "eastmoney": EastmoneySentimentProvider,
    }
