"""
Base provider class for valuation data.

This module defines the abstract interface for valuation data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class ValuationProvider(BaseProvider):
    """
    Abstract base class for valuation data providers.

    Defines the interface for fetching various types of valuation data:
    - Stock valuation (PE, PB, PS, etc.)
    - Market valuation
    - Industry valuation
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "valuation"

    def get_update_frequency(self) -> str:
        """Valuation data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Valuation data has 1 day delay."""
        return 0

    @abstractmethod
    def get_stock_valuation(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get stock valuation data.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Valuation data with columns:
                - date: Date
                - symbol: Stock symbol
                - close: Closing price
                - pe_ttm: PE (TTM)
                - pe_static: PE (Static)
                - pb: Price to Book
                - ps: Price to Sales
                - pcf: Price to Cash Flow
                - peg: PEG ratio
                - market_cap: Total market cap
                - float_market_cap: Float market cap
        """
        pass

    @abstractmethod
    def get_market_valuation(self) -> pd.DataFrame:
        """
        Get market-wide valuation data.

        Returns:
            pd.DataFrame: Market valuation data with columns:
                - index_name: Index name
                - pe: PE ratio
                - pb: PB ratio
                - date: Date
        """
        pass
