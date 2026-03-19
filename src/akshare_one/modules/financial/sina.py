import akshare as ak
import pandas as pd

from ..cache import cache
from .base import FinancialDataProvider, FinancialDataFactory


@FinancialDataFactory.register("sina")
class SinaFinancialReport(FinancialDataProvider):
    """Financial data provider for Sina finance reports.

    Provides standardized access to balance sheet, income statement,
    and cash flow data from Sina finance API.
    """

    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(symbol, **kwargs)
        self.stock = f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol

    @cache("financial_cache", key=lambda self: f"sina_balance_{self.symbol}")
    def get_balance_sheet(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取资产负债表数据"""
        try:
            raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="资产负债表")
            df = self._clean_balance_data(raw_df)
            return self.standardize_and_filter(df, "sina", columns=columns, row_filter=row_filter)
        except Exception as e:
            raise ValueError(f"Failed to get balance sheet for symbol {self.symbol}: {str(e)}") from e

    @cache("financial_cache", key=lambda self: f"sina_income_{self.symbol}")
    def get_income_statement(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取利润表数据"""
        try:
            raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="利润表")
            df = self._clean_income_data(raw_df)
            return self.standardize_and_filter(df, "sina", columns=columns, row_filter=row_filter)
        except Exception as e:
            raise ValueError(f"Failed to get income statement for symbol {self.symbol}: {str(e)}") from e

    @cache("financial_cache", key=lambda self: f"sina_cash_{self.symbol}")
    def get_cash_flow(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取现金流量表数据"""
        try:
            raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="现金流量表")
            df = self._clean_cash_data(raw_df)
            return self.standardize_and_filter(df, "sina", columns=columns, row_filter=row_filter)
        except Exception as e:
            raise ValueError(f"Failed to get cash flow statement for symbol {self.symbol}: {str(e)}") from e

    def get_financial_metrics(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetch financial metrics (falls back to balance sheet for Sina)"""
        return self.get_balance_sheet(columns=columns, row_filter=row_filter)

    def _clean_cash_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化现金流量表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = self.map_source_fields(raw_df, "sina")
            raw_df["report_date"] = pd.to_datetime(raw_df["report_date"], format="%Y%m%d")

        # Define column mappings and required columns
        column_mapping = {
            "currency": "currency",
            "net_cash_flow_from_operations": "net_cash_flow_from_operations",
            "capital_expenditure": "capital_expenditure",
            "business_acquisitions_and_disposals": "business_acquisitions_and_disposals",
            "net_cash_flow_from_investing": "net_cash_flow_from_investing",
            "issuance_or_repayment_of_debt_securities": "issuance_or_repayment_of_debt_securities",
            "issuance_or_purchase_of_equity_shares": "issuance_or_purchase_of_equity_shares",
            "net_cash_flow_from_financing": "net_cash_flow_from_financing",
            "change_in_cash_and_equivalents": "change_in_cash_and_equivalents",
            "effect_of_exchange_rate_changes": "effect_of_exchange_rate_changes",
            "ending_cash_balance": "ending_cash_balance",
            "cash_from_sales": "cash_from_sales",
            "tax_refunds_received": "tax_refunds_received",
            "cash_paid_to_employees": "cash_paid_to_employees",
            "taxes_paid": "taxes_paid",
            "total_cash_inflow_from_operations": "total_cash_inflow_from_operations",
            "total_cash_outflow_from_operations": "total_cash_outflow_from_operations",
            "cash_from_investment_recovery": "cash_from_investment_recovery",
            "cash_from_investment_income": "cash_from_investment_income",
            "cash_from_asset_sales": "cash_from_asset_sales",
            "total_cash_inflow_from_investing": "total_cash_inflow_from_investing",
            "total_cash_outflow_from_investing": "total_cash_outflow_from_investing",
            "cash_paid_for_dividends_and_interest": "cash_paid_for_dividends_and_interest",
            "cash_paid_for_debt_repayment": "cash_paid_for_debt_repayment",
            "total_cash_inflow_from_financing": "total_cash_inflow_from_financing",
            "total_cash_outflow_from_financing": "total_cash_outflow_from_financing",
            "beginning_cash_balance": "beginning_cash_balance",
            "ending_cash": "ending_cash",
            "ending_cash_equivalents": "ending_cash_equivalents",
        }

        required_columns = ["report_date"] + list(column_mapping.values())
        return raw_df.reindex(columns=required_columns)

    def _clean_balance_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化资产负债表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = self.map_source_fields(raw_df, "sina")
            raw_df["report_date"] = pd.to_datetime(raw_df["report_date"], format="%Y%m%d")

        # Define and apply column mappings in one optimized operation
        raw_df = self.map_source_fields(raw_df, "sina")

        # Select only required columns
        required_columns = [
            "report_date",
            "currency",
            "total_assets",
            "current_assets",
            "cash_and_equivalents",
            "inventory",
            "current_investments",
            "trade_and_non_trade_receivables",
            "non_current_assets",
            "property_plant_and_equipment",
            "goodwill_and_intangible_assets",
            "investments",
            "non_current_investments",
            "outstanding_shares",
            "tax_assets",
            "total_liabilities",
            "current_liabilities",
            "current_debt",
            "trade_and_non_trade_payables",
            "deferred_revenue",
            "deposit_liabilities",
            "non_current_liabilities",
            "non_current_debt",
            "tax_liabilities",
            "shareholders_equity",
            "retained_earnings",
            "accumulated_other_comprehensive_income",
            "accounts_receivable",
            "prepayments",
            "other_receivables",
            "fixed_assets_net",
            "construction_in_progress",
            "capital_reserve",
            "current_ratio",
            "debt_to_assets",
            "minority_interest",
        ]

        # Calculate financial ratios using vectorized operations
        cols = ["current_debt", "non_current_debt"]
        raw_df[cols] = raw_df[cols].apply(pd.to_numeric, errors="coerce")
        raw_df["total_debt"] = raw_df[cols].fillna(0).sum(axis=1)

        # Pre-calculate denominator conditions
        valid_current_liab = raw_df["current_liabilities"].ne(0)
        valid_total_assets = raw_df["total_assets"].ne(0)

        # Calculate ratios in one operation
        ratios = pd.DataFrame(
            {
                "current_ratio": raw_df["current_assets"] / raw_df["current_liabilities"],
                "cash_ratio": raw_df["cash_and_equivalents"] / raw_df["current_liabilities"],
                "debt_to_assets": raw_df["total_debt"] / raw_df["total_assets"],
            }
        )

        # Apply conditions
        cond = pd.DataFrame(
            {
                "current_ratio": valid_current_liab,
                "cash_ratio": valid_current_liab,
                "debt_to_assets": valid_total_assets,
            },
            index=ratios.index,
        )
        raw_df = raw_df.join(ratios.where(cond))

        return raw_df.reindex(columns=required_columns)

    def _clean_income_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化利润表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = self.map_source_fields(raw_df, "sina")
            raw_df["report_date"] = pd.to_datetime(raw_df["report_date"], format="%Y%m%d")

        # Define column mappings and required columns
        column_mapping = {
            "currency": "currency",
            "revenue": "revenue",
            "operating_revenue": "operating_revenue",
            "total_operating_costs": "total_operating_costs",
            "cost_of_revenue": "cost_of_revenue",
            "operating_profit": "operating_profit",
            "selling_general_and_administrative_expenses": "selling_general_and_administrative_expenses",
            "operating_expense": "operating_expense",
            "research_and_development": "research_and_development",
            "interest_expense": "interest_expense",
            "ebit": "ebit",
            "income_tax_expense": "income_tax_expense",
            "net_income": "net_income",
            "net_income_common_stock": "net_income_common_stock",
            "net_income_non_controlling_interests": "net_income_non_controlling_interests",
            "earnings_per_share": "earnings_per_share",
            "earnings_per_share_diluted": "earnings_per_share_diluted",
            "investment_income": "investment_income",
            "fair_value_adjustments": "fair_value_adjustments",
            "asset_impairment_loss": "asset_impairment_loss",
            "financial_expenses": "financial_expenses",
            "taxes_and_surcharges": "taxes_and_surcharges",
            "other_comprehensive_income": "other_comprehensive_income",
            "total_comprehensive_income": "total_comprehensive_income",
        }

        required_columns = ["report_date"] + list(column_mapping.values())
        return raw_df.reindex(columns=required_columns)

    @cache("financial_cache", key=lambda self: f"sina_metrics_{self.symbol}")
    def get_financial_metrics(self) -> pd.DataFrame:
        """获取三大财务报表关键指标"""
        # Fetch all reports
        try:
            balance_sheet = self.get_balance_sheet()
        except ValueError:
            balance_sheet = pd.DataFrame()

        try:
            income_statement = self.get_income_statement()
        except ValueError:
            income_statement = pd.DataFrame()

        try:
            cash_flow = self.get_cash_flow()
        except ValueError:
            cash_flow = pd.DataFrame()

        if balance_sheet.empty and income_statement.empty and cash_flow.empty:
            return pd.DataFrame()

        # Start with the non-empty DataFrame
        if not balance_sheet.empty:
            merged = balance_sheet
        elif not income_statement.empty:
            merged = income_statement
        else:
            merged = cash_flow

        # Merge with the remaining non-empty DataFrames
        if not income_statement.empty and merged is not income_statement:
            merged = pd.merge(merged, income_statement, on="report_date", how="outer")

        if not cash_flow.empty and merged is not cash_flow:
            merged = pd.merge(merged, cash_flow, on="report_date", how="outer")

        # Sort by report_date in descending order (most recent first)
        if "report_date" in merged.columns:
            merged = merged.sort_values("report_date", ascending=False).reset_index(drop=True)

        return merged
