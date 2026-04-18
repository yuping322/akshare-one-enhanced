"""
AkShare provider for dividend calculation data.

This module implements dividend calculation data provider using AkShare as the data source.
"""

import pandas as pd

from .base import DividendCalcFactory, DividendCalcProvider


@DividendCalcFactory.register("akshare")
class AkShareDividendCalcProvider(DividendCalcProvider):
    """
    Dividend calculation data provider using AkShare as the data source.

    AkShare provides comprehensive dividend data including:
    - Stock bonus and transfer information (stock_fhps_em)
    - Rights issue information (stock_pg_em)
    - Dividend details by date (stock_fhps_detail_em)
    """

    _API_MAP = {
        "get_stock_bonus": {
            "ak_func": "stock_fhps_em",
            "params": {"symbol": "symbol"},
        },
        "get_rights_issue": {
            "ak_func": "stock_pg_em",
            "params": {"symbol": "symbol"},
        },
        "get_dividend_by_date": {
            "ak_func": "stock_fhps_detail_em",
            "params": {"report_date": "date"},
        },
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "akshare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from AkShare.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_stock_bonus(self, symbol: str) -> pd.DataFrame:
        """
        Get stock bonus and transfer information.

        Args:
            symbol: Stock symbol (6-digit code)

        Returns:
            pd.DataFrame: Stock bonus data
        """
        return self.akshare_adapter.call("stock_fhps_em", symbol=symbol)

    def get_rights_issue(self, symbol: str) -> pd.DataFrame:
        """
        Get rights issue information.

        Args:
            symbol: Stock symbol (6-digit code)

        Returns:
            pd.DataFrame: Rights issue data
        """
        return self.akshare_adapter.call("stock_pg_em", symbol=symbol)

    def get_dividend_by_date(self, report_date: str) -> pd.DataFrame:
        """
        Get dividend data by report date.

        Args:
            report_date: Report date (e.g., '2023-12-31')

        Returns:
            pd.DataFrame: Dividend data for the specified date
        """
        return self.akshare_adapter.call("stock_fhps_detail_em", date=report_date)
