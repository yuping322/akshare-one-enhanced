"""
Share change depth data provider - share freeze and capital changes.
"""

import pandas as pd

from .....core.base import BaseProvider
from .base import ShareholderFactory


class ShareChangeDepthProvider(BaseProvider):
    """Provider for share change depth data."""

    def get_data_type(self) -> str:
        return "sharechangedepth"

    def get_freeze_info(self, symbol: str) -> pd.DataFrame:
        """Get share freeze information."""
        return self._execute_api_mapped("get_freeze_info", symbol=symbol)

    def get_capital_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get capital change information."""
        return self._execute_api_mapped("get_capital_change", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_topholder_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get top holder change information."""
        return self._execute_api_mapped("get_topholder_change", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_major_holder_trade(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get major holder trade information."""
        return self._execute_api_mapped(
            "get_major_holder_trade", symbol=symbol, start_date=start_date, end_date=end_date
        )


class ShareChangeDepthFactory(ShareholderFactory):
    """Factory for share change depth data providers."""

    pass


@ShareChangeDepthFactory.register("eastmoney")
class EastMoneyShareChangeDepthProvider(ShareChangeDepthProvider):
    """Share change depth data provider using EastMoney."""

    def get_source_name(self) -> str:
        return "eastmoney"

    def get_freeze_info(self, symbol: str) -> pd.DataFrame:
        """Get share freeze information."""
        return self.akshare_adapter.call("stock_gdfx_freeze_holding_detail_em", symbol=symbol)

    def get_capital_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get capital change information."""
        return self.akshare_adapter.call("stock_zgb_change_em", symbol=symbol)

    def get_topholder_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get top holder change information."""
        return self.akshare_adapter.call("stock_gdfx_holding_change_em", symbol=symbol)

    def get_major_holder_trade(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get major holder trade information."""
        return self.akshare_adapter.call("stock_gdfx_holding_analyse_em", symbol=symbol)
