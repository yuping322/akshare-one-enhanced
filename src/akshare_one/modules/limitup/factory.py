"""
Factory for creating limit up/down data providers.

This module implements the factory pattern for creating limit up/down data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import LimitUpDownProvider
from .eastmoney import EastmoneyLimitUpDownProvider


class LimitUpDownFactory:
    """
    Factory class for creating limit up/down data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[LimitUpDownProvider]] = {
        'eastmoney': EastmoneyLimitUpDownProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> LimitUpDownProvider:
        """
        Create a limit up/down data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            LimitUpDownProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = LimitUpDownFactory.get_provider('eastmoney')
            >>> df = provider.get_limit_up_pool('2024-01-01')
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
    def register_provider(cls, source: str, provider_class: Type[LimitUpDownProvider]) -> None:
        """
        Register a new limit up/down data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from LimitUpDownProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of LimitUpDownProvider
        
        Example:
            >>> class CustomProvider(LimitUpDownProvider):
            ...     pass
            >>> LimitUpDownFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, LimitUpDownProvider):
            raise TypeError(
                f"Provider class must inherit from LimitUpDownProvider, "
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
            >>> sources = LimitUpDownFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
