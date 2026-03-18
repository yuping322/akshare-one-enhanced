from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class InfoDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "info"

    def get_data_type(self) -> str:
        return "info"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_basic_info()

    @abstractmethod
    def get_basic_info(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetches basic information

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame:
            - symbol: 股票代码
            - name: 股票名称
            - industry: 所属行业
            - listing_date: 上市日期
            - total_shares: 总股本
            - float_shares: 流通股
            - total_market_cap: 总市值
            - float_market_cap: 流通市值
        """
        pass
