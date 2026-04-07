#!/usr/bin/env python3
"""
AKShare One Installation Verification Script

This script verifies that AKShare One is properly installed and functional.
It tests core functionality without requiring network access (using mock data where possible).
"""

import sys
import warnings
from pathlib import Path

# Suppress warnings during verification
warnings.filterwarnings("ignore")


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_success(msg: str) -> None:
    """Print a success message."""
    print(f"✓ {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    print(f"✗ {msg}", file=sys.stderr)


def print_warning(msg: str) -> None:
    """Print a warning message."""
    print(f"⚠ {msg}")


def test_imports() -> bool:
    """Test basic module imports."""
    print_header("Testing Module Imports")

    try:
        # Test core imports
        from akshare_one import (
            get_hist_data,
            get_realtime_data,
            get_basic_info,
            get_news_data,
            apply_data_filter,
        )
        print_success("Core API functions imported")

        # Test module imports
        from akshare_one.modules.historical import HistoricalDataFactory
        from akshare_one.modules.realtime import RealtimeDataFactory
        print_success("Data module factories imported")

        # Test multi-source imports
        from akshare_one.modules.multi_source import MultiSourceRouter
        print_success("Multi-source router imported")

        # Test indicators (optional)
        try:
            from akshare_one.indicators import get_sma, get_rsi
            print_success("Technical indicators imported")
        except ImportError as e:
            print_warning(f"Technical indicators not available (optional): {e}")

        # Test extended modules
        from akshare_one.modules.northbound import NorthboundFactory
        from akshare_one.modules.fundflow import FundFlowFactory
        from akshare_one.modules.macro import MacroFactory
        print_success("Extended modules imported")

        return True

    except ImportError as e:
        print_error(f"Import failed: {e}")
        return False


def test_data_filter() -> bool:
    """Test data filtering functionality."""
    print_header("Testing Data Filtering")

    try:
        import pandas as pd
        from akshare_one import apply_data_filter

        # Create test DataFrame
        df = pd.DataFrame({
            "symbol": ["600000", "600001", "600002"],
            "price": [10.5, 20.3, 15.8],
            "volume": [1000, 2000, 1500],
        })

        # Test column filtering
        filtered = apply_data_filter(df, columns=["symbol", "price"])
        if list(filtered.columns) == ["symbol", "price"]:
            print_success("Column filtering works")
        else:
            print_error("Column filtering failed")
            return False

        # Test row filtering (top_n)
        filtered = apply_data_filter(df, row_filter={"top_n": 2})
        if len(filtered) == 2:
            print_success("Row filtering (top_n) works")
        else:
            print_error("Row filtering failed")
            return False

        # Test sorting
        filtered = apply_data_filter(
            df, row_filter={"sort_by": "price", "ascending": False}
        )
        if filtered.iloc[0]["price"] == 20.3:
            print_success("Sorting works")
        else:
            print_error("Sorting failed")
            return False

        return True

    except Exception as e:
        print_error(f"Data filter test failed: {e}")
        return False


def test_factory_initialization() -> bool:
    """Test factory class initialization."""
    print_header("Testing Factory Initialization")

    try:
        from akshare_one.modules.historical import HistoricalDataFactory
        from akshare_one.modules.realtime import RealtimeDataFactory

        # Test historical data factory
        provider = HistoricalDataFactory.get_provider(
            "eastmoney_direct",
            symbol="600000",
            interval="day",
        )
        print_success(f"Historical provider initialized: {provider.__class__.__name__}")

        # Test realtime data factory
        provider = RealtimeDataFactory.get_provider("eastmoney_direct", symbol="600000")
        print_success(f"Realtime provider initialized: {provider.__class__.__name__}")

        return True

    except Exception as e:
        print_error(f"Factory initialization failed: {e}")
        return False


def test_data_schema() -> bool:
    """Test that data schemas are properly defined."""
    print_header("Testing Data Schemas")

    try:
        from akshare_one.modules.historical.base import HistoricalDataProvider
        from akshare_one.modules.realtime.base import RealtimeDataProvider

        # Check that providers have required methods
        historical_methods = ["get_hist_data"]
        for method in historical_methods:
            if hasattr(HistoricalDataProvider, method):
                print_success(f"Historical provider has method: {method}")
            else:
                print_error(f"Historical provider missing method: {method}")
                return False

        realtime_methods = ["get_current_data"]
        for method in realtime_methods:
            if hasattr(RealtimeDataProvider, method):
                print_success(f"Realtime provider has method: {method}")
            else:
                print_error(f"Realtime provider missing method: {method}")
                return False

        return True

    except Exception as e:
        print_error(f"Schema test failed: {e}")
        return False


def test_pandas_operations() -> bool:
    """Test pandas compatibility."""
    print_header("Testing Pandas Operations")

    try:
        import pandas as pd

        # Create sample data mimicking API output
        df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=5),
            "open": [10.0, 10.5, 11.0, 10.8, 11.2],
            "high": [10.5, 11.0, 11.5, 11.2, 11.8],
            "low": [9.8, 10.2, 10.8, 10.5, 11.0],
            "close": [10.3, 10.8, 11.2, 11.0, 11.5],
            "volume": [1000, 1200, 1500, 1100, 1300],
        })

        # Test basic operations
        if df["close"].dtype in [float, pd.Float64Dtype()]:
            print_success("DataFrame numeric columns OK")
        else:
            print_warning("DataFrame column types unexpected")

        # Test time operations
        if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            print_success("DataFrame datetime columns OK")
        else:
            print_warning("DataFrame timestamp type unexpected")

        return True

    except Exception as e:
        print_error(f"Pandas operations test failed: {e}")
        return False


