import sys
import os
import pandas as pd
import logging

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from akshare_one import get_hist_data

logging.basicConfig(level=logging.INFO)

def test_cache():
    symbol = "600000"
    start_date = "2024-01-01"
    end_date = "2024-01-10"
    
    print(f"--- First run (should fetch from network and save to cache) ---")
    df1 = get_hist_data(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date, 
        source="duckdb_cache"
    )
    print(f"Fetched {len(df1)} rows from {df1.attrs.get('source')}")
    print(df1.head())
    
    print(f"\n--- Second run (should fetch from DuckDB cache) ---")
    df2 = get_hist_data(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date, 
        source="duckdb_cache"
    )
    print(f"Fetched {len(df2)} rows from {df2.attrs.get('source')}")
    print(df2.head())
    
    # Verify data matches
    pd.testing.assert_frame_equal(df1.reset_index(drop=True), df2.reset_index(drop=True))
    print("\nVerification successful: Data matches!")

if __name__ == "__main__":
    try:
        test_cache()
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
