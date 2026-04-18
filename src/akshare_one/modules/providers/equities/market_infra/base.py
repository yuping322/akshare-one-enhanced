"""
Market infrastructure module - exchanges, instruments, universes.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class InstrumentProvider(BaseProvider):
    """Provider for instrument metadata."""

    def __init__(self, symbols: str | list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols if isinstance(symbols, list) else [symbols] if symbols else None

    def get_source_name(self) -> str:
        return "instrument"

    def get_data_type(self) -> str:
        return "instrument"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_instruments()

    def get_instruments(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches instrument metadata"""
        return self._execute_api_mapped("get_instruments", columns=columns, row_filter=row_filter, **kwargs)


class InstrumentFactory(BaseFactory["InstrumentProvider"]):
    """Factory class for creating instrument providers."""

    _providers: dict[str, type["InstrumentProvider"]] = {}


class ExchangeProvider(BaseProvider):
    """Provider for exchange data."""

    def __init__(self, exchange: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.exchange = exchange

    def get_source_name(self) -> str:
        return "exchange"

    def get_data_type(self) -> str:
        return "exchange"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_exchanges()

    def get_exchanges(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches exchange list"""
        return self._execute_api_mapped("get_exchanges", columns=columns, row_filter=row_filter, **kwargs)

    def get_exchange_instruments(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """Fetches instruments for a specific exchange"""
        return self._execute_api_mapped("get_exchange_instruments", columns=columns, row_filter=row_filter, **kwargs)


class ExchangeFactory(BaseFactory["ExchangeProvider"]):
    """Factory class for creating exchange providers."""

    _providers: dict[str, type["ExchangeProvider"]] = {}


class UniverseProvider(BaseProvider):
    """Provider for universe (标的池) data."""

    def __init__(self, universe_id: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.universe_id = universe_id

    def get_source_name(self) -> str:
        return "universe"

    def get_data_type(self) -> str:
        return "universe"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_universes()

    def get_universes(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches universe list"""
        return self._execute_api_mapped("get_universes", columns=columns, row_filter=row_filter, **kwargs)

    def get_universe_detail(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """Fetches universe detail"""
        return self._execute_api_mapped("get_universe_detail", columns=columns, row_filter=row_filter, **kwargs)


class UniverseFactory(BaseFactory["UniverseProvider"]):
    """Factory class for creating universe providers."""

    _providers: dict[str, type["UniverseProvider"]] = {}
