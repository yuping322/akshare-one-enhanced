import akshare_one.jq_compat as ak1
import pandas as pd

def test_industry_and_sentiment():
    print("--- Testing Industry & Sentiment Engine ---")
    
    # 1. Industry Test
    print("Checking Industry Stocks (Food & Beverage)...")
    stocks = ak1.get_industry_stocks("食品饮料")
    print(f"  Count: {len(stocks)}")
    if stocks: print(f"  Sample: {stocks[:3]}")
    
    # 2. Sentiment Test (Macro)
    print("\nChecking FED Model (Macro Valuation)...")
    fed = ak1.compute_fed_model()
    print(f"  FED Value: {fed.get('fed', 0):.4f}")
    print(f"  PE (HS300): {fed.get('pe', 0):.2f}")
    
    # 3. Sentiment Test (Volume/PB)
    print("\nChecking Crowding & Net Ratio...")
    crowd = ak1.compute_crowding_ratio()
    below = ak1.compute_below_net_ratio()
    print(f"  Crowding Ratio: {crowd.get('ratio', 0)*100:.2f}%")
    print(f"  Below Net Ratio: {below.get('ratio', 0)*100:.2f}%")

if __name__ == "__main__":
    test_industry_and_sentiment()
