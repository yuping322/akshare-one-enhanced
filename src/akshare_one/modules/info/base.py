import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class InfoDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "info"

    def get_data_type(self) -> str:
        return "info"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_basic_info()

    def get_basic_info(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches basic information"""
        return self._execute_api_mapped("get_basic_info", columns=columns, row_filter=row_filter, **kwargs)


class InfoDataFactory(BaseFactory["InfoDataProvider"]):
    """Factory class for creating info data providers."""

    _providers: dict[str, type["InfoDataProvider"]] = {}
