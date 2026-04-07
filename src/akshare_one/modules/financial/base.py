import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class FinancialDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "financial"

    def get_data_type(self) -> str:
        return "financial"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_balance_sheet()

    def get_balance_sheet(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches balance sheet data"""
        return self._execute_api_mapped("get_balance_sheet", columns=columns, row_filter=row_filter, **kwargs)

    def get_income_statement(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches income statement data"""
        return self._execute_api_mapped("get_income_statement", columns=columns, row_filter=row_filter, **kwargs)

    def get_cash_flow(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches cash flow data"""
        return self._execute_api_mapped("get_cash_flow", columns=columns, row_filter=row_filter, **kwargs)

    def get_financial_metrics(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetch financial metrics"""
        return self._execute_api_mapped("get_financial_metrics", columns=columns, row_filter=row_filter, **kwargs)

    def get_dividend_history(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetch dividend history"""
        return self._execute_api_mapped("get_dividend_history", columns=columns, row_filter=row_filter, **kwargs)


class FinancialDataFactory(BaseFactory["FinancialDataProvider"]):
    """Factory class for creating financial data providers."""

    _providers: dict[str, type["FinancialDataProvider"]] = {}
