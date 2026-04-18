import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class OptionsDataProvider(BaseProvider):
    """Base class for options data providers"""

    def __init__(
        self,
        underlying_symbol: str,
        option_type: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.underlying_symbol = underlying_symbol
        self.option_type = option_type

    def get_source_name(self) -> str:
        return "options"

    def get_data_type(self) -> str:
        return "options"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_options_chain()

    def get_options_chain(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches options chain data"""
        return self._execute_api_mapped("get_options_chain", columns=columns, row_filter=row_filter, **kwargs)

    def get_options_realtime(self, symbol: str, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches realtime options quote data"""
        return self._execute_api_mapped("get_options_realtime", symbol=symbol, columns=columns, row_filter=row_filter, **kwargs)

    def get_options_expirations(self, underlying_symbol: str, **kwargs) -> list[str]:
        """Fetches available expiration dates for options"""
        # This might return a list, but _execute_api_mapped returns a DataFrame
        # For now, let's keep it as is or implement it in subclasses if needed.
        # If it's in _API_MAP, it will return a DataFrame.
        return self._execute_api_mapped("get_options_expirations", underlying_symbol=underlying_symbol, **kwargs)

    def get_options_history(
        self,
        symbol: str,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> pd.DataFrame:
        """Fetches historical options quote data"""
        return self._execute_api_mapped("get_options_history", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)


class OptionsDataFactory(BaseFactory["OptionsDataProvider"]):
    """Factory class for creating options data providers."""

    _providers: dict[str, type["OptionsDataProvider"]] = {}
