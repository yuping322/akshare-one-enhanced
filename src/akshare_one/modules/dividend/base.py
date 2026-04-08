import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class DividendDataProvider(BaseProvider):
    def __init__(
        self,
        symbol: str,
        start_date: str = "1990-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_source_name(self) -> str:
        return "dividend"

    def get_data_type(self) -> str:
        return "dividend"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_dividend_data()

    def get_dividend_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        return self._execute_api_mapped("get_dividend_data", columns=columns, row_filter=row_filter, **kwargs)

    def get_adjust_factor(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        return self._execute_api_mapped("get_adjust_factor", columns=columns, row_filter=row_filter, **kwargs)


class DividendDataFactory(BaseFactory["DividendDataProvider"]):
    _providers: dict[str, type["DividendDataProvider"]] = {}
