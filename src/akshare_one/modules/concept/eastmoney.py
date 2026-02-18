"""
Eastmoney concept sector data provider.
"""

import pandas as pd

from .base import ConceptProvider


class EastmoneyConceptProvider(ConceptProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_concept_list(self) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_board_concept_name_em()
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "排名": "rank",
                    "板块名称": "name",
                    "板块代码": "code",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "换手率": "turnover",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股票": "leading_stock",
                }
            )
            cols = [
                "rank",
                "name",
                "code",
                "price",
                "pct_change",
                "turnover",
                "up_count",
                "down_count",
                "leading_stock",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_concept_stocks(self, concept: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_board_concept_cons_em(symbol=concept)
            if df.empty:
                return pd.DataFrame()
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "成交量": "volume",
                    "成交额": "amount",
                    "换手率": "turnover",
                    "市盈率-动态": "pe_ttm",
                    "市净率": "pb",
                }
            )
            cols = [
                "symbol",
                "name",
                "price",
                "pct_change",
                "volume",
                "amount",
                "turnover",
                "pe_ttm",
                "pb",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
