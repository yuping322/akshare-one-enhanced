"""
src/akshare_one/modules/bond/akshare.py
AkShare data provider for bonds.
"""

import pandas as pd
import akshare as ak
from typing import Optional
from .base import BondProvider, BondFactory


@BondFactory.register("akshare")
class AkShareBondProvider(BondProvider):
    _API_MAP = {
        "get_bond_list": {
            "ak_func": "bond_cb_jsl",
        },
        "get_bond_hist": {
            "ak_func": "bond_zh_hs_cov_daily",
            "params": {"symbol": "symbol"},
        },
        "get_bond_realtime": {
            "ak_func": "bond_cb_jsl",
        },
        "get_bond_spot": {
            "ak_func": "bond_cb_jsl",
        },
    }

    def get_source_name(self) -> str:
        return "akshare"

    def get_bond_list(self) -> pd.DataFrame:
        """Fetch active conversion bonds and their key metrics."""
        try:
            df = ak.bond_cb_jsl()
            if df.empty:
                return pd.DataFrame()

            # Standardize column names based on actual AkShare output
            df = df.rename(
                columns={
                    "代码": "bond_code",
                    "转债名称": "bond_name",
                    "正股代码": "stock_code",
                    "正股名称": "stock_name",
                    "现价": "close",
                    "转股价": "conversion_price",
                    "转股价值": "conversion_value",
                    "转股溢价率": "premium_rate",
                    "纯债价值": "bond_value",
                    "双低": "double_low",
                    "剩余年限": "remain_years",
                    "到期时间": "list_date",
                }
            )

            # Format stock codes to JQ style
            def fmt_code(c):
                c = str(c).zfill(6)
                return f"{c}.XSHG" if c.startswith("6") else f"{c}.XSHE"

            df["stock_code"] = df["stock_code"].apply(fmt_code)
            return df
        except Exception:
            return pd.DataFrame()

    def get_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical price data for a bond."""
        try:
            # Conversion bonds often use fund_etf_hist_em for price history in AkShare
            clean_sym = symbol.split(".")[0]
            df = ak.bond_zh_hs_cov_daily(symbol=f"sh{clean_sym}" if clean_sym.startswith("11") else f"sz{clean_sym}")
            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "date": "date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                }
            )
            df["date"] = pd.to_datetime(df["date"])
            df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
            return df
        except Exception:
            return pd.DataFrame()

    def get_bond_realtime(self) -> pd.DataFrame:
        """Get realtime quotes for all conversion bonds."""
        return self.get_bond_spot()

    def get_bond_spot(self) -> pd.DataFrame:
        """Get realtime quotes for all conversion bonds."""
        return self.get_bond_list()

    def get_bond_premium(self, symbol: str) -> pd.DataFrame:
        """Get detailed premium info for a specific bond."""
        df_all = self.get_bond_list()
        if df_all.empty:
            return pd.DataFrame()

        # Strip suffix for matching if needed
        clean_symbol = symbol.split(".")[0]
        df_filtered = df_all[df_all["bond_code"] == clean_symbol]
        return df_filtered
