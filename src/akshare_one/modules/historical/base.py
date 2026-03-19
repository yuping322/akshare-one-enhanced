from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class HistoricalDataProvider(BaseProvider):
    def __init__(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol
        self.interval = interval
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self.adjust = adjust

    def get_source_name(self) -> str:
        return "historical"

    def get_data_type(self) -> str:
        return "historical"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_hist_data()

    @classmethod
    def get_supported_intervals(cls) -> list[str]:
        return ["minute", "hour", "day", "week", "month", "year"]

    @abstractmethod
    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches historical market data"""
        pass


class HistoricalDataFactory(BaseFactory["HistoricalDataProvider"]):
    """Factory class for creating historical data providers."""

    _providers: dict[str, type["HistoricalDataProvider"]] = {}
