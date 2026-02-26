"""
Sina macro economic data provider.

This module implements the macro economic data provider using Sina as the data source.
"""

import pandas as pd

from .base import MacroProvider


class SinaMacroProvider(MacroProvider):
    """
    Macro economic data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sina"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_lpr_rate(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get LPR interest rate data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "loan_1y", "loan_5y", "deposit_1y", "deposit_5y"])

    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str) -> pd.DataFrame:
        """Get PMI index data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "pmi_type", "pmi", "previous", "change"])

    def get_cpi_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get CPI data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "cpi", "yoy", "mom"])

    def get_ppi_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get PPI data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "ppi", "yoy", "mom"])

    def get_m2_supply(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get M2 money supply data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "m2", "yoy", "mom"])

    def get_shibor_rate(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get Shibor interest rate data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "overnight", "1w", "2w", "1m", "3m", "6m", "1y"])

    def get_social_financing(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get social financing scale data from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=["date", "total", "RMB", "foreign_currency", "bill", "bond", "equity"])
