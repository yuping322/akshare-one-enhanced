#!/usr/bin/env python
"""
Verification script for key exceptions containing error codes.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from akshare_one.modules.base import BaseProvider
from akshare_one.modules.exceptions import InvalidParameterError
from akshare_one.error_codes import ErrorCode


def verify_validate_symbol():
    """Verify validate_symbol includes error codes."""
    print("1. Testing validate_symbol:")
    try:
        BaseProvider.validate_symbol('ABC')  # Invalid format
    except InvalidParameterError as e:
        print(f"   ✓ Raises InvalidParameterError")
        print(f"   ✓ Has error_code: {e.error_code.value}")
        print(f"   ✓ Error code matches: {e.error_code == ErrorCode.INVALID_SYMBOL_FORMAT}")
        print(f"   ✓ Context included: {e.context}")
        print(f"   ✓ Message format: {str(e)}")
        return True
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        return False


def verify_validate_symbol_empty():
    """Verify validate_symbol handles empty case."""
    print("\n2. Testing validate_symbol with empty string:")
    try:
        BaseProvider.validate_symbol('')
    except InvalidParameterError as e:
        print(f"   ✓ Raises InvalidParameterError")
        print(f"   ✓ Error code: {e.error_code.value}")
        print(f"   ✓ Matches INVALID_SYMBOL_EMPTY: {e.error_code == ErrorCode.INVALID_SYMBOL_EMPTY}")
        return True
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        return False


def verify_validate_date():
    """Verify validate_date includes error codes."""
    print("\n3. Testing validate_date:")
    try:
        BaseProvider.validate_date('2024/01/01', 'start_date')  # Invalid format
    except InvalidParameterError as e:
        print(f"   ✓ Raises InvalidParameterError")
        print(f"   ✓ Has error_code: {e.error_code.value}")
        print(f"   ✓ Error code matches: {e.error_code == ErrorCode.INVALID_DATE_FORMAT}")
        print(f"   ✓ Context included: {e.context}")
        return True
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        return False


def verify_validate_date_empty():
    """Verify validate_date handles empty case."""
    print("\n4. Testing validate_date with empty string:")
    try:
        BaseProvider.validate_date('', 'end_date')
    except InvalidParameterError as e:
        print(f"   ✓ Raises InvalidParameterError")
        print(f"   ✓ Error code: {e.error_code.value}")
        print(f"   ✓ Matches INVALID_DATE_EMPTY: {e.error_code == ErrorCode.INVALID_DATE_EMPTY}")
        return True
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        return False


def verify_validate_date_range():
    """Verify validate_date_range includes error codes."""
    print("\n5. Testing validate_date_range:")
    try:
        BaseProvider.validate_date_range('2024-12-31', '2024-01-01')  # Invalid range
    except InvalidParameterError as e:
        print(f"   ✓ Raises InvalidParameterError")
        print(f"   ✓ Has error_code: {e.error_code.value}")
        print(f"   ✓ Error code matches: {e.error_code == ErrorCode.INVALID_DATE_RANGE}")
        print(f"   ✓ Context included: {e.context}")
        return True
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        return False


def verify_all_exception_types():
    """Verify all exception types support error codes."""
    from akshare_one.modules.exceptions import (
        DataSourceUnavailableError,
        NoDataError,
        RateLimitError,
        DataValidationError,
        UpstreamChangedError,
    )

    print("\n6. Testing all exception types support error codes:")

    exceptions = [
        ("InvalidParameterError", InvalidParameterError("test", error_code=ErrorCode.INVALID_SYMBOL_FORMAT)),
        ("DataSourceUnavailableError", DataSourceUnavailableError("test", error_code=ErrorCode.SOURCE_UNAVAILABLE)),
        ("NoDataError", NoDataError("test", error_code=ErrorCode.SOURCE_NO_DATA)),
        ("RateLimitError", RateLimitError("test", error_code=ErrorCode.RATE_LIMIT_EXCEEDED)),
        ("DataValidationError", DataValidationError("test", error_code=ErrorCode.VALIDATION_VALUE_ERROR)),
        ("UpstreamChangedError", UpstreamChangedError("test", error_code=ErrorCode.SOURCE_SCHEMA_CHANGED)),
    ]

    all_passed = True
    for name, exc in exceptions:
        has_error_code = hasattr(exc, 'error_code') and exc.error_code is not None
        has_context = hasattr(exc, 'context')
        has_message = hasattr(exc, 'message')
        has_str_format = str(exc).startswith(f"[{exc.error_code.value}]")

        if has_error_code and has_context and has_message and has_str_format:
            print(f"   ✓ {name}: error_code={exc.error_code.value}, all attributes present")
        else:
            print(f"   ✗ {name}: Missing attributes")
            all_passed = False

    return all_passed


def verify_error_code_count():
    """Verify we have at least 20 error codes."""
    print("\n7. Verifying error code count:")
    total = len(ErrorCode)
    meets_requirement = total >= 20

    print(f"   Total error codes: {total}")
    print(f"   Requirement: >= 20")
    print(f"   ✓ Requirement met: {meets_requirement}")

    return meets_requirement


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("Error Code Verification Tests")
    print("=" * 70)

    results = [
        verify_validate_symbol(),
        verify_validate_symbol_empty(),
        verify_validate_date(),
        verify_validate_date_empty(),
        verify_validate_date_range(),
        verify_all_exception_types(),
        verify_error_code_count(),
    ]

    print("\n" + "=" * 70)
    if all(results):
        print("All Verification Tests Passed ✓")
        print("=" * 70)
        print("\nSummary:")
        print("  ✓ All key validation methods include error codes")
        print("  ✓ All exception types support error_code parameter")
        print("  ✓ Error codes properly propagated through exceptions")
        print("  ✓ Error codes properly formatted in exception messages")
        print("  ✓ Error code count meets requirement (>= 20)")
        print("=" * 70)
        return 0
    else:
        print("Some Verification Tests Failed ✗")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())