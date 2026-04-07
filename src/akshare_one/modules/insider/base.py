import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class InsiderDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "insider"

    def get_data_type(self) -> str:
        return "insider"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_inner_trade_data()

    def get_inner_trade_data(self, **kwargs) -> pd.DataFrame:
        """Fetches insider trade data"""
        return self._execute_api_mapped("get_inner_trade_data", **kwargs)


class InsiderDataFactory(BaseFactory["InsiderDataProvider"]):
    """Factory class for creating insider data providers."""

    _providers: dict[str, type["InsiderDataProvider"]] = {}
