"""
Sina northbound capital data provider.

This module implements the northbound capital data provider using Sina as the data source.
"""

import pandas as pd

from .base import NorthboundProvider


class SinaNorthboundProvider(NorthboundProvider):
    """
    Northbound capital data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'sina'

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_northbound_flow(
        self,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """Get northbound capital flow data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=[
            'date', 'market', 'inflow', 'outflow', 'net_inflow',
            'buy_amount', 'sell_amount', 'balance'
        ])

    def get_northbound_holdings(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get northbound holdings details from Sina."""
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=[
            'date', 'symbol', 'name', 'shares', '比例', 'change_shares', 'change_ratio'
        ])

    def get_northbound_top_stocks(
        self,
        date: str,
        market: str,
        top_n: int
    ) -> pd.DataFrame:
        """Get northbound capital top stocks ranking from Sina."""
        return pd.DataFrame(columns=[
            'rank', 'symbol', 'name', 'shares', '比例', 'change_shares', 'change_ratio'
        ])
