"""
AkShare provider for convertible bond (可转债) data.

This module implements the convertible bond data provider using AkShare as the data source.
Uses AkShareAdapter to handle function name drift across versions.
"""

import pandas as pd

from .base import ConvertBondFactory, ConvertBondProvider


@ConvertBondFactory.register("akshare")
class AkShareConvertBondProvider(ConvertBondProvider):
    """
    Convertible bond data provider using AkShare as the data source.

    Provides interfaces to fetch convertible bond data including:
    - Convertible bond list
    - Convertible bond details
    - Historical quotes
    - Realtime quotes
    - Premium rates
    """

    _API_MAP = {
        "get_convert_bond_list": {
            "ak_func": "bond_zh_cov",
        },
        "get_convert_bond_info": {
            "ak_func": "bond_zh_cov_info",
            "params": {"symbol": "symbol"},
        },
        "get_convert_bond_hist": {
            "ak_func": "bond_zh_cov_hist",
            "params": {"symbol": "symbol", "start_date": "start_date", "end_date": "end_date"},
        },
        "get_convert_bond_spot": {
            "ak_func": "bond_zh_cov_spot",
        },
        "get_convert_bond_premium": {
            "ak_func": "bond_zh_cov_value",
            "params": {"symbol": "symbol"},
        },
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "akshare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from AkShare.

        This method is not used directly; specific methods fetch their own data.
        """
        return pd.DataFrame()

    def get_convert_bond_list(self) -> pd.DataFrame:
        """
        获取可转债列表

        Returns:
            pd.DataFrame: 可转债列表数据
        """
        return self._execute_api_mapped("get_convert_bond_list")

    def get_convert_bond_info(self, symbol: str) -> pd.DataFrame:
        """
        获取可转债详细信息

        Args:
            symbol: 可转债代码

        Returns:
            pd.DataFrame: 可转债详细信息
        """
        return self._execute_api_mapped("get_convert_bond_info", symbol=symbol)

    def get_convert_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取可转债历史行情

        Args:
            symbol: 可转债代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 可转债历史行情数据
        """
        self.validate_date_range(start_date, end_date)
        return self._execute_api_mapped(
            "get_convert_bond_hist", symbol=symbol, start_date=start_date, end_date=end_date
        )

    def get_convert_bond_spot(self) -> pd.DataFrame:
        """
        获取可转债实时行情

        Returns:
            pd.DataFrame: 可转债实时行情数据
        """
        return self._execute_api_mapped("get_convert_bond_spot")

    def get_convert_bond_premium(self, symbol: str) -> pd.DataFrame:
        """
        获取可转债溢价率

        Args:
            symbol: 可转债代码

        Returns:
            pd.DataFrame: 可转债溢价率数据
        """
        return self._execute_api_mapped("get_convert_bond_premium", symbol=symbol)

    def get_convert_bond_by_stock(self, stock_code: str) -> pd.DataFrame:
        """
        获取正股对应的可转债

        Args:
            stock_code: 正股代码

        Returns:
            pd.DataFrame: 正股对应的可转债列表
        """
        all_bonds = self.get_convert_bond_list()
        if not all_bonds.empty and "正股代码" in all_bonds.columns:
            return all_bonds[all_bonds["正股代码"] == stock_code]
        return pd.DataFrame()

    def get_convert_bond_quote(self, symbol: str) -> pd.DataFrame:
        """
        获取可转债实时报价

        Args:
            symbol: 可转债代码

        Returns:
            pd.DataFrame: 可转债实时报价数据
        """
        df = self.get_convert_bond_spot()
        if not df.empty and "债券代码" in df.columns:
            return df[df["债券代码"] == symbol]
        return pd.DataFrame()
