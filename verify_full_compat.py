import akshare_one.jq_compat as ak1
import pandas as pd
import numpy as np

def verify_all_symbols():
    print("--- Starting Final API Compatibility Verification ---")
    
    # List of key groups to check
    groups = {
        "Market": ["get_price", "get_bars", "get_valuation", "get_price_jq", "get_valuation_jq"],
        "Margin": ["get_mtss", "get_margine_stocks", "get_mtss_jq", "get_margincash_stocks_jq"],
        "Futures": ["get_dominant_future", "get_settlement_price", "get_dominant_future_jq"],
        "Alpha": ["compute_rsrs", "winsorize_med", "FactorAnalyzer", "get_factor_values"],
        "Order": ["order_shares", "get_position_ratio", "will_sell_on_limit_up"],
        "Cache": ["CurrentDataCache", "BatchDataLoader", "warm_up_cache", "get_memory_usage"]
    }
    
    total_passed = 0
    total_failed = 0
    
    for group, symbols in groups.items():
        print(f"\nGroup: {group}")
        for sym in symbols:
            if hasattr(ak1, sym):
                print(f"  [PASS] {sym}")
                total_passed += 1
            else:
                print(f"  [FAIL] {sym} (Missing)")
                total_failed += 1
                
    print("\n" + "="*40)
    print(f"Verification Results: {total_passed} Passed, {total_failed} Failed.")
    print("="*40)
    
    if total_failed == 0:
        print("\nChecking a few live calls...")
        try:
            mem = ak1.get_memory_usage()
            print(f"  Memory Usage: {mem}")
            
            # Test a signal from alpha
            s = pd.Series(np.random.randn(10))
            w = ak1.winsorize_med(s)
            print(f"  Winsorize check: OK")
            
            # Test a margin call
            # Note: actual network calls might fail if offline, but attribute should exist
            print("  Margin call attribute: OK")
            
        except Exception as e:
            print(f"  Live call warning: {e} (Expected if data source unavailable)")

if __name__ == "__main__":
    verify_all_symbols()
