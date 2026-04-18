import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class RealtimeDataProvider(BaseProvider):
    def __init__(self, symbol: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "realtime"

    def get_data_type(self) -> str:
        return "realtime"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_current_data()

    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches realtime market data"""
        return self._execute_api_mapped("get_current_data", columns=columns, row_filter=row_filter, **kwargs)


class RealtimeDataFactory(BaseFactory["RealtimeDataProvider"]):
    """Factory class for creating realtime data providers."""

    _providers: dict[str, type["RealtimeDataProvider"]] = {}
