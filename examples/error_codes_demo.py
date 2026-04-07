"""
Simple demonstration of error codes and enhanced logging system.

This script shows how error codes work without requiring network calls.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from akshare_one.error_codes import ErrorCode, get_error_description, get_error_category_name
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
    RateLimitError,
    DataValidationError,
    UpstreamChangedError,
    map_to_standard_exception,
)
from akshare_one.logging_config import setup_logging, get_logger, log_exception, log_api_request


def demo_error_codes():
    """Demonstrate error code enumeration."""
    print("=" * 70)
    print("Error Codes Demonstration")
    print("=" * 70)

    # Show error code structure
    print("\n1. Error Code Structure:")
    ec = ErrorCode.INVALID_SYMBOL_FORMAT
    print(f"   Code: {ec.value}")
    print(f"   Format: E{ec.category}{ec.type_code}{ec.sequence}")
    print(f"   Module: {ec.category} (Parameter Validation)")
    print(f"   Type: {ec.type_code} (Invalid Format)")
    print(f"   Sequence: {ec.sequence}")

    # Show all categories
    print("\n2. Error Categories:")
    categories = {}
    for ec in ErrorCode:
        cat = ec.category
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    for cat, count in sorted(categories.items()):
        name = get_error_category_name(cat + "000")
        print(f"   {cat} - {name}: {count} codes")

    print(f"\n   Total: {len(ErrorCode)} error codes")


def demo_exceptions():
    """Demonstrate exceptions with error codes."""
    print("\n" + "=" * 70)
    print("Exceptions with Error Codes")
    print("=" * 70)

    examples = [
        ("Invalid Symbol", InvalidParameterError(
            "Symbol 'ABC' is not a valid 6-digit format",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "ABC", "expected_format": "6 digits"}
        )),
        ("Invalid Date", InvalidParameterError(
            "Date format invalid: '2024/01/01'",
            error_code=ErrorCode.INVALID_DATE_FORMAT,
            context={"date": "2024/01/01", "expected": "YYYY-MM-DD"}
        )),
        ("Source Unavailable", DataSourceUnavailableError(
            "Failed to connect to eastmoney API",
            error_code=ErrorCode.SOURCE_CONNECTION_FAILED,
            context={"source": "eastmoney", "timeout": 10}
        )),
        ("Rate Limit", RateLimitError(
            "API rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            context={"retry_after": 60, "quota": "1000/hour"}
        )),
        ("No Data", NoDataError(
            "No historical data available for symbol XYZ",
            error_code=ErrorCode.SOURCE_NO_DATA,
            context={"symbol": "XYZ", "date_range": "2024-01-01 to 2024-12-31"}
        )),
    ]

    print("\n3. Exception Examples:")
    for i, (label, exc) in enumerate(examples, 1):
        print(f"\n   {i}. {label}:")
        print(f"      Type: {type(exc).__name__}")
        print(f"      Error Code: {exc.error_code.value}")
        print(f"      Category: {get_error_category_name(exc.error_code)}")
        print(f"      Description: {get_error_description(exc.error_code)}")
        print(f"      Context: {exc.context}")
        print(f"      Full Message: {str(exc)}")


def demo_exception_mapping():
    """Demonstrate exception mapping preserves error codes."""
    print("\n" + "=" * 70)
    print("Exception Mapping Preserves Error Codes")
    print("=" * 70)

    print("\n4. Mapping to Standard Exceptions:")

    # Map InvalidParameterError to ValueError
    exc1 = InvalidParameterError(
        "Invalid symbol format",
        error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
        context={"symbol": "ABC"}
    )
    mapped1 = map_to_standard_exception(exc1, {"source": "eastmoney", "endpoint": "get_hist_data"})

    print(f"\n   a) InvalidParameterError → ValueError:")
    print(f"      Original: {exc1}")
    print(f"      Mapped: {mapped1}")
    print(f"      Type: {type(mapped1).__name__}")
    print(f"      Error Code preserved: {getattr(mapped1, 'error_code', 'N/A')}")
    print(f"      Context preserved: {getattr(mapped1, 'context', {})}")

    # Map DataSourceUnavailableError to ConnectionError
    exc2 = DataSourceUnavailableError(
        "Connection timeout",
        error_code=ErrorCode.SOURCE_TIMEOUT,
        context={"source": "eastmoney"}
    )
    mapped2 = map_to_standard_exception(exc2)

    print(f"\n   b) DataSourceUnavailableError → ConnectionError:")
    print(f"      Original: {exc2}")
    print(f"      Mapped: {mapped2}")
    print(f"      Type: {type(mapped2).__name__}")
    print(f"      Error Code preserved: {getattr(mapped2, 'error_code', 'N/A')}")

    # Map RateLimitError to RuntimeError
    exc3 = RateLimitError(
        "Rate limit exceeded",
        error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
        context={"retry_after": 60}
    )
    mapped3 = map_to_standard_exception(exc3)

    print(f"\n   c) RateLimitError → RuntimeError:")
    print(f"      Original: {exc3}")
    print(f"      Mapped: {mapped3}")
    print(f"      Type: {type(mapped3).__name__}")
    print(f"      Error Code preserved: {getattr(mapped3, 'error_code', 'N/A')}")


def demo_logging():
    """Demonstrate structured logging with error codes."""
    print("\n" + "=" * 70)
    print("Structured Logging with Error Codes")
    print("=" * 70)

    # Setup logging
    logger = setup_logging(
        log_level="INFO",
        enable_console=True,
        enable_file=False,
        json_format=True
    )

    print("\n5. Logging Examples (JSON format includes error_code field):")

    # Log exception with error code
    print("\n   a) Exception Logging:")
    exc = InvalidParameterError(
        "Invalid date: '2024/01/01'",
        error_code=ErrorCode.INVALID_DATE_FORMAT,
        context={"param": "start_date"}
    )
    log_exception(logger, exc, source="eastmoney", endpoint="get_hist_data", symbol="600000")

    # Log API request success
    print("\n   b) API Success:")
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_realtime_data",
        duration_ms=150,
        status="success",
        rows=100
    )

    # Log API request error with error code
    print("\n   c) API Error:")
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_hist_data",
        duration_ms=5000,
        status="error",
        error="Timeout exceeded",
        error_code=ErrorCode.SOURCE_TIMEOUT.value
    )

    # Log rate limit error
    print("\n   d) Rate Limit Error:")
    log_api_request(
        logger,
        source="eastmoney",
        endpoint="get_news_data",
        status="error",
        error="Rate limit exceeded",
        error_code=ErrorCode.RATE_LIMIT_EXCEEDED.value
    )


def demo_error_handling_patterns():
    """Demonstrate common error handling patterns."""
    print("\n" + "=" * 70)
    print("Common Error Handling Patterns")
    print("=" * 70)

    print("\n6. Pattern 1: Handle by Error Code")

    try:
        raise InvalidParameterError(
            "Invalid symbol: XYZ",
            error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
            context={"symbol": "XYZ"}
        )
    except InvalidParameterError as e:
        if e.error_code == ErrorCode.INVALID_SYMBOL_FORMAT:
            print(f"   ✓ Detected symbol format error")
            print(f"   Action: Prompt for valid 6-digit symbol")
        elif e.error_code == ErrorCode.INVALID_SYMBOL_EMPTY:
            print(f"   ✓ Detected empty symbol")
            print(f"   Action: Show 'symbol required' message")

    print("\n7. Pattern 2: Handle by Category")

    try:
        raise DataSourceUnavailableError(
            "API timeout",
            error_code=ErrorCode.SOURCE_TIMEOUT,
            context={"source": "eastmoney"}
        )
    except DataSourceUnavailableError as e:
        category = get_error_category_name(e.error_code)

        if category == "Parameter Validation":
            print(f"   Category: Parameter error - show input validation message")
        elif category == "Data Source":
            print(f"   ✓ Category: Data Source error")
            print(f"   Action: Try alternative source or show 'service unavailable'")
        elif category == "Network":
            print(f"   Category: Network error - suggest retry")

    print("\n8. Pattern 3: Get User-Friendly Description")

    exc = InvalidParameterError(
        "Date range invalid",
        error_code=ErrorCode.INVALID_DATE_RANGE,
        context={"start_date": "2024-12-31", "end_date": "2024-01-01"}
    )

    description = get_error_description(exc.error_code)
    print(f"   Error Code: {exc.error_code.value}")
    print(f"   ✓ User-Friendly: {description}")
    print(f"   Action: {description} - check date order")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("Error Codes and Enhanced Logging System Demo")
    print("=" * 70 + "\n")

    demo_error_codes()
    demo_exceptions()
    demo_exception_mapping()
    demo_logging()
    demo_error_handling_patterns()

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    print("\nKey Features:")
    print("  ✓ 67 unique error codes across 8 categories")
    print("  ✓ All exceptions include error_code and context attributes")
    print("  ✓ Structured JSON logs include error_code field")
    print("  ✓ Mapped exceptions preserve error codes")
    print("  ✓ User-friendly descriptions for each error code")
    print("  ✓ Category-based error handling support")

    print("\nBenefits:")
    print("  1. Better debugging with unique error identifiers")
    print("  2. Easier error tracking in logs and monitoring")
    print("  3. Consistent error handling across the application")
    print("  4. Clear error categorization for appropriate responses")
    print("  5. Preserved error information through exception chains")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()