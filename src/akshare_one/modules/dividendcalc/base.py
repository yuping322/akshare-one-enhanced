"""
Base classes for dividend calculation data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class DividendCalcProvider(BaseProvider):
    """Base class for dividend calculation data providers."""

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


class DividendCalcFactory(BaseFactory[DividendCalcProvider]):
    """Factory for dividend calculation data providers."""

    _providers: dict[str, type[DividendCalcProvider]] = {}
