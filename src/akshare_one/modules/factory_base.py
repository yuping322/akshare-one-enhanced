"""
Base factory class for creating data providers.

This module provides a generic factory base class that implements
the common factory pattern used across all data provider modules.
"""

from typing import Any, Generic, TypeVar, Callable
from functools import wraps

from .exceptions import InvalidParameterError

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


def api_endpoint(factory_cls: type["BaseFactory"]) -> Callable:
    """
    装饰器：自动处理 Factory 调用逻辑。
    将函数名作为 method_name 传递给 Factory.call_provider_method。
    """

    def decorator(func: Callable) -> Callable:
        # 先应用文档补全
        decorated_func = doc_params(func)

        @wraps(decorated_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return factory_cls.call_provider_method(func.__name__, *args, **kwargs)

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
    def create(cls, name: str, providers: dict[str, type[T]] | None = None) -> type["BaseFactory[T]"]:
        """
        创建一个子 Factory 类。
        """
        return type(f"{name}Factory", (cls,), {"_providers": providers or {}})

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
            raise InvalidParameterError(f"Unsupported data source: '{source}'. Available sources: {available}")

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
        from .multi_source import MultiSourceRouter

        if sources is None:
            sources = cls.list_sources()

        providers = []
        for s in sources:
            try:
                providers.append((s, cls.get_provider(s, **kwargs)))
            except Exception:
                continue

        return MultiSourceRouter(providers)

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
        """
        from ..client import apply_data_filter

        if isinstance(source, str):
            # Single source
            # Extract common constructor parameters if they exist in kwargs
            # For now, just pass all kwargs to get_provider as well
            # Providers should be tolerant of extra kwargs in __init__ if needed,
            # or we can be more selective.
            provider = cls.get_provider(source=source, **kwargs)
            method = getattr(provider, method_name)
            df = method(*args, **kwargs)
        else:
            # Multi-source router (source is None or list)
            router = cls.create_router(sources=source, **kwargs)
            df = router.execute(method_name, *args, **kwargs)

        return apply_data_filter(df, columns, row_filter)
