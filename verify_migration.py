import akshare_one
from akshare_one import risk, strategy
import pandas as pd
import numpy as np

def test_risk_module():
    print("Testing risk module...")
    # Test volatility with a smaller window for short test data
    prices = [100, 101, 102, 103, 102, 101, 100, 99, 98, 97, 98, 99, 100, 101, 102]
    vol = risk.compute_volatility(prices, window=5)
    print(f"Volatility (window=5): {vol.iloc[-1]}")
    
    # Test drawdown
    dd = risk.compute_max_drawdown([100, 105, 102, 108, 104])
    print(f"Max Drawdown: {dd}")
    
    # Test position sizing with mock DataFrame for ATR
    mock_df = pd.DataFrame({
        'open': [100]*15,
        'high': [102]*15,
        'low': [98]*15,
        'close': prices,
        'date': pd.date_range('2023-01-01', periods=15)
    })
    # Pass DataFrame directly as 'symbol' due to polymorphism
    # Signature: atr_based_position_size(symbol, total_capital, ...)
    pos = risk.atr_based_position_size(mock_df, 100000, risk_per_trade=0.01)
    print(f"Position size (using mock DataFrame): {pos}")
    print("Risk module seems OK.")

def test_strategy_module():
    print("\nTesting strategy module...")
    # Test helpers
    ma = strategy.calculate_ma([10, 11, 12, 13, 14], 3)
    print(f"MA: {ma.iloc[-1]}")
    
    # Test scanner
    scanner = strategy.StrategyScanner()
    print("Scanner initialized.")
    
    # Test timer rules
    calendar = strategy.TradingDayCalendar()
    print("Calendar initialized.")
    
    print("Strategy module seems OK.")

if __name__ == "__main__":
    try:
        test_risk_module()
        test_strategy_module()
        print("\nAll migrated modules are accessible and functional!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        import traceback
        traceback.print_exc()
