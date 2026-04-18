import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


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

    def get_daily_basic(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetches daily basic indicators"""
        return pd.DataFrame()

    def get_suspend_data(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetches suspension/resumption data"""
        return pd.DataFrame()

    def get_stk_limit(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetches daily limit up/down prices"""
        return pd.DataFrame()

    def get_adj_factor(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetches adjustment factor data"""
        return pd.DataFrame()


class InfoDataFactory(BaseFactory["InfoDataProvider"]):
    """Factory class for creating info data providers."""

    _providers: dict[str, type["InfoDataProvider"]] = {}
