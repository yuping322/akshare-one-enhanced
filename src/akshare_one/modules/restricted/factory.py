"""
Factory for creating restricted stock release data providers.

This module implements the factory pattern for creating restricted release data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import RestrictedReleaseProvider
from .eastmoney import EastmoneyRestrictedReleaseProvider


class RestrictedReleaseFactory:
    """
    Factory class for creating restricted stock release data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[RestrictedReleaseProvider]] = {
        'eastmoney': EastmoneyRestrictedReleaseProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> RestrictedReleaseProvider:
        """
        Create a restricted release data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            RestrictedReleaseProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = RestrictedReleaseFactory.get_provider('eastmoney')
            >>> df = provider.get_restricted_release('600000', '2024-01-01', '2024-12-31')
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
    def register_provider(cls, source: str, provider_class: Type[RestrictedReleaseProvider]) -> None:
        """
        Register a new restricted release data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from RestrictedReleaseProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of RestrictedReleaseProvider
        
        Example:
            >>> class CustomProvider(RestrictedReleaseProvider):
            ...     pass
            >>> RestrictedReleaseFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, RestrictedReleaseProvider):
            raise TypeError(
                f"Provider class must inherit from RestrictedReleaseProvider, "
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
            >>> sources = RestrictedReleaseFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
