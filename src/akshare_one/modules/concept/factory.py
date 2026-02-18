"""
Factory for creating concept sector data providers.
"""


from .base import ConceptProvider
from .eastmoney import EastmoneyConceptProvider


class ConceptFactory:
    _providers: dict[str, type[ConceptProvider]] = {
        "eastmoney": EastmoneyConceptProvider,
    }

    @classmethod
    def get_provider(cls, source: str = "eastmoney", **kwargs) -> ConceptProvider:
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._providers[source](**kwargs)

    @classmethod
    def register_provider(cls, source: str, provider_class: type[ConceptProvider]) -> None:
        if not issubclass(provider_class, ConceptProvider):
            raise TypeError("Provider must inherit from ConceptProvider")
        cls._providers[source] = provider_class

    @classmethod
    def list_sources(cls) -> list:
        return list(cls._providers.keys())
