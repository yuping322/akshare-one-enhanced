"""
TickFlow provider for financial data.

This module implements financial data provider using TickFlow API.
"""

import pandas as pd

from ...tickflow_client import get_tickflow_client
from .base import FinancialDataFactory, FinancialDataProvider


@FinancialDataFactory.register("tickflow")
class TickFlowFinancialProvider(FinancialDataProvider):
    """
    Financial data provider using TickFlow API.

    Provides balance sheet, income statement, cash flow, and financial metrics.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_balance_sheet(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get balance sheet data from TickFlow.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - latest: Only return latest period (boolean)

        Returns:
            pd.DataFrame: Balance sheet data with columns:
                - symbol: Stock code
                - period_end: Period end date
                - announce_date: Announcement date
                - total_assets: Total assets
                - total_current_assets: Total current assets
                - cash_and_equivalents: Cash and cash equivalents
                - accounts_receivable: Accounts receivable
                - inventory: Inventory
                - fixed_assets: Fixed assets
                - total_liabilities: Total liabilities
                - total_current_liabilities: Total current liabilities
                - accounts_payable: Accounts payable
                - total_equity: Total equity
                - equity_attributable: Equity attributable to parent
                - minority_interest: Minority interest
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"

        params = {"symbols": symbol}

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        latest = kwargs.get("latest")

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if latest:
            params["latest"] = "true"

        response = client.query_api("/v1/financials/balance-sheet", method="GET", params=params)

        data = response.get("data", {}).get(symbol, [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        column_rename = {
            "period_end": "report_date",
            "announce_date": "announcement_date",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_income_statement(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get income statement data from TickFlow.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - latest: Only return latest period (boolean)

        Returns:
            pd.DataFrame: Income statement data with columns:
                - symbol: Stock code
                - period_end: Period end date
                - announce_date: Announcement date
                - revenue: Revenue
                - operating_profit: Operating profit
                - net_income: Net income
                - eps: Earnings per share
                - eps_diluted: Diluted EPS
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"

        params = {"symbols": symbol}

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        latest = kwargs.get("latest")

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if latest:
            params["latest"] = "true"

        response = client.query_api("/v1/financials/income", method="GET", params=params)

        data = response.get("data", {}).get(symbol, [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        column_rename = {
            "period_end": "report_date",
            "announce_date": "announcement_date",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_cash_flow(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get cash flow statement data from TickFlow.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - latest: Only return latest period (boolean)

        Returns:
            pd.DataFrame: Cash flow statement data with columns:
                - symbol: Stock code
                - period_end: Period end date
                - announce_date: Announcement date
                - net_operating_cash_flow: Net operating cash flow
                - net_investing_cash_flow: Net investing cash flow
                - net_financing_cash_flow: Net financing cash flow
                - net_cash_change: Net change in cash
                - capex: Capital expenditure
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"

        params = {"symbols": symbol}

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        latest = kwargs.get("latest")

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if latest:
            params["latest"] = "true"

        response = client.query_api("/v1/financials/cash-flow", method="GET", params=params)

        data = response.get("data", {}).get(symbol, [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        column_rename = {
            "period_end": "report_date",
            "announce_date": "announcement_date",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_financial_metrics(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get comprehensive financial metrics from TickFlow.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - latest: Only return latest period (boolean)

        Returns:
            pd.DataFrame: Financial metrics with columns:
                - symbol: Stock code
                - period_end: Period end date
                - announce_date: Announcement date
                - eps: Earnings per share
                - bvps: Book value per share
                - roe: Return on equity
                - roa: Return on assets
                - gross_margin: Gross margin
                - net_margin: Net margin
                - debt_ratio: Debt ratio
                - current_ratio: Current ratio
                - quick_ratio: Quick ratio
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"

        params = {"symbols": symbol}

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        latest = kwargs.get("latest")

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if latest:
            params["latest"] = "true"

        response = client.query_api("/v1/financials/metrics", method="GET", params=params)

        data = response.get("data", {}).get(symbol, [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        column_rename = {
            "period_end": "report_date",
            "announce_date": "announcement_date",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_dividend_history(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get dividend history.

        Note: TickFlow API currently doesn't have a dividend endpoint.
        This method returns an empty DataFrame for compatibility.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Empty DataFrame (not supported by TickFlow)
        """
        self.logger.warning(
            "TickFlow API does not support dividend history data. Returning empty DataFrame.",
            extra={
                "context": {
                    "log_type": "unsupported_feature",
                    "provider": "tickflow",
                    "feature": "dividend_history",
                }
            },
        )
        return pd.DataFrame()
