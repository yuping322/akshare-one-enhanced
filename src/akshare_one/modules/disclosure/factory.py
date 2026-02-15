"""
Factory for creating disclosure data providers.

This module provides a factory class for creating disclosure data provider instances
based on the specified data source.
"""

from typing import Literal

from .base import DisclosureProvider
from .eastmoney import EastmoneyDisclosureProvider
from .sina import SinaDisclosureProvider


class DisclosureFactory:
    """
    Factory class for creating disclosure data providers.
    
    Supports multiple data sources and provides a unified interface
    for creating provider instances.
    """
    
    @staticmethod
    def get_provider(
        source: str = "eastmoney"
    ) -> DisclosureProvider:
        """
        Get a disclosure data provider instance.
        
        Args:
            source: Data source name ('eastmoney', 'sina')
        
        Returns:
            DisclosureProvider: Provider instance for the specified source
        
        Raises:
            ValueError: If the specified source is not supported
        
        Example:
            >>> provider = DisclosureFactory.get_provider(source='eastmoney')
            >>> df = provider.get_dividend_data('600000', '2024-01-01', '2024-12-31')
        """
        providers = {
            'eastmoney': EastmoneyDisclosureProvider,
            'sina': SinaDisclosureProvider,
        }
        
        if source not in providers:
            raise ValueError(
                f"Unsupported data source: {source}. "
                f"Available sources: {', '.join(providers.keys())}"
            )
        
        return providers[source]()
    
    @staticmethod
    def get_available_sources() -> list[str]:
        """
        Get list of available data sources.
    
        Returns:
            list[str]: List of available source names
        """
        return ['eastmoney', 'sina']
