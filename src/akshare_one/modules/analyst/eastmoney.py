"""
Eastmoney analyst data provider.
"""

import pandas as pd

from .base import AnalystProvider, AnalystFactory


@AnalystFactory.register("eastmoney")
class EastmoneyAnalystProvider(AnalystProvider):
    _API_MAP = {
        "get_analyst_rank": {
            "ak_func": "stock_analyst_rank_em",
        },
        "get_research_report": {
            "ak_func": "stock_research_report_em",
            "params": {"symbol": "symbol"},
        },
    }

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

EastmoneyAnalyst = EastmoneyAnalystProvider
