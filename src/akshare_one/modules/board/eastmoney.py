"""
Eastmoney board data provider.
"""

import pandas as pd

from .base import BoardProvider


class EastmoneyBoardProvider(BoardProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_kcb_stocks(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_kcb_spot_em()
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
                    "换手率": "turnover",
                }
            )
            cols = ["symbol", "name", "price", "pct_change", "change", "volume", "amount", "turnover"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_cyb_stocks(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_cyb_spot_em()
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
                    "换手率": "turnover",
                }
            )
            cols = ["symbol", "name", "price", "pct_change", "change", "volume", "amount", "turnover"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
