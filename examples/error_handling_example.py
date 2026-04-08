"""
Example demonstrating error codes and enhanced logging in practice.

This script shows how to:
1. Handle exceptions with error codes
2. Log errors with structured context
3. Use multi-source API with error tracking
4. Check error categories for better handling
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from akshare_one import get_hist_data, get_realtime_data
from akshare_one.error_codes import ErrorCode, get_error_category_name, get_error_description
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    DataSourceUnavailableError,
    map_to_standard_exception,
)
from akshare_one.logging_config import setup_logging, get_logger, log_exception

# Setup logging
logger = setup_logging(log_level="INFO", enable_console=True, enable_file=False, json_format=True)


def example_1_handle_invalid_symbol():
    """Example 1: Handling invalid symbol errors."""
    print("\n" + "=" * 60)
    print("Example 1: Handling Invalid Symbol Errors")
    print("=" * 60)

    try:
        raise InvalidParameterError(
            "Symbol 'ABC' is not a valid 6-digit format",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "ABC", "expected_format": "6 digits"},
        )
    except InvalidParameterError as e:
        print(f"\nCaught InvalidParameterError:")
        print(f"  Error Code: {e.error_code.value}")
        print(f"  Category: {get_error_category_name(e.error_code)}")
        print(f"  Description: {get_error_description(e.error_code)}")
        print(f"  Context: {e.context}")

        # Log the error with full context
        log_exception(logger, e, source="eastmoney", endpoint="get_hist_data", symbol="ABC")

        # Handle based on error code
        if e.error_code == ErrorCode.INVALID_SYMBOL_FORMAT:
            print("\n  Action: Prompt user to enter valid 6-digit symbol")


def example_2_handle_invalid_date():
    """Example 2: Handling invalid date format."""
    print("\n" + "=" * 60)
    print("Example 2: Handling Invalid Date Format")
    print("=" * 60)

    try:
        raise InvalidParameterError(
            "Date format invalid: '2024/01/01'",
            error_code=ErrorCode.INVALID_DATE_FORMAT,
            context={"date": "2024/01/01", "expected": "YYYY-MM-DD"},
        )
    except InvalidParameterError as e:
        print(f"\nCaught InvalidParameterError:")
        print(f"  Error Code: {e.error_code.value}")
        print(f"  Category: {get_error_category_name(e.error_code)}")
        print(f"  Description: {get_error_description(e.error_code)}")

        if e.error_code == ErrorCode.INVALID_DATE_FORMAT:
            print("\n  Action: Inform user to use YYYY-MM-DD format")


def example_3_multi_source_error_handling():
    """Example 3: Multi-source API with error tracking."""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Source Error Handling")
    print("=" * 60)

    try:
        raise DataSourceUnavailableError(
            "All data sources failed after retries",
            error_code=ErrorCode.SOURCE_UNAVAILABLE,
            context={"sources": ["eastmoney", "sina", "qq"], "retries": 3},
        )
    except DataSourceUnavailableError as e:
        print(f"\nCaught DataSourceUnavailableError:")
        print(f"  Error Code: {e.error_code.value}")
        print(f"  Category: {get_error_category_name(e.error_code)}")

        if e.error_code == ErrorCode.SOURCE_UNAVAILABLE:
            print("\n  Action: All sources failed, inform user to try later")


def example_4_checking_error_category():
    """Example 4: Handling errors by category."""
    print("\n" + "=" * 60)
    print("Example 4: Handling Errors by Category")
    print("=" * 60)

    try:
        raise InvalidParameterError(
            "Invalid symbol 'XYZ123' and date 'invalid-date'",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "XYZ123", "start_date": "invalid-date"},
        )
    except InvalidParameterError as e:
        category = get_error_category_name(e.error_code)

        print(f"\nError Category: {category}")

        # Handle by category
        if category == "Parameter Validation":
            print("  This is a parameter validation error")
            print("  Action: Show user-friendly input validation message")

        elif category == "Network":
            print("  This is a network connectivity error")
            print("  Action: Suggest retry or check internet connection")

        elif category == "Data Source":
            print("  This is a data source error")
            print("  Action: Try alternative data source")


def example_5_mapped_exception_preserves_error_code():
    """Example 5: Mapped exceptions preserve error code."""
    print("\n" + "=" * 60)
    print("Example 5: Mapped Exceptions Preserve Error Code")
    print("=" * 60)

    try:
        # Internal error
        raise InvalidParameterError(
            "Symbol must be 6 digits", error_code=ErrorCode.INVALID_SYMBOL_FORMAT, context={"symbol": "ABC"}
        )
    except InvalidParameterError as e:
        # Map to standard exception for external API
        mapped = map_to_standard_exception(e, {"source": "eastmoney"})

        print(f"\nMapped Exception:")
        print(f"  Type: {type(mapped).__name__}")
        print(f"  Message: {mapped}")

        # Error code is preserved
        if hasattr(mapped, "error_code"):
            print(f"  Preserved Error Code: {mapped.error_code.value}")
            print(f"  Preserved Context: {mapped.context}")

        # Now raise it for external caller
        print("\n  External caller would catch ValueError with error_code attribute")


def example_6_api_error_logging():
    """Example 6: API error logging with error codes."""
    print("\n" + "=" * 60)
    print("Example 6: API Error Logging")
    print("=" * 60)

    from akshare_one.logging_config import log_api_request

    # Log successful request
    log_api_request(logger, source="eastmoney", endpoint="get_hist_data", duration_ms=150, status="success", rows=100)

    # Log failed request with error code
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_realtime_data",
        duration_ms=5000,
        status="error",
        error="Timeout after 5 seconds",
        error_code=ErrorCode.SOURCE_TIMEOUT.value,
    )

    # Log rate limit error
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_news_data",
        status="error",
        error="Rate limit exceeded",
        error_code=ErrorCode.RATE_LIMIT_EXCEEDED.value,
    )

    print("\n  Logged 3 API requests (1 success, 2 errors)")
    print("  JSON logs include error_code field for tracking")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Error Codes and Enhanced Logging Examples")
    print("=" * 70 + "\n")

    example_1_handle_invalid_symbol()
    example_2_handle_invalid_date()
    example_3_multi_source_error_handling()
    example_4_checking_error_category()
    example_5_mapped_exception_preserves_error_code()
    example_6_api_error_logging()

    print("\n" + "=" * 70)
    print("All Examples Completed")
    print("=" * 70 + "\n")

    print("Key Takeaways:")
    print("1. All exceptions now include error_code attribute")
    print("2. Error codes follow format: E{Module}{Type}{Sequence}")
    print("3. Logs include error_code field for better tracking")
    print("4. Mapped exceptions preserve error codes")
    print("5. Use get_error_category_name() for category-based handling")
    print("6. Use get_error_description() for user-friendly messages")


if __name__ == "__main__":
    main()
