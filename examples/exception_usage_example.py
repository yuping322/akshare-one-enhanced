"""
Example demonstrating the usage of market data exceptions.

This example shows how to use the exception hierarchy in real-world scenarios.
"""

import pandas as pd
from akshare_one.modules import (
    BaseProvider,
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
    UpstreamChangedError,
    handle_upstream_error,
)


class ExampleProvider(BaseProvider):
    """Example provider demonstrating exception usage."""

    def get_source_name(self) -> str:
        return "example"

    def get_data_type(self) -> str:
        return "demo"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch data with proper error handling."""
        # This would normally call an external API
        return pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '600001'],
            'close': [10.0, 11.0]
        })


def example_parameter_validation():
    """Example 1: Parameter validation with InvalidParameterError."""
    print("Example 1: Parameter Validation")
    print("-" * 50)

    def get_stock_data(symbol: str, start_date: str, end_date: str):
        """Get stock data with parameter validation."""
        # Validate symbol
        try:
            BaseProvider.validate_symbol(symbol)
        except ValueError as e:
            raise InvalidParameterError(str(e))

        # Validate date range
        try:
            BaseProvider.validate_date_range(start_date, end_date)
        except ValueError as e:
            raise InvalidParameterError(str(e))

        print(f"✓ Parameters validated: {symbol}, {start_date} to {end_date}")
        return pd.DataFrame()

    # Valid parameters
    try:
        get_stock_data("600000", "2024-01-01", "2024-12-31")
    except InvalidParameterError as e:
        print(f"✗ Error: {e}")

    # Invalid symbol
    try:
        get_stock_data("ABC", "2024-01-01", "2024-12-31")
    except InvalidParameterError as e:
        print(f"✗ Error: {e}")

    # Invalid date range
    try:
        get_stock_data("600000", "2024-12-31", "2024-01-01")
    except InvalidParameterError as e:
        print(f"✗ Error: {e}")

    print()


def example_upstream_error_handling():
    """Example 2: Handling upstream errors."""
    print("Example 2: Upstream Error Handling")
    print("-" * 50)

    import requests
    from unittest.mock import Mock

    def fetch_from_api(url: str):
        """Simulate API call with error handling."""
        try:
            # Simulate different error scenarios
            if "timeout" in url:
                raise requests.Timeout("Connection timeout")
            elif "404" in url:
                response = Mock()
                response.status_code = 404
                error = requests.HTTPError("Not found")
                error.response = response
                raise error
            elif "429" in url:
                response = Mock()
                response.status_code = 429
                error = requests.HTTPError("Too many requests")
                error.response = response
                raise error
            else:
                return {"data": []}
        except Exception as e:
            # Convert to appropriate MarketDataError
            raise handle_upstream_error(e, "example_api")

    # Test different scenarios
    scenarios = [
        ("https://api.example.com/data", "Success"),
        ("https://api.example.com/timeout", "Timeout"),
        ("https://api.example.com/404", "Not Found"),
        ("https://api.example.com/429", "Rate Limited"),
    ]

    for url, description in scenarios:
        try:
            _ = fetch_from_api(url)
            print(f"✓ {description}: Success")
        except DataSourceUnavailableError as e:
            print(f"✗ {description}: DataSourceUnavailableError - {e}")
        except InvalidParameterError as e:
            print(f"✗ {description}: InvalidParameterError - {e}")
        except Exception as e:
            print(f"✗ {description}: {type(e).__name__} - {e}")

    print()


def example_data_validation():
    """Example 3: Data validation with custom exceptions."""
    print("Example 3: Data Validation")
    print("-" * 50)

    from akshare_one.modules.exceptions import DataValidationError

    def validate_market_data(df: pd.DataFrame):
        """Validate market data integrity."""
        # Check for negative prices
        if 'close' in df.columns and (df['close'] < 0).any():
            raise DataValidationError("Close price cannot be negative")

        # Check for negative volume
        if 'volume' in df.columns and (df['volume'] < 0).any():
            raise DataValidationError("Volume cannot be negative")

        # Check for missing required fields
        required_fields = ['date', 'symbol', 'close']
        missing = set(required_fields) - set(df.columns)
        if missing:
            raise UpstreamChangedError(
                f"Missing required fields: {missing}. API structure may have changed."
            )

        print("✓ Data validation passed")

    # Valid data
    valid_df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'symbol': ['600000', '600001'],
        'close': [10.0, 11.0],
        'volume': [1000, 2000]
    })

    try:
        validate_market_data(valid_df)
    except Exception as e:
        print(f"✗ Error: {e}")

    # Invalid data - negative price
    invalid_df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'symbol': ['600000', '600001'],
        'close': [10.0, -1.0],
        'volume': [1000, 2000]
    })

    try:
        validate_market_data(invalid_df)
    except DataValidationError as e:
        print(f"✗ Error: {e}")

    # Missing fields
    incomplete_df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'symbol': ['600000', '600001']
    })

    try:
        validate_market_data(incomplete_df)
    except UpstreamChangedError as e:
        print(f"✗ Error: {e}")

    print()


def example_exception_hierarchy():
    """Example 4: Using exception hierarchy for error handling."""
    print("Example 4: Exception Hierarchy")
    print("-" * 50)

    from akshare_one.modules.exceptions import MarketDataError

    def risky_operation(scenario: str):
        """Simulate different error scenarios."""
        if scenario == "invalid_param":
            raise InvalidParameterError("Invalid parameter")
        elif scenario == "no_data":
            raise NoDataError("No data available")
        elif scenario == "upstream_down":
            raise DataSourceUnavailableError("Upstream service unavailable")
        else:
            return "Success"

    scenarios = ["success", "invalid_param", "no_data", "upstream_down"]

    for scenario in scenarios:
        try:
            result = risky_operation(scenario)
            print(f"✓ {scenario}: {result}")
        except InvalidParameterError as e:
            print(f"✗ {scenario}: Invalid parameter - {e}")
        except NoDataError as e:
            print(f"✗ {scenario}: No data - {e}")
        except DataSourceUnavailableError as e:
            print(f"✗ {scenario}: Source unavailable - {e}")
        except MarketDataError as e:
            # Catch-all for any other market data errors
            print(f"✗ {scenario}: Market data error - {e}")

    print()


def example_provider_integration():
    """Example 5: Integration with BaseProvider."""
    print("Example 5: Provider Integration")
    print("-" * 50)

    provider = ExampleProvider()

    # Get metadata
    print(f"Provider metadata: {provider.metadata}")

    # Fetch and standardize data
    try:
        data = provider.get_data()
        print(f"✓ Fetched {len(data)} rows")
        print(f"Columns: {list(data.columns)}")
        print(f"Data types: {data.dtypes.to_dict()}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()


if __name__ == "__main__":
    print("=" * 50)
    print("Market Data Exception Usage Examples")
    print("=" * 50)
    print()

    example_parameter_validation()
    example_upstream_error_handling()
    example_data_validation()
    example_exception_hierarchy()
    example_provider_integration()

    print("=" * 50)
    print("All examples completed!")
    print("=" * 50)
