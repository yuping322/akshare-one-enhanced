"""
Factory for creating board data providers.
"""

from ..factory_base import BaseFactory
from .base import BoardProvider
from .eastmoney import EastmoneyBoardProvider


class BoardFactory(BaseFactory[BoardProvider]):
    """Factory for board data providers."""
    _providers: dict[str, type[BoardProvider]] = {
        "eastmoney": EastmoneyBoardProvider,
    }
