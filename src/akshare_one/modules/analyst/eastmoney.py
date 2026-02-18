"""
Eastmoney analyst data provider.
"""

import pandas as pd

from .base import AnalystProvider


class EastmoneyAnalystProvider(AnalystProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_analyst_rank(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_analyst_rank_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "分析师名称": "analyst_name",
                    "分析师单位": "company",
                    "年度指数": "annual_index",
                    "2024年收益率": "return_ytd",
                    "3个月收益率": "return_3m",
                    "6个月收益率": "return_6m",
                    "12个月收益率": "return_12m",
                    "行业": "industry",
                    "更新日期": "update_date",
                }
            )
            cols = [
                "analyst_name",
                "company",
                "annual_index",
                "return_ytd",
                "return_3m",
                "return_6m",
                "return_12m",
                "industry",
                "update_date",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_research_report(self, symbol: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_research_report_em(symbol=symbol)
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票简称": "name",
                    "报告名称": "report_title",
                    "东财评级": "rating",
                    "机构": "institution",
                    "日期": "date",
                    "近一月个股研报数": "report_count",
                }
            )
            cols = [
                "symbol",
                "name",
                "report_title",
                "rating",
                "institution",
                "date",
                "report_count",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
