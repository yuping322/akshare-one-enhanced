import akshare_one.jq_compat as ak1
import pandas as pd
import numpy as np

def test_api_existence():
    groups = {
        "Market": ["get_price", "get_bars", "history", "attribute_history", "get_valuation", "get_market", "get_detailed_quote", "get_ticks_enhanced"],
        "Securities": ["get_all_securities", "get_security_info"],
        "Date": ["get_shifted_date", "get_previous_trade_date", "is_trade_date", "get_trade_dates_between", "clear_trade_days_cache"],
        "Indicators": ["MA", "EMA", "MACD", "KDJ", "RSI", "BOLL", "ATR"],
        "Filter": ["filter_st", "filter_paused", "filter_limit_up", "filter_new_stocks", "apply_common_filters"],
        "Stats": ["get_ols", "get_zscore", "get_rank", "get_num", "get_beta"],
        "Order": ["order_shares", "order_target_percent", "rebalance_portfolio"],
        "Cache": ["CurrentDataCache", "get_current_data_cached", "BatchDataLoader"],
        "Money Flow": ["get_money_flow", "get_sector_money_flow", "get_money_flow_rank"],
        "Billboard": ["get_billboard_list", "get_institutional_holdings", "get_billboard_hot_stocks"],
        "Financial": ["bank_indicator", "security_indicator", "insurance_indicator"]
    }
    
    print("--- API Existence Check ---")
    missing = []
    for group, apis in groups.items():
        print(f"Checking {group}...")
        for api in apis:
            if hasattr(ak1, api):
                print(f"  [OK] {api}")
            else:
                print(f"  [MISSING] {api}")
                missing.append(api)
    
    if not missing:
        print("\nAll target APIs are present in jq_compat!")
    else:
        print(f"\nMissing APIs: {missing}")

def test_basic_calls():
    print("\n--- Basic Functional Tests ---")
    try:
        # Date
        d = ak1.get_previous_trade_date("2024-01-01")
        print(f"Date check: {d}")
        
        # Indicator
        data = np.random.random(100)
        ma = ak1.MA(pd.Series(data), 5)
        print(f"MA check: OK")
        
        # Security Info
        info = ak1.get_security_info("600519.XSHG")
        print(f"Security Info check: {info.name if info else 'None'}")
        
        # Filter
        stocks = ["600519.XSHG", "000001.XSHE"]
        filtered = ak1.filter_kcb_stock(stocks)
        print(f"Filter check: {filtered}")
        
    except Exception as e:
        print(f"Functional test error: {e}")

if __name__ == "__main__":
    test_api_existence()
    test_basic_calls()
