"""
Factory for creating macro economic data providers.

This module implements the factory pattern for creating macro data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import MacroProvider
from .official import OfficialMacroProvider


class MacroFactory:
    """
    Factory class for creating macro economic data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[MacroProvider]] = {
        'official': OfficialMacroProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> MacroProvider:
        """
        Create a macro data provider instance.
        
        Args:
            source: Data source name ('official')
            **kwargs: Additional parameters for the provider
        
        Returns:
            MacroProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = MacroFactory.get_provider('official')
            >>> df = provider.get_lpr_rate('2024-01-01', '2024-12-31')
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
    def register_provider(cls, source: str, provider_class: Type[MacroProvider]) -> None:
        """
        Register a new macro data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from MacroProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of MacroProvider
        
        Example:
            >>> class CustomProvider(MacroProvider):
            ...     pass
            >>> MacroFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, MacroProvider):
            raise TypeError(
                f"Provider class must inherit from MacroProvider, "
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
            >>> sources = MacroFactory.list_sources()
            >>> print(sources)
            ['official']
        """
        return list(cls._providers.keys())
