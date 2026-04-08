import akshare_one
from akshare_one import jq_compat
import pandas as pd

def test_valuation():
    print("Testing get_valuation...")
    # Test single stock
    df = jq_compat.get_valuation("600519.XSHG", date="2023-12-01")
    print(f"Valuation for 600519.XSHG:\n{df.head()}")
    
    # Test batch
    df_batch = jq_compat.get_valuation(["600519.XSHG", "000858.XSHE"], date="2023-12-01")
    print(f"Batch valuation:\n{df_batch}")
    return not df.empty and not df_batch.empty

def test_fundamentals():
    print("\nTesting get_fundamentals...")
    
    # Mock a query object
    class Query:
        def __init__(self, table, code=None, fields=None):
            self.table = table
            self.code = code
            self.fields = fields

    # Test valuation table via get_fundamentals
    q_val = Query("valuation", code="600519.XSHG")
    df_val = jq_compat.get_fundamentals(q_val, date="2023-12-01")
    print(f"Fundamentals (valuation):\n{df_val}")
    
    # Test income table
    q_inc = Query("income", code="600519.XSHG")
    df_inc = jq_compat.get_fundamentals(q_inc, statDate="2023")
    print(f"Fundamentals (income):\n{df_inc.head()}")
    
    return not df_val.empty and not df_inc.empty

if __name__ == "__main__":
    try:
        v_ok = test_valuation()
        f_ok = test_fundamentals()
        if v_ok and f_ok:
            print("\nAll fundamental and valuation tests passed!")
        else:
            print("\nSome tests failed (empty results).")
    except Exception as e:
        print(f"\nVerification failed with error: {e}")
        import traceback
        traceback.print_exc()
