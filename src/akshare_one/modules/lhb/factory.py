"""
Factory for creating dragon tiger list data providers.

This module implements the factory pattern for creating dragon tiger list data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import DragonTigerProvider
from .eastmoney import EastmoneyDragonTigerProvider


class DragonTigerFactory:
    """
    Factory class for creating dragon tiger list data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[DragonTigerProvider]] = {
        'eastmoney': EastmoneyDragonTigerProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> DragonTigerProvider:
        """
        Create a dragon tiger list data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            DragonTigerProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = DragonTigerFactory.get_provider('eastmoney')
            >>> df = provider.get_dragon_tiger_list('2024-01-01')
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
    def register_provider(cls, source: str, provider_class: Type[DragonTigerProvider]) -> None:
        """
        Register a new dragon tiger list data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from DragonTigerProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of DragonTigerProvider
        
        Example:
            >>> class CustomProvider(DragonTigerProvider):
            ...     pass
            >>> DragonTigerFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, DragonTigerProvider):
            raise TypeError(
                f"Provider class must inherit from DragonTigerProvider, "
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
            >>> sources = DragonTigerFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
