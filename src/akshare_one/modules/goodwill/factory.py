"""
Factory for creating goodwill data providers.

This module implements the factory pattern for creating goodwill data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import GoodwillProvider
from .eastmoney import EastmoneyGoodwillProvider


class GoodwillFactory:
    """
    Factory class for creating goodwill data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[GoodwillProvider]] = {
        'eastmoney': EastmoneyGoodwillProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> GoodwillProvider:
        """
        Create a goodwill data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            GoodwillProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = GoodwillFactory.get_provider('eastmoney')
            >>> df = provider.get_goodwill_data('600000', '2024-01-01', '2024-12-31')
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
    def register_provider(cls, source: str, provider_class: Type[GoodwillProvider]) -> None:
        """
        Register a new goodwill data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from GoodwillProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of GoodwillProvider
        
        Example:
            >>> class CustomProvider(GoodwillProvider):
            ...     pass
            >>> GoodwillFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, GoodwillProvider):
            raise TypeError(
                f"Provider class must inherit from GoodwillProvider, "
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
            >>> sources = GoodwillFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
