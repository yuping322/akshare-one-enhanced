"""
Northbound depth data provider - extended APIs for northbound capital.
"""

import pandas as pd

from .....core.base import BaseProvider
from .base import NorthboundFactory


class NorthboundDepthProvider(BaseProvider):
    """Extended provider for northbound depth data."""

    def get_data_type(self) -> str:
        return "northbounddepth"

    def get_north_stock_detail(self, symbol: str, date: str = "") -> pd.DataFrame:
        """Get individual stock northbound capital details."""
        return self._execute_api_mapped("get_north_stock_detail", symbol=symbol, date=date)

    def get_north_quota_info(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get northbound quota usage information."""
        return self._execute_api_mapped("get_north_quota_info", start_date=start_date, end_date=end_date)

    def get_north_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get northbound trading calendar."""
        return self._execute_api_mapped("get_north_calendar", start_date=start_date, end_date=end_date)


class NorthboundDepthFactory(NorthboundFactory):
    """Factory for northbound depth data providers."""

    pass


@NorthboundDepthFactory.register("akshare")
class AkShareNorthboundDepthProvider(NorthboundDepthProvider):
    """Northbound depth data provider using AkShare."""

    def get_source_name(self) -> str:
        return "akshare"

    def get_north_stock_detail(self, symbol: str, date: str = "") -> pd.DataFrame:
        """Get individual stock northbound details."""
        return self.akshare_adapter.call("stock_hsgt_individual_em", symbol=symbol)

    def get_north_quota_info(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get northbound quota usage."""
        return self.akshare_adapter.call("stock_hsgt_quota_em")

    def get_north_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get northbound trading calendar."""
        return self.akshare_adapter.call("stock_hsgt_calendar_em")
