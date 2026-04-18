"""
Lixinger provider for financial data.

This module implements financial data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ......lixinger_client import get_lixinger_client
from ......constants import SYMBOL_ZFILL_WIDTH
from .base import FinancialDataFactory, FinancialDataProvider


@FinancialDataFactory.register("lixinger")
class LixingerFinancialProvider(FinancialDataProvider):
    """
    Financial data provider using Lixinger OpenAPI.

    Provides balance sheet, income statement, cash flow, and financial metrics.
    """

    _balance_sheet_metrics = [
        "q.bs.ta.t",
        "q.bs.fa.t",
        "q.bs.c.t",
        "q.bs.ar.t",
        "q.bs.i.t",
        "q.bs.tl.t",
        "q.bs.ap.t",
        "q.bs.dr.t",
        "q.bs.te.t",
    ]

    _income_statement_metrics = [
        "q.ps.toi.t",
        "q.ps.toc.t",
        "q.ps.oc.t",
        "q.ps.op.t",
        "q.ps.ni.t",
    ]

    _cash_flow_metrics = [
        "q.cf.oncf.t",
        "q.cf.icf.t",
        "q.cf.fcf.t",
        "q.cf.cce.t",
    ]

    _column_rename_map = {
        "date": "report_date",
        "stockCode": "symbol",
        "q.bs.ta.t": "total_assets",
        "q.bs.fa.t": "fixed_assets_net",
        "q.bs.c.t": "cash_and_equivalents",
        "q.bs.ar.t": "accounts_receivable",
        "q.bs.i.t": "inventory",
        "q.bs.tl.t": "total_liabilities",
        "q.bs.ap.t": "trade_and_non_trade_payables",
        "q.bs.dr.t": "deferred_revenue",
        "q.bs.te.t": "shareholders_equity",
        "q.ps.toi.t": "revenue",
        "q.ps.toc.t": "total_operating_costs",
        "q.ps.oc.t": "operating_costs",
        "q.ps.op.t": "operating_profit",
        "q.ps.ni.t": "net_income",
        "q.cf.oncf.t": "net_cash_flow_from_operations",
        "q.cf.icf.t": "net_cash_flow_from_investing",
        "q.cf.fcf.t": "net_cash_flow_from_financing",
        "q.cf.cce.t": "change_in_cash_and_equivalents",
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def _fetch_financial_data(
        self, metrics: list[str], start_date: str | None = None, end_date: str | None = None, date: str | None = None
    ) -> pd.DataFrame:
        """
        Fetch financial data from Lixinger API.

        Args:
            metrics: List of metrics to fetch
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            date: Specific date or 'latest'

        Returns:
            pd.DataFrame: Raw financial data
        """
        client = get_lixinger_client()

        params = {"stockCodes": [self.symbol], "metricsList": metrics}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        response = client.query_api("cn/company/fs/non_financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        return df

    def get_balance_sheet(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get balance sheet data from Lixinger.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters (start_date, end_date, date, metrics)

        Returns:
            pd.DataFrame: Balance sheet data
        """
        metrics = kwargs.get("metrics", self._balance_sheet_metrics)
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date", "latest")

        df = self._fetch_financial_data(metrics, start_date, end_date, date)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._column_rename_map)

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_income_statement(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get income statement data from Lixinger.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters (start_date, end_date, date, metrics)

        Returns:
            pd.DataFrame: Income statement data
        """
        metrics = kwargs.get("metrics", self._income_statement_metrics)
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date", "latest")

        df = self._fetch_financial_data(metrics, start_date, end_date, date)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._column_rename_map)

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_cash_flow(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get cash flow statement data from Lixinger.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters (start_date, end_date, date, metrics)

        Returns:
            pd.DataFrame: Cash flow statement data
        """
        metrics = kwargs.get("metrics", self._cash_flow_metrics)
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date", "latest")

        df = self._fetch_financial_data(metrics, start_date, end_date, date)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._column_rename_map)

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_financial_metrics(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get comprehensive financial metrics from Lixinger.

        Combines balance sheet, income statement, and cash flow data.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters (start_date, end_date, date)

        Returns:
            pd.DataFrame: Combined financial metrics
        """
        all_metrics = self._balance_sheet_metrics + self._income_statement_metrics + self._cash_flow_metrics

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date", "latest")

        df = self._fetch_financial_data(all_metrics, start_date, end_date, date)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._column_rename_map)

        if "report_date" in df.columns:
            df = df.sort_values("report_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_dividend_history(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get dividend history from Lixinger via cn/company/dividend.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: start_date, end_date

        Returns:
            pd.DataFrame: Dividend history with announcement_date, dividend_per_share, ex_date, etc.
        """
        client = get_lixinger_client()

        start_date = kwargs.get("start_date", "1970-01-01")
        end_date = kwargs.get("end_date", "2099-12-31")

        params = {"stockCode": self.symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/dividend", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        rename = {
            "date": "announcement_date",
            "content": "content",
            "bonusSharesFromProfit": "bonus_shares_from_profit",
            "bonusSharesFromCapitalReserve": "bonus_shares_from_reserve",
            "dividend": "dividend_per_share",
            "currency": "currency",
            "dividendAmount": "dividend_amount",
            "annualNetProfit": "annual_net_profit",
            "annualNetProfitDividendRatio": "dividend_ratio",
            "registerDate": "record_date",
            "exDate": "ex_date",
            "paymentDate": "payment_date",
            "fsEndDate": "fiscal_year_end",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        df["symbol"] = self.symbol.zfill(SYMBOL_ZFILL_WIDTH) if self.symbol else ""

        for date_col in ["announcement_date", "record_date", "ex_date", "payment_date", "fiscal_year_end"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")

        if "announcement_date" in df.columns:
            df = df.sort_values("announcement_date", ascending=False, na_position="last").reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)
