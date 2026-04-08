import akshare_one.jq_compat as ak1
import pandas as pd

def test_bond_and_fund():
    print("--- Testing Bond & Fund Engine ---")
    
    # 1. Bond Test
    print("Checking Conversion Bond List...")
    bonds = ak1.get_bond_list_jq()
    print(f"  Total Bonds: {len(bonds)}")
    if not bonds.empty:
        print(f"  Sample Bonds: {bonds['bond_code'].head(3).tolist()}")
        
        # Test premium for a sample
        sample_bond = bonds['bond_code'].iloc[0]
        print(f"\nChecking Premium for {sample_bond}...")
        premium = ak1.get_bond_premium_jq(sample_bond)
        if not premium.empty:
            print(f"  Premium Rate: {premium['premium_rate'].iloc[0]:.2f}%")
            print(f"  Underlying Stock: {premium['stock_code'].iloc[0]}")
    
    # 2. Fund Test
    print("\nChecking ETF List...")
    etfs = ak1.get_fund_list(fund_type="etf")
    print(f"  Total ETFs: {len(etfs)}")
    if not etfs.empty:
        sample_etf = etfs['symbol'].iloc[0]
        print(f"  Sample ETF: {sample_etf}")
        
        # Test NAV
        nav = ak1.get_fund_nav(sample_etf)
        print(f"  NAV History Count: {len(nav)}")

if __name__ == "__main__":
    test_bond_and_fund()