def test_optional_dependencies() -> bool:
    """Test optional dependencies."""
    print_header("Testing Optional Dependencies")

    # Test TA-Lib (optional)
    try:
        import talib
        print_success("TA-Lib available (optional)")
    except ImportError:
        print_warning("TA-Lib not available (optional, for technical indicators)")

    # Test MCP dependencies (optional)
    try:
        import fastmcp
        import pydantic
        print_success("MCP dependencies available (optional)")
    except ImportError:
        print_warning("MCP dependencies not available (optional, for MCP server)")

    return True


def run_network_test() -> bool:
    """Run a simple network test if user agrees."""
    print_header("Network Connectivity Test (Optional)")

    try:
        # Ask user if they want to run network tests
        response = input("\nRun network connectivity test? (y/n): ").strip().lower()

        if response != "y":
            print("Skipping network test")
            return True

        print("\nAttempting to fetch real data (may take a few seconds)...")

        from akshare_one import get_realtime_data

        # Try to get realtime data
        df = get_realtime_data(symbol="600000")

        if df is not None and len(df) > 0:
            print_success(f"Network test passed: fetched {len(df)} records")
            print("\nSample data:")
            print(df.head(2).to_string(index=False))
            return True
        else:
            print_warning("Network test returned empty data")
            return True

    except KeyboardInterrupt:
        print("\nNetwork test skipped by user")
        return True
    except Exception as e:
        print_warning(f"Network test failed: {e}")
        print_warning("This may be due to network issues or API changes")
        return True  # Don't fail verification for network issues


def generate_report(results: dict) -> None:
    """Generate a diagnostic report."""
    print_header("Verification Report")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print(f"\nTests Passed: {passed_tests}/{total_tests}")

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")

    if passed_tests == total_tests:
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        print("\nAKShare One is ready to use!")
    else:
        print("\n" + "=" * 50)
        print("⚠ SOME TESTS FAILED")
        print("=" * 50)
        print("\nPlease check the errors above and refer to the documentation:")
        print("  - docs/quickstart.md")
        print("  - https://zwldarren.github.io/akshare-one/")

    # Environment info
    print("\n" + "=" * 50)
    print("Environment Information")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print(f"Working Directory: {Path.cwd()}")

    try:
        import akshare_one
        print(f"AKShare One Location: {akshare_one.__file__}")
    except Exception:
        pass

    try:
        import pandas as pd
        print(f"Pandas Version: {pd.__version__}")
    except Exception:
        pass


def main() -> int:
    """Run all verification tests."""
    print("=" * 50)
    print("  AKShare One Installation Verification")
    print("=" * 50)
    print("\nThis script will verify your installation by testing:")
    print("  - Module imports")
    print("  - Data filtering")
    print("  - Factory initialization")
    print("  - Data schemas")
    print("  - Pandas compatibility")
    print("  - Optional dependencies")
    print("  - Network connectivity (optional)")
    print("\nEstimated time: < 1 minute")

    # Run tests
    results = {
        "Module Imports": test_imports(),
        "Data Filtering": test_data_filter(),
        "Factory Initialization": test_factory_initialization(),
        "Data Schemas": test_data_schema(),
        "Pandas Operations": test_pandas_operations(),
        "Optional Dependencies": test_optional_dependencies(),
        "Network Connectivity": run_network_test(),
    }

    # Generate report
    generate_report(results)

    # Return exit code
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())