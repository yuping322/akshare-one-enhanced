"""
Dividend calculation provider - bonus, rights issue, and dividend calculations.
"""

import pandas as pd

from .....core.base import BaseProvider
from .base import DividendDataFactory


class DividendCalcProvider(BaseProvider):
    """Provider for dividend calculation data."""

    def get_data_type(self) -> str:
        return "dividendcalc"

    def get_stock_bonus(self, symbol: str) -> pd.DataFrame:
        """Get stock bonus and transfer information."""
        return self._execute_api_mapped("get_stock_bonus", symbol=symbol)

    def get_rights_issue(self, symbol: str) -> pd.DataFrame:
        """Get rights issue information."""
        return self._execute_api_mapped("get_rights_issue", symbol=symbol)

    def get_dividend_by_date(self, report_date: str) -> pd.DataFrame:
        """Get dividend data by report date."""
        return self._execute_api_mapped("get_dividend_by_date", report_date=report_date)


class DividendCalcFactory(DividendDataFactory):
    """Factory for dividend calculation data providers."""

    pass


@DividendCalcFactory.register("akshare")
class AkShareDividendCalcProvider(DividendCalcProvider):
    """Dividend calculation data provider using AkShare."""

    def get_source_name(self) -> str:
        return "akshare"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_stock_bonus(self, symbol: str) -> pd.DataFrame:
        """Get stock bonus and transfer information."""
        return self.akshare_adapter.call("stock_fhps_em", symbol=symbol)

    def get_rights_issue(self, symbol: str) -> pd.DataFrame:
        """Get rights issue information."""
        return self.akshare_adapter.call("stock_pg_em", symbol=symbol)

    def get_dividend_by_date(self, report_date: str) -> pd.DataFrame:
        """Get dividend data by report date."""
        return self.akshare_adapter.call("stock_fhps_detail_em", date=report_date)
