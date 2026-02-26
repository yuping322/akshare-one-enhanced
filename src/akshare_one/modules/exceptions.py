"""
Exception classes for market data operations.

This module defines a comprehensive exception hierarchy for handling
various error scenarios in market data fetching and processing.
"""


class MarketDataError(Exception):
    """
    Base exception class for all market data related errors.

    This is the root exception that all other market data exceptions inherit from.
    Use this for catching any market data related error.

    Example:
        try:
            data = provider.fetch_data()
        except MarketDataError as e:
            logger.error(f"Market data error: {e}")
    """

    pass


class InvalidParameterError(MarketDataError):
    r"""
    Exception raised when invalid parameters are provided to a data provider.

    This includes:
    - Invalid symbol format (e.g., not 6 digits)
    - Invalid date format (e.g., not YYYY-MM-DD)
    - Invalid date range (start_date > end_date)
    - Invalid enum values (e.g., invalid market type)
    - Out of range values (e.g., negative top_n)

    Example:
        if not re.match(r'^\d{6}$', symbol):
            raise InvalidParameterError(f"Invalid symbol format: {symbol}")
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
            raise DataSourceUnavailableError(f"Failed to reach {url}: {e}")
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
            raise NoDataError(f"No data available for symbol {symbol}")
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
                f"Missing expected columns: {missing}. "
                f"Upstream API may have changed."
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
                f"Rate limit exceeded. Retry after {retry_after} seconds."
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
            raise DataValidationError("Close price cannot be negative")
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
