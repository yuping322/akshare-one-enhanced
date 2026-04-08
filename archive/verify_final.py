import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

import akshare_one as ak1

logging.basicConfig(level=logging.INFO)

def test_jq_apis():
    symbol = "600000"
    
    print(f"--- Testing get_price ---")
    try:
        df_price = ak1.get_price(symbol, count=5, frequency="daily")
        print(f"get_price returned {len(df_price)} rows")
        print(df_price.head())
    except Exception as e:
        print(f"get_price failed (expected if no network/cache): {e}")

    print(f"\n--- Testing get_bars ---")
    try:
        df_bars = ak1.get_bars(symbol, count=5, unit="1d")
        print(f"get_bars returned {len(df_bars)} rows")
        print(df_bars.head())
    except Exception as e:
        print(f"get_bars failed: {e}")

    print(f"\n--- Testing history ---")
    try:
        df_hist = ak1.history(count=5, unit="1d", field="close", security_list=[symbol, "000001"])
        print(f"history returned DataFrame with shape {df_hist.shape}")
        print(df_hist.head())
    except Exception as e:
        print(f"history failed: {e}")

    # Test get_all_securities
    print("Testing get_all_securities...")
    try:
        stocks = ak1.get_all_securities()
        print(f"Total securities: {len(stocks)}")
        if not stocks.empty:
            print(f"First 5 stocks:\n{stocks.head()}")
    except Exception as e:
        print(f"get_all_securities failed: {e}")
        
    # Test get_trade_dates_between
    print("\nTesting get_trade_dates_between...")
    try:
        days = ak1.get_trade_dates_between("2023-01-01", "2023-01-10")
        print(f"Trade days in early Jan 2023: {days}")
    except Exception as e:
        print(f"get_trade_dates_between failed: {e}")
    
    # Test get_concepts
    print("\nTesting get_concepts...")
    try:
        concepts = ak1.get_concepts()
        if not concepts.empty:
            print(f"Total concepts: {len(concepts)}")
            print(f"First 5 concepts:\n{concepts.head()}")
    except Exception as e:
        print(f"get_concepts failed: {e}")

    print(f"\n--- Testing get_valuation ---")
    try:
        df_val = ak1.get_valuation(symbol, count=1)
        print(f"get_valuation returned {len(df_val)} rows")
        print(df_val.head())
    except Exception as e:
        print(f"get_valuation failed: {e}")

if __name__ == "__main__":
    test_jq_apis()
