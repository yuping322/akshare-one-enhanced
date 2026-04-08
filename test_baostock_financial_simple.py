"""
Simple test for Baostock financial data.
"""

import sys

try:
    print("1. Importing module...")
    from akshare_one.modules.financial import FinancialDataFactory
    from akshare_one.modules.financial.baostock import BaostockFinancialProvider

    print("✓ Import successful")

    print("\n2. Checking registration...")
    sources = FinancialDataFactory.list_sources()
    print(f"✓ Available sources: {sources}")

    print("\n3. Creating provider...")
    provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")
    print(f"✓ Provider created: {provider}")
    print(f"  bs_code: {provider.bs_code}")

    print("\n4. Testing profit data API (without year/quarter)...")
    try:
        df = provider.get_profit_data()
        print(f"✓ Profit data fetched: shape={df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}")
            print(f"  First row:\n{df.head(1).to_string()}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n5. Testing profit data API with year/quarter...")
    try:
        df = provider.get_profit_data(year=2023, quarter=4)
        print(f"✓ Profit data fetched: shape={df.shape}")
        if not df.empty:
            print(f"  Columns: {list(df.columns)[:5]}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n6. Logout...")
    BaostockFinancialProvider.logout()
    print("✓ Logout successful")

    print("\n=== Test Complete ===")
    sys.exit(0)

except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
