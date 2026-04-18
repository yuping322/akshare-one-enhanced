import re

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


def parse_futures_symbol(symbol: str, contract: str = "main") -> tuple[str, str]:
    """Parse and normalize futures symbol and contract."""
    symbol = symbol.upper().strip()
    contract = contract.strip()

    match = re.match(r"^([A-Z]+)(\d*)$", symbol)
    if not match:
        return symbol, contract

    base_symbol = match.group(1)
    symbol_suffix = match.group(2)

    if symbol_suffix:
        if symbol_suffix == "0":
            if contract.lower() == "main" or contract == "0":
                return base_symbol, "main"
            return base_symbol, contract
        else:
            if contract.lower() == "main":
                return base_symbol, symbol_suffix
            if contract != symbol_suffix and contract.lower() != "main":
                return base_symbol, contract
            return base_symbol, symbol_suffix

    return base_symbol, contract


class HistoricalFuturesDataProvider(BaseProvider):
    def __init__(
        self,
        symbol: str,
        contract: str = "main",
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.symbol, self.contract = parse_futures_symbol(symbol, contract)
        self.interval = interval
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self._validate_dates()

    def get_source_name(self) -> str:
        return "futures"

    def get_data_type(self) -> str:
        return "futures"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_hist_data()

    def _validate_dates(self) -> None:
        try:
            pd.to_datetime(self.start_date)
            pd.to_datetime(self.end_date)
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.") from None

    @classmethod
    def get_supported_intervals(cls) -> list[str]:
        return ["minute", "hour", "day", "week", "month"]

    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches historical futures market data"""
        return self._execute_api_mapped("get_hist_data", columns=columns, row_filter=row_filter, **kwargs)

    def get_main_contracts(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches main contract list"""
        return self._execute_api_mapped("get_main_contracts", columns=columns, row_filter=row_filter, **kwargs)


class RealtimeFuturesDataProvider(BaseProvider):
    symbol: str | None
    contract: str | None
    original_symbol: str | None

    def __init__(self, symbol: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if symbol:
            parsed_symbol, parsed_contract = parse_futures_symbol(symbol, "main")
            self.symbol = parsed_symbol
            self.contract = parsed_contract
            self.original_symbol = symbol.upper().strip()
        else:
            self.symbol = None
            self.contract = None
            self.original_symbol = None

    def get_source_name(self) -> str:
        return "futures"

    def get_data_type(self) -> str:
        return "futures"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_current_data()

    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches realtime futures market data"""
        return self._execute_api_mapped("get_current_data", columns=columns, row_filter=row_filter, **kwargs)

    def get_all_quotes(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches all futures quotes"""
        return self._execute_api_mapped("get_all_quotes", columns=columns, row_filter=row_filter, **kwargs)


class FuturesHistoricalFactory(BaseFactory["HistoricalFuturesDataProvider"]):
    """Factory class for creating historical futures data providers."""

    _providers: dict[str, type["HistoricalFuturesDataProvider"]] = {}


class FuturesRealtimeFactory(BaseFactory["RealtimeFuturesDataProvider"]):
    """Factory class for creating realtime futures data providers."""

    _providers: dict[str, type["RealtimeFuturesDataProvider"]] = {}


class FuturesDataFactory:
    """
    Unified factory for futures data providers.

    This factory provides compatibility methods for accessing both historical
    and realtime futures providers through a single interface.

    This class delegates to FuturesHistoricalFactory and FuturesRealtimeFactory
    for actual provider creation.
    """

    _historical_providers: dict[str, type["HistoricalFuturesDataProvider"]] = (
        FuturesHistoricalFactory._providers
    )
    _realtime_providers: dict[str, type["RealtimeFuturesDataProvider"]] = (
        FuturesRealtimeFactory._providers
    )

    @classmethod
    def get_historical_provider(cls, source: str, **kwargs) -> "HistoricalFuturesDataProvider":
        """
        Get a historical futures data provider for the specified source.

        Args:
            source: Data source name (e.g., 'eastmoney', 'sina')
            **kwargs: Additional parameters passed to the provider constructor

        Returns:
            HistoricalFuturesDataProvider instance
        """
        return FuturesHistoricalFactory.get_provider(source, **kwargs)

    @classmethod
    def get_realtime_provider(cls, source: str, **kwargs) -> "RealtimeFuturesDataProvider":
        """
        Get a realtime futures data provider for the specified source.

        Args:
            source: Data source name (e.g., 'eastmoney', 'sina')
            **kwargs: Additional parameters passed to the provider constructor

        Returns:
            RealtimeFuturesDataProvider instance
        """
        return FuturesRealtimeFactory.get_provider(source, **kwargs)

    @classmethod
    def list_historical_sources(cls) -> list[str]:
        """List all available historical data sources."""
        return FuturesHistoricalFactory.list_sources()

    @classmethod
    def list_realtime_sources(cls) -> list[str]:
        """List all available realtime data sources."""
        return FuturesRealtimeFactory.list_sources()
