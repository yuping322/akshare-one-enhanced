import akshare_one.jq_compat as ak1
import pandas as pd
import numpy as np

def test_alpha_engine():
    print("--- Testing Alpha Engine ---")
    
    # 1. Preprocessing Test
    print("Checking Preprocessing (Winsorize)...")
    s = pd.Series([1, 2, 3, 100, -50, 4, 5])
    w = ak1.winsorize_med(s)
    print(f"  Original: {s.tolist()}")
    print(f"  Winsorized: {w.tolist()}")
    
    # 2. Factor Calculation Test
    print("\nChecking Factor Calculation...")
    try:
        mc = ak1.compute_market_cap("600519.XSHG", count=1)
        print(f"  Market Cap (600519): {mc}")
    except Exception as e:
        print(f"  Market Cap error: {e}")
        
    # 3. Signal Test
    print("\nChecking Signals (MA Cross)...")
    try:
        close = pd.Series(np.random.randn(100).cumsum() + 100)
        cross = ak1.compute_ma_cross(close)
        print(f"  MA Cross signal tail: {cross.tail(5).tolist()}")
    except Exception as e:
        print(f"  MA Cross error: {e}")

    # 4. Indicators Test
    print("\nChecking RSRS Indicator...")
    try:
        # Mocking data for RSRS
        h = pd.Series(np.random.randn(700).cumsum() + 100)
        l = h - 2
        rsrs = ak1.compute_rsrs(h, l)
        print(f"  RSRS tail: {rsrs.tail(3).tolist()}")
    except Exception as e:
        print(f"  RSRS error: {e}")

if __name__ == "__main__":
    test_alpha_engine()
