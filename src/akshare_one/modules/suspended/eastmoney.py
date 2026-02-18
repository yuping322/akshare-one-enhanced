"""
Eastmoney suspended stocks data provider.
"""

import pandas as pd

from .base import SuspendedProvider


class EastmoneySuspendedProvider(SuspendedProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_suspended_stocks(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_tfp_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "停牌日期": "suspend_date",
                    "预计复牌日期": "expected_resume_date",
                    "停牌原因": "reason",
                }
            )
            cols = ["symbol", "name", "suspend_date", "expected_resume_date", "reason"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
