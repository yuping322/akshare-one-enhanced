"""
Eastmoney performance data provider.
"""

import pandas as pd

from .base import PerformanceProvider


class EastmoneyPerformanceProvider(PerformanceProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_performance_forecast(self, date: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_yjyg_em(date=date.replace("-", ""))
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票简称": "name",
                    "预测指标": "indicator",
                    "业绩变动": "change",
                    "预测数值": "forecast_value",
                    "业绩变动幅度": "change_pct",
                    "预告类型": "forecast_type",
                    "公告日期": "announce_date",
                }
            )
            cols = [
                "symbol",
                "name",
                "indicator",
                "change",
                "forecast_value",
                "change_pct",
                "forecast_type",
                "announce_date",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_performance_express(self, date: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_yjkb_em(date=date.replace("-", ""))
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票简称": "name",
                    "每股收益": "eps",
                    "营业收入-营业收入": "revenue",
                    "营业收入-同比增长": "revenue_yoy",
                    "净利润-净利润": "net_profit",
                    "净利润-同比增长": "profit_yoy",
                    "每股净资产": "bps",
                    "净资产收益率": "roe",
                    "所处行业": "industry",
                    "公告日期": "announce_date",
                }
            )
            cols = [
                "symbol",
                "name",
                "eps",
                "revenue",
                "revenue_yoy",
                "net_profit",
                "profit_yoy",
                "bps",
                "roe",
                "industry",
                "announce_date",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
