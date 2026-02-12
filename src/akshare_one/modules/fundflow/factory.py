"""
Factory for creating fund flow data providers.

This module implements the factory pattern for creating fund flow data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import FundFlowProvider
from .eastmoney import EastmoneyFundFlowProvider


class FundFlowFactory:
    """
    Factory class for creating fund flow data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[FundFlowProvider]] = {
        'eastmoney': EastmoneyFundFlowProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> FundFlowProvider:
        """
        Create a fund flow data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            FundFlowProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = FundFlowFactory.get_provider('eastmoney')
            >>> df = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
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
    def register_provider(cls, source: str, provider_class: Type[FundFlowProvider]) -> None:
        """
        Register a new fund flow data provider.
        
        This allows extending the factory with custom providers.
        
        Args:
            source: Data source name
            provider_class: Provider class (must inherit from FundFlowProvider)
        
        Raises:
            TypeError: If provider_class is not a subclass of FundFlowProvider
        
        Example:
            >>> class CustomProvider(FundFlowProvider):
            ...     pass
            >>> FundFlowFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, FundFlowProvider):
            raise TypeError(
                f"Provider class must inherit from FundFlowProvider, "
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
            >>> sources = FundFlowFactory.list_sources()
            >>> print(sources)
            ['eastmoney']
        """
        return list(cls._providers.keys())
