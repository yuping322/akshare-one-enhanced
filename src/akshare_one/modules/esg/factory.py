"""
Factory for creating ESG rating data providers.

This module implements the factory pattern for creating ESG rating data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import ESGProvider
from .eastmoney import EastmoneyESGProvider
from .sina import SinaESGProvider


class ESGFactory:
    """
    Factory class for creating ESG rating data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[ESGProvider]] = {
        'eastmoney': EastmoneyESGProvider,
        'sina': SinaESGProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> ESGProvider:
        """
        Create an ESG rating data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            ESGProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = ESGFactory.get_provider('eastmoney')
            >>> df = provider.get_esg_rating('600000', '2024-01-01', '2024-12-31')
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
    def register_provider(cls, source: str, provider_class: Type[ESGProvider]) -> None:
        """
        Register a new ESG rating data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from ESGProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of ESGProvider
        
        Example:
            >>> class CustomProvider(ESGProvider):
            ...     pass
            >>> ESGFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, ESGProvider):
            raise TypeError(
                f"Provider class must inherit from ESGProvider, "
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
            >>> sources = ESGFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
