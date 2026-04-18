from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class NorthboundDepthProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "northbounddepth"

    def get_north_stock_detail(self, symbol: str, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_north_stock_detail", symbol=symbol, date=date)

    def get_north_quota_info(self, start_date: str, end_date: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_north_quota_info", start_date=start_date, end_date=end_date)

    def get_north_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_north_calendar", start_date=start_date, end_date=end_date)


class NorthboundDepthFactory(BaseFactory[NorthboundDepthProvider]):
    _providers: dict[str, type[NorthboundDepthProvider]] = {}
