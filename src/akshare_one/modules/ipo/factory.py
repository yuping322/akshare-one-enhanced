"""
Factory for creating IPO data providers.
"""

from typing import Dict, Type

from .base import IPOProvider
from .eastmoney import EastmoneyIPOProvider


class IPOFactory:
    _providers: Dict[str, Type[IPOProvider]] = {
        "eastmoney": EastmoneyIPOProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> IPOProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
