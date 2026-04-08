import akshare as ak
try:
    df = ak.bond_cb_jsl()
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head(2))
except Exception as e:
    print("Error:", e)
