"""
Factory for creating industry sector data providers.
"""


from .base import IndustryProvider
from .eastmoney import EastmoneyIndustryProvider


class IndustryFactory:
    _providers: dict[str, type[IndustryProvider]] = {
        "eastmoney": EastmoneyIndustryProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> IndustryProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def register_provider(cls, source: str, provider_class: type[IndustryProvider]) -> None:
        if not issubclass(provider_class, IndustryProvider):
            raise TypeError("Provider must inherit from IndustryProvider")
        cls._providers[source] = provider_class

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
