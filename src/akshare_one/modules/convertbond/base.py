"""
Base classes for convertible bond (可转债) data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ConvertBondProvider(BaseProvider):
    """Base class for convertible bond data providers."""

    def get_data_type(self) -> str:
        return "convertbond"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_convert_bond_list(self) -> pd.DataFrame:
        """获取可转债列表"""
        return self._execute_api_mapped("get_convert_bond_list")

    def get_convert_bond_info(self, symbol: str) -> pd.DataFrame:
        """获取可转债详细信息"""
        return self._execute_api_mapped("get_convert_bond_info", symbol=symbol)

    def get_convert_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取可转债历史行情"""
        return self._execute_api_mapped(
            "get_convert_bond_hist", symbol=symbol, start_date=start_date, end_date=end_date
        )

    def get_convert_bond_spot(self) -> pd.DataFrame:
        """获取可转债实时行情"""
        return self._execute_api_mapped("get_convert_bond_spot")

    def get_convert_bond_premium(self, symbol: str) -> pd.DataFrame:
        """获取可转债溢价率"""
        return self._execute_api_mapped("get_convert_bond_premium", symbol=symbol)

    def get_convert_bond_by_stock(self, stock_code: str) -> pd.DataFrame:
        """获取正股对应的可转债"""
        return self._execute_api_mapped("get_convert_bond_by_stock", stock_code=stock_code)

    def get_convert_bond_quote(self, symbol: str) -> pd.DataFrame:
        """获取可转债实时报价"""
        return self._execute_api_mapped("get_convert_bond_quote", symbol=symbol)


class ConvertBondFactory(BaseFactory[ConvertBondProvider]):
    """Factory for convertible bond data providers."""

    _providers: dict[str, type[ConvertBondProvider]] = {}
