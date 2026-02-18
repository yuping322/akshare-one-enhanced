"""
Factory for creating block deal data providers.
"""

from ..factory_base import BaseFactory
from .base import BlockDealProvider
from .eastmoney import EastmoneyBlockDealProvider
from .sina import SinaBlockDealProvider


class BlockDealFactory(BaseFactory[BlockDealProvider]):
    """Factory class for creating block deal data providers."""

    _providers: dict[str, type[BlockDealProvider]] = {
        "eastmoney": EastmoneyBlockDealProvider,
        "sina": SinaBlockDealProvider,
    }
