from ..core.base import BaseProvider
from ..core.factory import BaseFactory
import pandas as pd


class NorthDailyProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "northdaily"

    def get_north_daily(self, date: str = "") -> dict:
        return self._execute_api_mapped("get_north_daily", date=date)


class NorthDailyFactory(BaseFactory[NorthDailyProvider]):
    _providers: dict[str, type[NorthDailyProvider]] = {}
