from ..base import BaseProvider
import pandas as pd
from .base import NorthboundDepthFactory


class AkShareNorthboundDepthProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "akshare"

    def get_north_stock_detail(self, symbol: str, date: str = "") -> pd.DataFrame:
        """个股北向详情 - ak.stock_hsgt_individual_em"""
        return self.akshare_adapter.call("stock_hsgt_individual_em", symbol=symbol)

    def get_north_quota_info(self, start_date: str, end_date: str) -> pd.DataFrame:
        """额度使用 - ak.stock_hsgt_quota_em"""
        return self.akshare_adapter.call("stock_hsgt_quota_em")

    def get_north_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """交易日历 - ak.stock_hsgt_calendar_em"""
        return self.akshare_adapter.call("stock_hsgt_calendar_em")


@NorthboundDepthFactory.register("akshare")
class AkShareProvider(AkShareNorthboundDepthProvider):
    pass
