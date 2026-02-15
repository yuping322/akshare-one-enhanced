"""
Factory for creating margin financing data providers.

This module implements the factory pattern for creating margin financing data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import MarginProvider
from .eastmoney import EastmoneyMarginProvider
from .sina import SinaMarginProvider


class MarginFactory:
    """
    Factory class for creating margin financing data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[MarginProvider]] = {
        'eastmoney': EastmoneyMarginProvider,
        'sina': SinaMarginProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> MarginProvider:
        """
        Create a margin financing data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            MarginProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = MarginFactory.get_provider('eastmoney')
            >>> df = provider.get_margin_data('600000', '2024-01-01', '2024-01-31')
        """
        if source not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unsupported data source: {source}. "
                f"Available sources: {available}"
            )
        
        provider_class = cls._providers[source]
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, source: str, provider_class: Type[MarginProvider]) -> None:
        """
        Register a new margin financing data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from MarginProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of MarginProvider
        
        Example:
            >>> class CustomProvider(MarginProvider):
            ...     pass
            >>> MarginFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, MarginProvider):
            raise TypeError(
                f"Provider class must inherit from MarginProvider, "
                f"got {provider_class.__name__}"
            )
        
        cls._providers[source] = provider_class
    
    @classmethod
    def list_sources(cls) -> list:
        """
        List all available data sources.
        
        Returns:
            list: List of available source names
        
        Example:
            >>> sources = MarginFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
