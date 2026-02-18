"""
Factory for creating valuation data providers.

This module implements the factory pattern for creating valuation data providers
based on the specified data source.
"""

from ..factory_base import BaseFactory
from .base import ValuationProvider
from .eastmoney import EastmoneyValuationProvider
from .legu import LeguValuationProvider


class ValuationFactory(BaseFactory[ValuationProvider]):
    """
    Factory class for creating valuation data providers.

    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """

    _providers: dict[str, type[ValuationProvider]] = {
        "eastmoney": EastmoneyValuationProvider,
        "legu": LeguValuationProvider,
    }
