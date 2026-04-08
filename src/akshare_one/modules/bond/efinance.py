"""
Efinance bond data provider.

This module implements the bond data provider using efinance as the data source.
"""

import pandas as pd

from .base import BondFactory, BondProvider


@BondFactory.register("efinance")
class EfinanceBondProvider(BondProvider):
    """
    Bond data provider using efinance as the data source.

    Efinance provides comprehensive bond data including:
    - Bond list with base info
    - Historical K-line data
    - Realtime quotes
    - Fund flow data
    """

    _API_MAP = {
        "get_bond_list": {
            "ak_func": None,
        },
        "get_bond_hist": {
            "ak_func": None,
        },
        "get_bond_realtime": {
            "ak_func": None,
        },
        "get_bond_spot": {
            "ak_func": None,
        },
    }

    def __init__(self, **kwargs):
        """Initialize the efinance bond provider."""
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_bond_list(self) -> pd.DataFrame:
        """
        Get convertible bond list from efinance.

        Returns:
            pd.DataFrame: Bond list
        """
        import efinance as ef

        try:
            df = ef.bond.get_all_base_info()

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "债券代码": "bond_code",
                    "债券名称": "name",
                    "正股代码": "underlying_symbol",
                    "正股名称": "underlying_name",
                }
            )

            cols = [
                "bond_code",
                "name",
                "underlying_symbol",
                "underlying_name",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get bond historical data from efinance.

        Args:
            symbol: Bond symbol (e.g., '123050')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Historical data
        """
        import efinance as ef

        try:
            beg = start_date.replace("-", "")
            end = end_date.replace("-", "")

            df = ef.bond.get_quote_history(symbol, beg=beg, end=end, klt=101)

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "最高": "high",
                    "最低": "low",
                    "收盘": "close",
                    "成交量": "volume",
                    "成交额": "amount",
                }
            )

            df["symbol"] = symbol

            df["date"] = pd.to_datetime(df["date"])

            cols = ["date", "symbol", "open", "high", "low", "close", "volume", "amount"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_realtime(self) -> pd.DataFrame:
        """Get bond realtime quotes (alias for get_bond_spot)."""
        return self.get_bond_spot()

    def get_bond_spot(self, bond_codes: list[str] | None = None) -> pd.DataFrame:
        """
        Get bond realtime quotes from efinance.

        Args:
            bond_codes: Optional list of bond codes to query

        Returns:
            pd.DataFrame: Realtime bond data
        """
        import efinance as ef

        try:
            if bond_codes:
                df = ef.bond.get_realtime_quotes(bond_codes)
            else:
                df = ef.bond.get_realtime_quotes()

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "债券代码": "bond_code",
                    "债券名称": "name",
                    "正股代码": "underlying_symbol",
                    "正股名称": "underlying_name",
                    "最新价": "price",
                    "涨跌幅": "pct_change",
                    "成交量": "volume",
                    "成交额": "amount",
                    "换手率": "turnover_rate",
                }
            )

            cols = [
                "bond_code",
                "name",
                "underlying_symbol",
                "underlying_name",
                "price",
                "pct_change",
                "volume",
                "amount",
                "turnover_rate",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_info(self, bond_codes: list[str] | str) -> pd.DataFrame:
        """
        Get bond base info from efinance.

        Args:
            bond_codes: Bond code or list of bond codes

        Returns:
            pd.DataFrame: Bond base info
        """
        import efinance as ef

        try:
            if isinstance(bond_codes, str):
                bond_codes = [bond_codes]

            df = ef.bond.get_base_info(bond_codes)

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "债券代码": "bond_code",
                    "债券名称": "name",
                    "正股代码": "underlying_symbol",
                    "正股名称": "underlying_name",
                }
            )

            cols = [
                "bond_code",
                "name",
                "underlying_symbol",
                "underlying_name",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_deal_detail(self, bond_code: str) -> pd.DataFrame:
        """
        Get bond deal details from efinance.

        Args:
            bond_code: Bond code

        Returns:
            pd.DataFrame: Deal details
        """
        import efinance as ef

        try:
            df = ef.bond.get_deal_detail(bond_code)

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "时间": "time",
                    "价格": "price",
                    "成交量": "volume",
                    "成交额": "amount",
                    "性质": "direction",
                }
            )

            df["bond_code"] = bond_code

            cols = ["bond_code", "time", "price", "volume", "amount", "direction"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_history_bill(self, bond_code: str) -> pd.DataFrame:
        """
        Get bond historical fund flow from efinance.

        Args:
            bond_code: Bond code

        Returns:
            pd.DataFrame: Historical fund flow
        """
        import efinance as ef

        try:
            df = ef.bond.get_history_bill(bond_code)

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "日期": "date",
                    "主力净流入": "main_net_inflow",
                    "小单净流入": "small_net_inflow",
                    "中单净流入": "medium_net_inflow",
                    "大单净流入": "large_net_inflow",
                    "超大单净流入": "xlarge_net_inflow",
                }
            )

            df["bond_code"] = bond_code

            cols = [
                "bond_code",
                "date",
                "main_net_inflow",
                "small_net_inflow",
                "medium_net_inflow",
                "large_net_inflow",
                "xlarge_net_inflow",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_today_bill(self, bond_code: str) -> pd.DataFrame:
        """
        Get bond today's fund flow from efinance.

        Args:
            bond_code: Bond code

        Returns:
            pd.DataFrame: Today's fund flow
        """
        import efinance as ef

        try:
            df = ef.bond.get_today_bill(bond_code)

            if df is None or df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "时间": "time",
                    "主力净流入": "main_net_inflow",
                    "小单净流入": "small_net_inflow",
                    "中单净流入": "medium_net_inflow",
                    "大单净流入": "large_net_inflow",
                    "超大单净流入": "xlarge_net_inflow",
                }
            )

            df["bond_code"] = bond_code

            cols = [
                "bond_code",
                "time",
                "main_net_inflow",
                "small_net_inflow",
                "medium_net_inflow",
                "large_net_inflow",
                "xlarge_net_inflow",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
