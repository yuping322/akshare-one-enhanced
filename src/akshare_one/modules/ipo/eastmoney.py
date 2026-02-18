"""
Eastmoney IPO data provider.
"""

import pandas as pd

from .base import IPOProvider


class EastmoneyIPOProvider(IPOProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_new_stocks(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_new_a_spot_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "涨跌额": "change",
                    "成交量": "volume",
                    "成交额": "amount",
                    "上市日期": "list_date",
                }
            )
            cols = ["symbol", "name", "price", "pct_change", "change", "volume", "amount", "list_date"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_ipo_info(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_ipo_summary_cninfo()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "公司代码": "symbol",
                    "公司简称": "name",
                    "发行价": "issue_price",
                    "申购日期": "subscription_date",
                    "上市日期": "list_date",
                }
            )
            cols = ["symbol", "name", "issue_price", "subscription_date", "list_date"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
