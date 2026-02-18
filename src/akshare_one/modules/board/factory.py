"""
Factory for creating board data providers.
"""

from typing import Dict, Type

from .base import BoardProvider
from .eastmoney import EastmoneyBoardProvider


class BoardFactory:
    _providers: Dict[str, Type[BoardProvider]] = {
        "eastmoney": EastmoneyBoardProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> BoardProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
