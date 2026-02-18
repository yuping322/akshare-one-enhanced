"""
Factory for creating ST stocks data providers.
"""

from typing import Dict, Type

from .base import STProvider
from .eastmoney import EastmoneySTProvider


class STFactory:
    _providers: Dict[str, Type[STProvider]] = {
        "eastmoney": EastmoneySTProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> STProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
