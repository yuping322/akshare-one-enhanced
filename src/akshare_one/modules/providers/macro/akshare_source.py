"""
AkShare macro data provider - Chinese macroeconomic data from AkShare.
"""

import pandas as pd

from ...core.base import BaseProvider
from .base import MacroFactory


class MacroAkShareProvider(BaseProvider):
    """Provider for AkShare macro data."""

    def get_data_type(self) -> str:
        return "macroakshare"

    def get_macro_gdp(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China GDP data."""
        return self._execute_api_mapped("get_macro_gdp", start_date=start_date, end_date=end_date)

    def get_macro_cpi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China CPI data."""
        return self._execute_api_mapped("get_macro_cpi", start_date=start_date, end_date=end_date)

    def get_macro_ppi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China PPI data."""
        return self._execute_api_mapped("get_macro_ppi", start_date=start_date, end_date=end_date)

    def get_macro_pmi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China PMI data."""
        return self._execute_api_mapped("get_macro_pmi", start_date=start_date, end_date=end_date)

    def get_macro_interest_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China interest rate data."""
        return self._execute_api_mapped("get_macro_interest_rate", start_date=start_date, end_date=end_date)

    def get_macro_exchange_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get China exchange rate data."""
        return self._execute_api_mapped("get_macro_exchange_rate", start_date=start_date, end_date=end_date)


class MacroAkShareFactory(MacroFactory):
    """Factory for AkShare macro data providers."""

    pass


@MacroAkShareFactory.register("akshare")
class AkShareMacroAkShareProvider(MacroAkShareProvider):
    """AkShare macro data provider."""

    def get_source_name(self) -> str:
        return "akshare"

    def get_data_type(self) -> str:
        return "macroakshare"

    def get_macro_gdp(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_gdp")

    def get_macro_cpi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_cpi")

    def get_macro_ppi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_ppi")

    def get_macro_pmi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_pmi")

    def get_macro_interest_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_interest_rate")

    def get_macro_exchange_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_exchange_rate")
