"""
EastMoney provider for shareholder depth data.

This module implements shareholder depth data provider using EastMoney API.
"""

import pandas as pd

from .base import ShareholderDepthFactory, ShareholderDepthProvider


@ShareholderDepthFactory.register("eastmoney")
class EastMoneyShareholderDepthProvider(ShareholderDepthProvider):
    """
    Shareholder depth data provider using EastMoney.

    Provides shareholder structure, shareholder concentration,
    and top float shareholders.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_shareholder_structure(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get shareholder structure from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Shareholder structure data
        """
        return self.akshare_adapter.call("stock_gdfx_free_holding_analyse_em", symbol=symbol)

    def get_shareholder_concentration(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get shareholder concentration from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Shareholder concentration data
        """
        return self.akshare_adapter.call("stock_gdfx_holding_detail_em", symbol=symbol)

    def get_top_float_shareholders(self, symbol: str, date: str = None, **kwargs) -> pd.DataFrame:
        """
        Get top float shareholders from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Top float shareholders data
        """
        if date:
            return self.akshare_adapter.call("stock_gdfx_free_top_10_em", symbol=symbol, date=date)
        return self.akshare_adapter.call("stock_gdfx_free_top_10_em", symbol=symbol)
