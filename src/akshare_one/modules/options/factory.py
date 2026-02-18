"""
Factory for creating options data providers.
"""


from ..factory_base import BaseFactory
from .base import OptionsDataProvider
from .eastmoney import EastmoneyOptionsProvider
from .sina import SinaOptionsProvider


class OptionsDataFactory(BaseFactory[OptionsDataProvider]):
    """Factory class for creating options data providers."""

    _providers: dict[str, type[OptionsDataProvider]] = {
        "sina": SinaOptionsProvider,
        "eastmoney": EastmoneyOptionsProvider,
    }
