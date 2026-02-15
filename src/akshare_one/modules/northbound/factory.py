"""
Factory for creating northbound capital data providers.

This module implements the factory pattern for creating northbound capital data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import NorthboundProvider
from .eastmoney import EastmoneyNorthboundProvider
from .sina import SinaNorthboundProvider


class NorthboundFactory:
    """
    Factory class for creating northbound capital data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[NorthboundProvider]] = {
        'eastmoney': EastmoneyNorthboundProvider,
        'sina': SinaNorthboundProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> NorthboundProvider:
        """
        Create a northbound capital data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            NorthboundProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = NorthboundFactory.get_provider('eastmoney')
            >>> df = provider.get_northbound_flow('2024-01-01', '2024-01-31', 'all')
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
    def register_provider(cls, source: str, provider_class: Type[NorthboundProvider]) -> None:
        """
        Register a new northbound capital data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from NorthboundProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of NorthboundProvider
        
        Example:
            >>> class CustomProvider(NorthboundProvider):
            ...     pass
            >>> NorthboundFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, NorthboundProvider):
            raise TypeError(
                f"Provider class must inherit from NorthboundProvider, "
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
            >>> sources = NorthboundFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
