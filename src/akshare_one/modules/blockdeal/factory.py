"""
Factory for creating block deal data providers.

This module implements the factory pattern for creating block deal data providers
based on the specified data source.
"""

from typing import Dict, Type

from .base import BlockDealProvider
from .eastmoney import EastmoneyBlockDealProvider


class BlockDealFactory:
    """
    Factory class for creating block deal data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[BlockDealProvider]] = {
        'eastmoney': EastmoneyBlockDealProvider,
    }
    
    @classmethod
    def get_provider(cls, source: str, **kwargs) -> BlockDealProvider:
        """
        Create a block deal data provider instance.
        
        Args:
            source: Data source name ('eastmoney')
            **kwargs: Additional parameters for the provider
        
        Returns:
            BlockDealProvider: Provider instance
        
        Raises:
            ValueError: If the specified source is not supported
        """
        if source not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unsupported data source: {source}. "
                f"Available sources: {available}"
            )
        
        provider_class = cls._providers[source]
        return provider_class(**kwargs)
