"""
Eastmoney sentiment data provider.
"""

import pandas as pd

from .base import SentimentProvider


class EastmoneySentimentProvider(SentimentProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_hot_rank(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_hot_rank_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "当前排名": "rank",
                    "代码": "symbol",
                    "股票名称": "name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                }
            )
            cols = ["rank", "symbol", "name", "price", "pct_change"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_stock_comment(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_comment_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "换手率": "turnover",
                    "综合得分": "score",
                    "关注指数": "attention_index",
                    "交易日": "trade_date",
                }
            )
            cols = [
                "symbol",
                "name",
                "price",
                "pct_change",
                "turnover",
                "score",
                "attention_index",
                "trade_date",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
