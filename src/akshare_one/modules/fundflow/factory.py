"""
Factory for creating fund flow data providers.

This module implements the factory pattern for creating fund flow data providers
based on the specified data source.
"""

from ..factory_base import BaseFactory
from .base import FundFlowProvider
from .eastmoney import EastmoneyFundFlowProvider
from .sina import SinaFundFlowProvider


class FundFlowFactory(BaseFactory[FundFlowProvider]):
    """
    Factory class for creating fund flow data providers.

    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """

    _providers: dict[str, type[FundFlowProvider]] = {
        "eastmoney": EastmoneyFundFlowProvider,
        "sina": SinaFundFlowProvider,
    }
