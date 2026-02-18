"""
Base factory class for creating data providers.

This module provides a generic factory base class that implements
the common factory pattern used across all data provider modules.
"""

from typing import Generic, TypeVar

from .exceptions import InvalidParameterError

T = TypeVar("T")


class BaseFactory(Generic[T]):
    """
    Generic factory base class for creating data providers.

    This class provides a unified interface for:
    - Creating provider instances by source name
    - Registering new providers
    - Listing available sources

    Subclasses only need to define the _providers class variable
    with the appropriate provider classes.

    Example:
        >>> class MyProvider:
        ...     pass
        >>> class MyFactory(BaseFactory[MyProvider]):
        ...     _providers = {"eastmoney": MyProvider}
        >>> provider = MyFactory.get_provider("eastmoney")
    """

    _providers: dict[str, type[T]] = {}

    @classmethod
    def get_provider(cls, source: str, **kwargs) -> T:
        """
        Create a provider instance for the specified data source.

        Args:
            source: Data source name (e.g., 'eastmoney', 'sina')
            **kwargs: Additional parameters passed to the provider constructor

        Returns:
            Provider instance

        Raises:
            InvalidParameterError: If the specified source is not supported

        Example:
            >>> provider = FundFlowFactory.get_provider('eastmoney', symbol='600000')
        """
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise InvalidParameterError(
                f"Unsupported data source: '{source}'. Available sources: {available}"
            )

        provider_class = cls._providers[source]
        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, source: str, provider_class: type[T]) -> None:
        """
        Register a new provider for a data source.

        This allows extending the factory with custom providers at runtime.

        Args:
            source: Data source name
            provider_class: Provider class (must be compatible with the factory's type)

        Example:
            >>> class CustomProvider(FundFlowProvider):
            ...     pass
            >>> FundFlowFactory.register_provider('custom', CustomProvider)
        """
        cls._providers[source] = provider_class

    @classmethod
    def list_sources(cls) -> list[str]:
        """
        List all available data sources.

        Returns:
            List of available source names

        Example:
            >>> sources = FundFlowFactory.list_sources()
            >>> print(sources)
            ['eastmoney', 'sina']
        """
        return list(cls._providers.keys())

    @classmethod
    def has_source(cls, source: str) -> bool:
        """
        Check if a data source is supported.

        Args:
            source: Data source name

        Returns:
            True if the source is supported, False otherwise
        """
        return source in cls._providers
