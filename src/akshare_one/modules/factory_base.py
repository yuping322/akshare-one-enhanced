"""
Base factory class for creating data providers.

This module provides a generic factory base class that implements
the common factory pattern used across all data provider modules.
"""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, Generic, TypeVar

import pandas as pd

from .exceptions import InvalidParameterError, MarketDataError, map_to_standard_exception

T = TypeVar("T")


def doc_params(func: Callable) -> Callable:
    """
    装饰器：自动在函数文档字符串末尾追加标准参数说明。
    """
    standard_params_doc = """
    Args (Standard):
        source: Data source name, list of names, or None for auto-selection.
        columns: List of columns to return in the result.
        row_filter: Row filter configuration dictionary.
    """
    if func.__doc__:
        func.__doc__ = func.__doc__.rstrip() + "\n" + standard_params_doc
    else:
        func.__doc__ = standard_params_doc
    return func


def api_endpoint(factory_cls: type["BaseFactory"], method_name: str | None = None) -> Callable:
    """
    装饰器：自动处理 Factory 调用逻辑。
    将函数名作为 method_name 传递给 Factory.call_provider_method，除非指定了 method_name。

    Args:
        factory_cls: Factory 类
        method_name: 可选的显式方法名，如果为 None 则使用 func.__name__
    """

    def decorator(func: Callable) -> Callable:
        # 先应用文档补全
        decorated_func = doc_params(func)
        sig = inspect.signature(func)

        @wraps(decorated_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Bind arguments and fill in defaults
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            params = bound_args.arguments.copy()

            # Extract standard parameters for call_provider_method
            source = params.pop("source", None)
            columns = params.pop("columns", None)
            row_filter = params.pop("row_filter", None)

            # Use explicit method_name if provided, otherwise use func.__name__
            effective_method_name = method_name if method_name is not None else func.__name__

            try:
                return factory_cls.call_provider_method(
                    effective_method_name,
                    source=source,
                    columns=columns,
                    row_filter=row_filter,
                    **params,
                )
            except MarketDataError as e:
                # Map internal exception to standard exception for public API
                context = {
                    "source": source if isinstance(source, str) else None,
                    "endpoint": effective_method_name,
                }
                # Add any symbol/context from params
                if "symbol" in params:
                    context["symbol"] = kwargs["symbol"]

                raise map_to_standard_exception(e, context)

        return wrapper

    return decorator


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
    def register(cls, source: str) -> Callable:
        """
        装饰器：注册一个新的 Provider。
        """

        def decorator(provider_cls: type[T]) -> type[T]:
            cls._providers[source] = provider_cls
            return provider_cls

        return decorator

    @classmethod
    def create(cls, source: str, **kwargs) -> T:
        """
        Create a provider instance for the specified data source.

        This is a convenience method that combines factory class creation
        with provider instantiation in one call.

        Args:
            source: Data source name (e.g., 'eastmoney', 'sina')
            **kwargs: Additional parameters passed to the provider constructor

        Returns:
            Provider instance

        Example:
            >>> provider = FundFlowFactory.create('eastmoney', symbol='600000')
        """
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            internal_error = InvalidParameterError(
                f"Unsupported data source: '{source}'. Available sources: {available}"
            )
            raise map_to_standard_exception(internal_error, {"source": source})

        provider_class = cls._providers[source]
        return provider_class(**kwargs)

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
            ValueError: If the specified source is not supported (mapped from InvalidParameterError)

        Example:
            >>> provider = FundFlowFactory.get_provider('eastmoney', symbol='600000')
        """
        if source not in cls._providers:
            available = ", ".join(cls._providers.keys())
            internal_error = InvalidParameterError(
                f"Unsupported data source: '{source}'. Available sources: {available}"
            )
            # Map to ValueError for external callers
            raise map_to_standard_exception(internal_error, {"source": source})

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

        Raises:
            TypeError: If provider_class doesn't inherit from the expected base class

        Example:
            >>> class CustomProvider(FundFlowProvider):
            ...     pass
            >>> FundFlowFactory.register_provider('custom', CustomProvider)
        """
        # Validate that provider_class is a proper class
        if not inspect.isclass(provider_class):
            raise TypeError(f"Provider must be a class, got {type(provider_class)}")

        # Validate inheritance by checking against existing registered providers
        # If factory has existing providers, find the base class and validate
        if cls._providers:
            # Get a sample provider to determine the base class
            sample_provider_cls = next(iter(cls._providers.values()))

            # Find the specific provider base class (e.g., NorthboundProvider, FundFlowProvider)
            # by looking at the sample provider's MRO
            base_provider_class = None
            for parent in sample_provider_cls.__mro__:
                # Skip the sample class itself and generic base classes
                if parent is sample_provider_cls:
                    continue
                # Find the first class ending with "Provider" (the specific base)
                if parent.__name__.endswith("Provider"):
                    base_provider_class = parent
                    break

            # If we found a base class, validate inheritance
            if base_provider_class:
                if not issubclass(provider_class, base_provider_class):
                    raise TypeError(f"Provider class must inherit from {base_provider_class.__name__}")

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
    def get_available_sources(cls) -> list[str]:
        """
        Alias for list_sources() for backward compatibility.

        Returns:
            List of available source names

        Example:
            >>> sources = FundFlowFactory.get_available_sources()
            >>> print(sources)
            ['eastmoney', 'sina']
        """
        return cls.list_sources()

    @classmethod
    def has_source(cls, source: str) -> bool:
        """
        Check if a data source is supported.

        Args:
            source: Data source name

        Returns:
            True if supported, False otherwise
        """
        return source in cls._providers

    @classmethod
    def create_router(cls, sources: list[str] | None = None, **kwargs) -> Any:
        """
        Create a MultiSourceRouter for the specified sources.

        Args:
            sources: List of source names. If None, all available sources are used.
            **kwargs: Additional parameters passed to the provider constructors

        Returns:
            MultiSourceRouter instance
        """
        from .multi_source import EmptyDataPolicy, MultiSourceRouter

        if sources is None:
            sources = cls.list_sources()

        providers = []
        for s in sources:
            try:
                providers.append((s, cls.get_provider(s, **kwargs)))
            except Exception:
                continue

        return MultiSourceRouter(providers, empty_data_policy=EmptyDataPolicy.RELAXED)

    @classmethod
    def call_provider_method(
        cls,
        method_name: str,
        *args: Any,
        source: str | list[str] | None = None,
        columns: list[str] | None = None,
        row_filter: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Call a method on one or more providers with automatic routing and filtering.

        This centralizes the logic for:
        1. Selecting the source (single or list)
        2. Routing the request through MultiSourceRouter if needed
        3. Applying data filters (columns and row filters)

        Args:
            method_name: Name of the method to call on the provider(s)
            *args: Positional arguments for the provider method
            source: Single source name, list of source names, or None for all available
            columns: List of columns to keep in the result
            row_filter: Dictionary of row filtering rules
            **kwargs: Keyword arguments for the provider method

        Returns:
            pd.DataFrame: Standardized and filtered result

        Raises:
            ValueError: If source is invalid or parameters are invalid (mapped from InvalidParameterError)
            KeyError: If upstream data structure changed (mapped from UpstreamChangedError)
            ConnectionError: If data source is unavailable (mapped from DataSourceUnavailableError)
        """
        from ..client import apply_data_filter

        try:
            if isinstance(source, str):
                # Single source
                # Extract common constructor parameters if they exist in kwargs
                # row_filter and columns are for apply_data_filter, not for provider __init__
                provider_kwargs = {k: v for k, v in kwargs.items() if k not in ("row_filter", "columns")}
                provider = cls.get_provider(source=source, **provider_kwargs)
                method = getattr(provider, method_name)
                df = method(*args, **kwargs)
            else:
                # Multi-source router (source is None or list)
                router = cls.create_router(sources=source, **kwargs)
                df = router.execute(method_name, *args, **kwargs)

            return apply_data_filter(df, columns, row_filter)

        except MarketDataError as e:
            # Map internal exception to standard exception for public API
            context = {
                "source": source if isinstance(source, str) else None,
                "endpoint": method_name,
            }
            # Add any symbol/context from kwargs
            if "symbol" in kwargs:
                context["symbol"] = kwargs["symbol"]

            raise map_to_standard_exception(e, context)
