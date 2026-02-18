"""
Factory for creating restricted stock release data providers.
"""

from ..factory_base import BaseFactory
from .base import RestrictedReleaseProvider
from .eastmoney import EastmoneyRestrictedReleaseProvider


class RestrictedReleaseFactory(BaseFactory[RestrictedReleaseProvider]):
    """Factory class for creating restricted stock release data providers."""

    _providers: dict[str, type[RestrictedReleaseProvider]] = {
        "eastmoney": EastmoneyRestrictedReleaseProvider,
    }
