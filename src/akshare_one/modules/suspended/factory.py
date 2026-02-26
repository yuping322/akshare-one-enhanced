"""
Factory for creating suspended stocks data providers.
"""

from .base import SuspendedProvider
from .eastmoney import EastmoneySuspendedProvider


class SuspendedFactory:
    _providers: dict[str, type[SuspendedProvider]] = {
        "eastmoney": EastmoneySuspendedProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> SuspendedProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
