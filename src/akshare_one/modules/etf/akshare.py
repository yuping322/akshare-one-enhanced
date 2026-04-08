"""
src/akshare_one/modules/etf/akshare.py
AkShare data provider for ETFs and funds.
"""

import pandas as pd
import akshare as ak
from .base import ETFProvider, ETFFactory


@ETFFactory.register("akshare")
class AkShareETFProvider(ETFProvider):
    _API_MAP = {
        "get_etf_hist": {
            "ak_func": None,
        },
        "get_etf_spot": {
            "ak_func": None,
        },
        "get_etf_list": {
            "ak_func": "fund_etf_spot_em",
        },
        "get_fund_manager": {
            "ak_func": None,
        },
        "get_fund_rating": {
            "ak_func": None,
        },
        "get_fund_nav": {
            "ak_func": "fund_etf_fund_info_em",
            "params": {"symbol": "fund"},
        },
    }

    def get_source_name(self) -> str:
        return "akshare"

    def get_etf_list(self, fund_type: str = "etf") -> pd.DataFrame:
        """Fetch list of funds from AkShare."""
        try:
            if fund_type == "etf":
                df = ak.fund_etf_spot_em()
            elif fund_type == "lof":
                df = ak.fund_lof_spot_em()
            elif fund_type == "reits":
                df = ak.fund_reits_spot_em()
            else:
                return pd.DataFrame()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "成交额": "amount",
                }
            )
            return df
        except Exception:
            return pd.DataFrame()

    def get_fund_nav(self, symbol: str) -> pd.DataFrame:
        """Fetch fund Net Asset Value (NAV) history."""
        try:
            df = ak.fund_etf_fund_info_em(fund=symbol)
            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "净值日期": "date",
                    "单位净值": "unit_nav",
                    "累计净值": "acc_nav",
                    "日增长率": "daily_growth",
                }
            )
            df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception:
            return pd.DataFrame()
