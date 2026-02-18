"""
Factory for creating HK/US stock data providers.
"""


from .base import HKUSProvider
from .eastmoney import EastmoneyHKUSProvider


class HKUSFactory:
    _providers: dict[str, type[HKUSProvider]] = {
        "eastmoney": EastmoneyHKUSProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> HKUSProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def register_provider(cls, source: str, provider_class: type[HKUSProvider]) -> None:
        if not issubclass(provider_class, HKUSProvider):
            raise TypeError("Provider must inherit from HKUSProvider")
        cls._providers[source] = provider_class

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
