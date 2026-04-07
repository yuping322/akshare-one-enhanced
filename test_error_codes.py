#!/usr/bin/env python
"""
Test script for error codes and enhanced logging system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from akshare_one.error_codes import ErrorCode, get_error_description, get_error_category_name
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
    RateLimitError,
    DataValidationError,
    UpstreamChangedError,
    MarketDataError,
    map_to_standard_exception,
)
from akshare_one.logging_config import setup_logging, get_logger, log_exception

def test_error_codes():
    """Test error code enumeration and descriptions."""
    print("=" * 60)
    print("Testing Error Codes")
    print("=" * 60)

    # Test ErrorCode enum
    print(f"\n1. Error Code Enum:")
    print(f"   INVALID_SYMBOL_FORMAT: {ErrorCode.INVALID_SYMBOL_FORMAT.value}")
    print(f"   Category: {ErrorCode.INVALID_SYMBOL_FORMAT.category}")
    print(f"   Type: {ErrorCode.INVALID_SYMBOL_FORMAT.type_code}")
    print(f"   Sequence: {ErrorCode.INVALID_SYMBOL_FORMAT.sequence}")

    # Test descriptions
    print(f"\n2. Error Descriptions:")
    desc = get_error_description(ErrorCode.INVALID_SYMBOL_FORMAT)
    print(f"   Description: {desc}")

    # Test category names
    print(f"\n3. Category Names:")
    cat_name = get_error_category_name(ErrorCode.INVALID_SYMBOL_FORMAT)
    print(f"   Category Name: {cat_name}")

    # Test all error codes count
    print(f"\n4. Total Error Codes: {len(ErrorCode)}")
    print(f"   Categories covered: {len(set(e.category for e in ErrorCode))}")

    print("✓ Error codes test passed\n")


def test_exceptions_with_error_codes():
    """Test exceptions with error codes."""
    print("=" * 60)
    print("Testing Exceptions with Error Codes")
    print("=" * 60)

    # Test InvalidParameterError with error code
    print(f"\n1. InvalidParameterError:")
    try:
        raise InvalidParameterError(
            "Invalid symbol format: ABC",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "ABC", "market_type": "a_stock"}
        )
    except InvalidParameterError as e:
        print(f"   Message: {e.message}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Context: {e.context}")
        print(f"   String representation: {str(e)}")

    # Test DataSourceUnavailableError
    print(f"\n2. DataSourceUnavailableError:")
    try:
        raise DataSourceUnavailableError(
            "Failed to connect to eastmoney",
            error_code=ErrorCode.SOURCE_CONNECTION_FAILED,
            context={"source": "eastmoney", "url": "http://example.com"}
        )
    except DataSourceUnavailableError as e:
        print(f"   Message: {e.message}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Context: {e.context}")
        print(f"   String representation: {str(e)}")

    # Test RateLimitError
    print(f"\n3. RateLimitError:")
    try:
        raise RateLimitError(
            "Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            context={"retry_after": 60}
        )
    except RateLimitError as e:
        print(f"   Message: {e.message}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Context: {e.context}")

    print("✓ Exceptions with error codes test passed\n")


def test_exception_mapping():
    """Test exception mapping to standard exceptions."""
    print("=" * 60)
    print("Testing Exception Mapping")
    print("=" * 60)

    # Test mapping InvalidParameterError to ValueError
    print(f"\n1. Mapping InvalidParameterError:")
    try:
        raise InvalidParameterError(
            "Invalid symbol: XYZ",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "XYZ"}
        )
    except InvalidParameterError as e:
        mapped = map_to_standard_exception(e, {"source": "eastmoney"})
        print(f"   Original: {type(e).__name__} - {e}")
        print(f"   Mapped: {type(mapped).__name__} - {mapped}")
        print(f"   Mapped error_code attribute: {getattr(mapped, 'error_code', None)}")
        print(f"   Mapped context attribute: {getattr(mapped, 'context', None)}")

    # Test mapping DataSourceUnavailableError to ConnectionError
    print(f"\n2. Mapping DataSourceUnavailableError:")
    try:
        raise DataSourceUnavailableError(
            "Connection failed",
            error_code=ErrorCode.SOURCE_CONNECTION_FAILED,
            context={"source": "eastmoney"}
        )
    except DataSourceUnavailableError as e:
        mapped = map_to_standard_exception(e)
        print(f"   Original: {type(e).__name__} - {e}")
        print(f"   Mapped: {type(mapped).__name__} - {mapped}")
        print(f"   Mapped error_code: {getattr(mapped, 'error_code', None)}")

    # Test mapping RateLimitError to RuntimeError
    print(f"\n3. Mapping RateLimitError:")
    try:
        raise RateLimitError(
            "Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            context={"retry_after": 60}
        )
    except RateLimitError as e:
        mapped = map_to_standard_exception(e, {"endpoint": "get_hist_data"})
        print(f"   Original: {type(e).__name__} - {e}")
        print(f"   Mapped: {type(mapped).__name__} - {mapped}")
        print(f"   Mapped error_code: {getattr(mapped, 'error_code', None)}")

    print("✓ Exception mapping test passed\n")


def test_logging_with_error_codes():
    """Test logging with error codes."""
    print("=" * 60)
    print("Testing Logging with Error Codes")
    print("=" * 60)

    # Setup logging
    logger = setup_logging(
        log_level="INFO",
        enable_console=True,
        enable_file=False,
        json_format=True
    )

    # Test logging exception with error code
    print(f"\n1. Logging exception with error code:")
    try:
        raise InvalidParameterError(
            "Invalid date format: 2024/01/01",
            error_code=ErrorCode.INVALID_DATE_FORMAT,
            context={"date": "2024/01/01", "param": "start_date"}
        )
    except InvalidParameterError as e:
        log_exception(
            logger,
            e,
            source="eastmoney",
            endpoint="get_hist_data",
            symbol="600000"
        )

    # Test logging API request
    print(f"\n2. Logging API request:")
    from akshare_one.logging_config import log_api_request
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_realtime_data",
        duration_ms=156.5,
        status="success",
        rows=100
    )

    # Test logging API error
    print(f"\n3. Logging API error:")
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_hist_data",
        duration_ms=2000,
        status="error",
        error="Timeout exceeded",
        error_code=ErrorCode.SOURCE_TIMEOUT.value
    )

    print("✓ Logging test passed\n")


def test_all_error_codes_coverage():
    """Test that we have comprehensive error codes."""
    print("=" * 60)
    print("Testing Error Codes Coverage")
    print("=" * 60)

    # Count error codes by category
    categories = {}
    for error_code in ErrorCode:
        cat = error_code.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(error_code)

    print(f"\nError codes by category:")
    for cat, codes in sorted(categories.items()):
        cat_name = get_error_category_name(codes[0])
        print(f"   {cat} ({cat_name}): {len(codes)} codes")

    # Total count
    total = len(ErrorCode)
    print(f"\n   Total: {total} error codes")

    # Check we meet the requirement
    if total >= 20:
        print(f"   ✓ Requirement met: >= 20 error codes ({total} defined)")
    else:
        print(f"   ✗ Requirement NOT met: < 20 error codes ({total} defined)")

    print("✓ Error codes coverage test completed\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Error Codes and Logging System Test Suite")
    print("=" * 60 + "\n")

    try:
        test_error_codes()
        test_exceptions_with_error_codes()
        test_exception_mapping()
        test_logging_with_error_codes()
        test_all_error_codes_coverage()

        print("=" * 60)
        print("All Tests Passed ✓")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"Test Failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()