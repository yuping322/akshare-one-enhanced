"""
Exception classes for market data operations.

This module defines a comprehensive exception hierarchy for handling
various error scenarios in market data fetching and processing.
"""

from typing import Any

from ...error_codes import ErrorCode


class MarketDataError(Exception):
    """
    Base exception class for all market data related errors.

    This is the root exception that all other market data exceptions inherit from.
    Use this for catching any market data related error.

    Args:
        message: Error message
        error_code: Error code from ErrorCode enum
        context: Additional context (source, endpoint, symbol, etc.)

    Example:
        try:
            data = provider.fetch_data()
        except MarketDataError as e:
            logger.error(f"[{e.error_code}] Market data error: {e}")
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def __str__(self) -> str:
        """Return error message with error code."""
        if self.error_code:
            return f"[{self.error_code.value}] {self.message}"
        return self.message


class InvalidParameterError(MarketDataError, ValueError):
    r"""
    Exception raised when invalid parameters are provided to a data provider.

    This exception inherits from both MarketDataError and ValueError to maintain
    compatibility with tests that expect ValueError while providing rich error context.

    This includes:
    - Invalid symbol format (e.g., not 6 digits)
    - Invalid date format (e.g., not YYYY-MM-DD)
    - Invalid date range (start_date > end_date)
    - Invalid enum values (e.g., invalid market type)
    - Out of range values (e.g., negative top_n)

    Example:
        if not re.match(r'^\d{6}$', symbol):
            raise InvalidParameterError(
                f"Invalid symbol format: {symbol}",
                error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
                context={"symbol": symbol}
            )
    """

    pass


class DataSourceUnavailableError(MarketDataError):
    """
    Exception raised when a data source is unavailable or unreachable.

    This includes:
    - Network timeout
    - HTTP errors (4xx, 5xx)
    - DNS resolution failures
    - Connection refused
    - SSL/TLS errors

    The upper layer (View Service) can use this to trigger data source switching
    or return UPSTREAM_TIMEOUT status.

    Example:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise DataSourceUnavailableError(
                f"Failed to reach {url}: {e}",
                error_code=ErrorCode.SOURCE_UNAVAILABLE,
                context={"url": url}
            )
    """

    pass


class NoDataError(MarketDataError):
    """
    Exception raised when no data is returned from the data source.

    This is different from an empty result - it indicates that the data source
    returned an unexpected empty response or explicitly indicated no data is available.

    Note: Providers should typically return an empty DataFrame with proper column
    structure instead of raising this exception. This exception is for cases where
    the data source explicitly signals "no data available" vs. "empty result set".

    Example:
        if response.json().get('error') == 'NO_DATA':
            raise NoDataError(
                f"No data available for symbol {symbol}",
                error_code=ErrorCode.SOURCE_NO_DATA,
                context={"symbol": symbol}
            )
    """

    pass


class UpstreamChangedError(MarketDataError):
    """
    Exception raised when upstream data source structure has changed.

    This includes:
    - Missing expected fields in response
    - Changed field names
    - Changed data types
    - Changed response format (e.g., JSON to XML)

    This exception helps detect when the upstream API has been modified and
    the provider code needs to be updated. Contract tests should catch these
    issues early.

    The upper layer (View Service) can return UPSTREAM_CHANGED warning when
    this exception is caught.

    Example:
        expected_columns = ['date', 'symbol', 'close']
        if not all(col in df.columns for col in expected_columns):
            missing = set(expected_columns) - set(df.columns)
            raise UpstreamChangedError(
                f"Missing expected columns: {missing}. Upstream API may have changed.",
                error_code=ErrorCode.SOURCE_SCHEMA_CHANGED,
                context={"expected_columns": expected_columns, "actual_columns": list(df.columns)}
            )
    """

    pass


class RateLimitError(MarketDataError):
    """
    Exception raised when API rate limit is exceeded.

    This indicates that the data source has throttled requests due to
    exceeding rate limits. The provider should implement retry logic
    with exponential backoff.

    The upper layer (View Service) can return RATE_LIMITED status and
    serve stale cache if available.

    Example:
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_after} seconds.",
                error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                context={"retry_after": retry_after}
            )
    """

    pass


class DataValidationError(MarketDataError):
    """
    Exception raised when data validation fails.

    This includes:
    - Data type mismatches
    - Out of range values
    - Invalid data combinations
    - Failed integrity checks

    Example:
        if df['close'].min() < 0:
            raise DataValidationError(
                "Close price cannot be negative",
                error_code=ErrorCode.VALIDATION_VALUE_ERROR,
                context={"field": "close", "min_value": float(df['close'].min())}
            )
    """

    pass


# Convenience function for error handling
def handle_upstream_error(error: Exception, source: str) -> MarketDataError:
    """
    Convert common upstream errors to appropriate MarketDataError subclasses.

    This helper function standardizes error handling across different providers.

    Args:
        error: The original exception from upstream
        source: Name of the data source (for error messages)

    Returns:
        MarketDataError: Appropriate MarketDataError subclass

    Example:
        try:
            response = requests.get(url)
        except Exception as e:
            raise handle_upstream_error(e, 'eastmoney')
    """
    import requests

    if isinstance(error, requests.Timeout):
        return DataSourceUnavailableError(f"Timeout connecting to {source}: {error}")
    elif isinstance(error, requests.ConnectionError):
        return DataSourceUnavailableError(f"Connection error to {source}: {error}")
    elif isinstance(error, requests.HTTPError):
        if error.response.status_code == 429:
            return RateLimitError(f"Rate limit exceeded for {source}: {error}")
        elif 400 <= error.response.status_code < 500:
            return InvalidParameterError(f"Client error from {source}: {error}")
        else:
            return DataSourceUnavailableError(f"Server error from {source}: {error}")
    elif isinstance(error, (KeyError, AttributeError)):
        return UpstreamChangedError(f"Unexpected data structure from {source}: {error}")
    else:
        return MarketDataError(f"Unexpected error from {source}: {error}")


def map_to_standard_exception(error: MarketDataError, context: dict | None = None) -> Exception:
    """
    Map internal MarketDataError to standard Python exceptions for public API.

    This function provides a unified exception contract for external callers:
    - InvalidParameterError -> ValueError
    - UpstreamChangedError -> KeyError
    - DataSourceUnavailableError -> ConnectionError
    - RateLimitError -> RuntimeError
    - NoDataError -> ValueError
    - DataValidationError -> ValueError
    - MarketDataError (generic) -> RuntimeError

    The mapped exception preserves the original error message, error code, and
    adds context information (source, endpoint, symbol) for better debugging.

    Args:
        error: Internal MarketDataError exception
        context: Optional context dict with 'source', 'endpoint', 'symbol' etc.

    Returns:
        Exception: Standard Python exception (ValueError, KeyError, etc.) with error_code attribute

    Example:
        >>> try:
        ...     provider.validate_symbol("ABC")
        ... except InvalidParameterError as e:
        ...     raise map_to_standard_exception(e, {"source": "eastmoney"})
        >>> # External caller catches ValueError
    """
    # Build enhanced error message with context
    base_message = error.message  # Use original message without error code

    # Merge error context with provided context
    merged_context = {**error.context}
    if context:
        merged_context.update(context)

    if merged_context:
        context_parts = []
        if "source" in merged_context:
            context_parts.append(f"source={merged_context['source']}")
        if "endpoint" in merged_context:
            context_parts.append(f"endpoint={merged_context['endpoint']}")
        if "symbol" in merged_context:
            context_parts.append(f"symbol={merged_context['symbol']}")

        if context_parts:
            enhanced_message = f"{base_message} (context: {', '.join(context_parts)})"
        else:
            enhanced_message = base_message
    else:
        enhanced_message = base_message

    # Map to standard exception types
    standard_exception: Exception
    if isinstance(error, InvalidParameterError):
        standard_exception = ValueError(enhanced_message)
    elif isinstance(error, UpstreamChangedError):
        standard_exception = KeyError(enhanced_message)
    elif isinstance(error, DataSourceUnavailableError):
        # ConnectionError is more specific for network issues
        standard_exception = ConnectionError(enhanced_message)
    elif isinstance(error, RateLimitError):
        standard_exception = RuntimeError(enhanced_message)
    elif isinstance(error, NoDataError) or isinstance(error, DataValidationError):
        standard_exception = ValueError(enhanced_message)
    else:
        # Generic MarketDataError or unknown subclass
        standard_exception = RuntimeError(enhanced_message)

    # Attach error code and context to standard exception
    standard_exception.error_code = error.error_code  # type: ignore[attr-defined]
    standard_exception.context = merged_context  # type: ignore[attr-defined]

    return standard_exception


def raise_mapped_exception(error: MarketDataError, context: dict | None = None) -> None:
    """
    Raise a mapped standard exception while preserving internal error for logging.

    This is a convenience function that maps and raises the exception.
    Use this in public API boundaries to ensure external callers see standard exceptions.

    Args:
        error: Internal MarketDataError exception
        context: Optional context dict with 'source', 'endpoint', 'symbol' etc.

    Raises:
        Exception: Standard Python exception mapped from the internal error

    Example:
        >>> try:
        ...     # Internal validation that raises InvalidParameterError
        ...     validate_symbol_internal(symbol)
        ... except InvalidParameterError as e:
        ...     # Log the detailed internal error
        ...     logger.error(f"Internal error: {e}")
        ...     # Raise standard exception for external callers
        ...     raise_mapped_exception(e, {"source": "eastmoney", "symbol": symbol})
    """
    raise map_to_standard_exception(error, context)
