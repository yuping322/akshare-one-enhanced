"""
Eastmoney sentiment data provider.
"""

import time

import pandas as pd

from ...metrics import get_stats_collector
from .base import SentimentFactory, SentimentProvider


@SentimentFactory.register("eastmoney")
class EastmoneySentimentProvider(SentimentProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_hot_rank(self) -> pd.DataFrame:
        import akshare as ak

        start_time = time.time()

        try:
            df = ak.stock_hot_rank_em()
            if df.empty:
                result = pd.DataFrame()
                duration_ms = (time.time() - start_time) * 1000
                stats_collector = get_stats_collector()
                stats_collector.record_request("eastmoney", duration_ms, True)
                return result
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
            result = df[[c for c in cols if c in df.columns]]

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result
        except Exception:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            return pd.DataFrame()

    def get_stock_comment(self) -> pd.DataFrame:
        import akshare as ak

        start_time = time.time()

        try:
            df = ak.stock_comment_em()
            if df.empty:
                result = pd.DataFrame()
                duration_ms = (time.time() - start_time) * 1000
                stats_collector = get_stats_collector()
                stats_collector.record_request("eastmoney", duration_ms, True)
                return result
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
            result = df[[c for c in cols if c in df.columns]]

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result
        except Exception:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            return pd.DataFrame()
