"""
Test Baostock financial data integration.

This script tests the newly implemented Baostock financial data APIs.
"""

import sys
import pandas as pd
from akshare_one.modules.financial import FinancialDataFactory
from akshare_one.modules.financial.baostock import BaostockFinancialProvider


def test_profit_data():
    """Test profit data (盈利能力) API"""
    print("\n=== Testing Profit Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_profit_data(year=2023, quarter=4)
        print(f"✓ Profit data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_operation_data():
    """Test operation data (营运能力) API"""
    print("\n=== Testing Operation Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_operation_data(year=2023, quarter=4)
        print(f"✓ Operation data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_growth_data():
    """Test growth data (成长能力) API"""
    print("\n=== Testing Growth Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_growth_data(year=2023, quarter=4)
        print(f"✓ Growth data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_balance_data():
    """Test balance data (偿债能力) API"""
    print("\n=== Testing Balance Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_balance_data(year=2023, quarter=4)
        print(f"✓ Balance data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_cash_flow_data():
    """Test cash flow data (现金流量) API"""
    print("\n=== Testing Cash Flow Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_cash_flow_data(year=2023, quarter=4)
        print(f"✓ Cash flow data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_dupont_data():
    """Test dupont data (杜邦指数) API"""
    print("\n=== Testing Dupont Data ===")
    try:
        provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
        df = provider.get_dupont_data(year=2023, quarter=4)
        print(f"✓ Dupont data fetched successfully. Shape: {df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}...")
            print(f"  Sample:\n{df.head(2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_symbol_conversion():
    """Test symbol conversion"""
    print("\n=== Testing Symbol Conversion ===")
    try:
        # Test different symbol formats
        test_cases = [
            ("600000", "sh.600000"),
            ("000001", "sz.000001"),
            ("sh.600000", "sh.600000"),
            ("sz.000001", "sz.000001"),
        ]

        for input_symbol, expected_code in test_cases:
            provider = BaostockFinancialProvider(symbol=input_symbol)
            assert provider.bs_code == expected_code, f"Expected {expected_code}, got {provider.bs_code}"
            print(f"✓ Symbol '{input_symbol}' -> '{provider.bs_code}'")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_provider_registration():
    """Test that provider is registered in factory"""
    print("\n=== Testing Provider Registration ===")
    try:
        sources = FinancialDataFactory.list_sources()
        print(f"✓ Available financial data sources: {sources}")
        assert "baostock" in sources, "Baostock not registered in FinancialDataFactory"
        print("✓ Baostock is registered in FinancialDataFactory")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_logout():
    """Test logout functionality"""
    print("\n=== Testing Logout ===")
    try:
        BaostockFinancialProvider.logout()
        assert not BaostockFinancialProvider._is_logged_in, "Should be logged out"
        print("✓ Logged out successfully")

        # Re-login for subsequent tests if needed
        BaostockFinancialProvider._ensure_login()
        assert BaostockFinancialProvider._is_logged_in, "Should be logged in"
        print("✓ Re-logged in successfully")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Baostock Financial Data Integration Test")
    print("=" * 60)

    tests = [
        ("Provider Registration", test_provider_registration),
        ("Symbol Conversion", test_symbol_conversion),
        ("Profit Data", test_profit_data),
        ("Operation Data", test_operation_data),
        ("Growth Data", test_growth_data),
        ("Balance Data", test_balance_data),
        ("Cash Flow Data", test_cash_flow_data),
        ("Dupont Data", test_dupont_data),
        ("Logout", test_logout),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"✗ Test {test_name} failed with exception: {e}")
            results.append((test_name, "ERROR"))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, status in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, status in results if status == "PASS")
    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
