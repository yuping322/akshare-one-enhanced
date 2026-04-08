"""
Minimal test for Baostock financial data.
"""

import sys

try:
    print("1. Import and login...")
    import baostock as bs

    lg = bs.login()
    print(f"✓ Login result: error_code={lg.error_code}, error_msg={lg.error_msg}")

    if lg.error_code != "0":
        print("✗ Login failed")
        sys.exit(1)

    print("\n2. Query profit data directly...")
    rs = bs.query_profit_data(code="sh.600000", year=2023, quarter=4)
    print(f"✓ Query result: error_code={rs.error_code}, error_msg={rs.error_msg}")

    data_list = []
    while (rs.error_code == "0") & rs.next():
        data_list.append(rs.get_row_data())

    print(f"✓ Data fetched: {len(data_list)} rows")

    if data_list:
        import pandas as pd

        df = pd.DataFrame(data_list, columns=rs.fields)
        print(f"  Fields: {rs.fields}")
        print(f"  DataFrame shape: {df.shape}")
        print(f"  First row:\n{df.head(1).to_string()}")

    print("\n3. Logout...")
    bs.logout()
    print("✓ Logout successful")

    print("\n=== Direct API Test Complete ===")

    print("\n4. Testing our wrapper...")
    from akshare_one.modules.financial.baostock import BaostockFinancialProvider

    provider = BaostockFinancialProvider(symbol="600000")
    print(f"✓ Provider created")

    print("\n5. Fetching profit data via wrapper...")
    df = provider.get_profit_data(year=2023, quarter=4)
    print(f"✓ Data fetched via wrapper: shape={df.shape}")
    if not df.empty:
        print(f"  Columns: {list(df.columns)[:5]}")

    print("\n=== Wrapper Test Complete ===")
    sys.exit(0)

except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
