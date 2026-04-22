"""
Shareholder depth data provider - extended shareholder APIs.
"""

import pandas as pd

from .....core.base import BaseProvider
from .base import ShareholderFactory


class ShareholderDepthProvider(BaseProvider):
    """Extended provider for shareholder depth data."""

    def get_data_type(self) -> str:
        return "shareholderdepth"

    def get_update_frequency(self) -> str:
        return "quarterly"

    def get_delay_minutes(self) -> int:
        return 0

    def get_shareholder_structure(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get shareholder structure information."""
        return self._execute_api_mapped("get_shareholder_structure", symbol=symbol, **kwargs)

    def get_shareholder_concentration(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get shareholder concentration information."""
        return self._execute_api_mapped("get_shareholder_concentration", symbol=symbol, **kwargs)

    def get_top_float_shareholders(self, symbol: str, date: str = None, **kwargs) -> pd.DataFrame:
        """Get top float shareholders."""
        return self._execute_api_mapped("get_top_float_shareholders", symbol=symbol, date=date, **kwargs)


class ShareholderDepthFactory(ShareholderFactory):
    """Factory for shareholder depth data providers."""

    pass


@ShareholderDepthFactory.register("eastmoney")
class EastMoneyShareholderDepthProvider(ShareholderDepthProvider):
    """Shareholder depth data provider using EastMoney."""

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_shareholder_structure(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get shareholder structure from EastMoney."""
        return self.akshare_adapter.call("stock_gdfx_free_holding_analyse_em", symbol=symbol)

    def get_shareholder_concentration(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get shareholder concentration from EastMoney."""
        return self.akshare_adapter.call("stock_gdfx_holding_detail_em", symbol=symbol)

    def get_top_float_shareholders(self, symbol: str, date: str = None, **kwargs) -> pd.DataFrame:
        """Get top float shareholders from EastMoney."""
        if date:
            return self.akshare_adapter.call("stock_gdfx_free_top_10_em", symbol=symbol, date=date)
        return self.akshare_adapter.call("stock_gdfx_free_top_10_em", symbol=symbol)
