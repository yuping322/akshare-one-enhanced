"""
Base classes for fund data providers.

This module provides the base classes for implementing fund data providers
with standardized interfaces for fetching fund-related data.
"""

from typing import Literal

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class FundProvider(BaseProvider):
    """
    Base class for fund data providers.

    Provides common functionality for:
    - Fund historical net value data
    - Fund basic information
    - Fund holdings/investment positions
    - Fund industry distribution
    - Fund asset allocation (types percentage)
    """

    fund_code: str

    def __init__(
        self,
        fund_code: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.fund_code = fund_code

    def get_source_name(self) -> str:
        return "fund"

    def get_data_type(self) -> str:
        return "fund"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_quote_history()

    def get_quote_history(
        self,
        fund_code: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund historical net value data.

        Args:
            fund_code: Fund code (e.g., '000001')
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund historical net value data
        """
        raise NotImplementedError

    def get_base_info(
        self,
        fund_codes: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund basic information.

        Args:
            fund_codes: Fund code or list of codes
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund basic information
        """
        raise NotImplementedError

    def get_invest_position(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund investment positions/holdings.

        Args:
            fund_code: Fund code
            dates: Date or list of dates for holdings
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund holdings data
        """
        raise NotImplementedError

    def get_industry_distribution(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund industry distribution/allocation.

        Args:
            fund_code: Fund code
            dates: Date or list of dates
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund industry distribution data
        """
        raise NotImplementedError

    def get_types_percentage(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund asset allocation/types percentage.

        Args:
            fund_code: Fund code
            dates: Date or list of dates
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund asset allocation data
        """
        raise NotImplementedError

    def get_fund_codes(
        self,
        ft: Literal["open", "closed", "etf", "index", "all"] = "all",
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get list of fund codes.

        Args:
            ft: Fund type filter
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund codes list
        """
        raise NotImplementedError

    def get_fund_manager(
        self,
        ft: Literal["open", "closed", "etf", "index", "all"] = "all",
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund manager information.

        Args:
            ft: Fund type filter
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund manager data
        """
        raise NotImplementedError

    def get_realtime_increase_rate(
        self,
        fund_codes: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund realtime increase rate (change percentage).

        Args:
            fund_codes: Fund code or list of codes
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with realtime change data
        """
        raise NotImplementedError

    def get_quote_history_multi(
        self,
        fund_codes: list[str],
        pz: int = 100,
        **kwargs,
    ) -> dict[str, pd.DataFrame]:
        """
        Get fund historical net value data for multiple funds.

        Args:
            fund_codes: List of fund codes
            pz: Number of records per fund

        Returns:
            Dict mapping fund codes to DataFrames with historical data
        """
        raise NotImplementedError

    def get_public_dates(
        self,
        fund_code: str | None = None,
        **kwargs,
    ) -> list[str]:
        """
        Get list of public announcement dates for a fund.

        Args:
            fund_code: Fund code

        Returns:
            List of date strings
        """
        raise NotImplementedError

    def get_period_change(
        self,
        fund_code: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund performance in different periods.

        Args:
            fund_code: Fund code
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with period performance data
        """
        raise NotImplementedError

    def get_pdf_reports(
        self,
        fund_code: str | None = None,
        max_count: int = 12,
        save_dir: str = "pdf",
        **kwargs,
    ) -> list[str] | None:
        """
        Download PDF reports for a fund.

        Args:
            fund_code: Fund code
            max_count: Maximum number of PDF reports to download
            save_dir: Directory to save PDF reports

        Returns:
            List of file paths or None on error
        """
        raise NotImplementedError


class FundFactory(BaseFactory["FundProvider"]):
    """
    Factory class for creating fund data providers.
    """

    _providers: dict[str, type["FundProvider"]] = {}


FIELD_MAPPING = {
    "基金代码": "fund_code",
    "日期": "date",
    "单位净值": "net_value",
    "累计净值": "accumulated_net_value",
    "涨跌幅": "pct_change",
    "持仓占比": "holding_ratio",
    "股票代码": "symbol",
    "股票简称": "name",
    "基金简称": "fund_name",
    "基金类型": "fund_type",
    "基金全称": "fund_full_name",
    "基金经理": "fund_manager",
    "基金规模": "fund_scale",
    "成立日期": "establish_date",
    "管理费": "management_fee",
    "托管费": "custody_fee",
    "净值日期": "date",
    "日增长率": "daily_growth_rate",
    "申购状态": "subscription_status",
    "赎回状态": "redemption_status",
    "行业": "industry",
    "持仓市值": "holding_value",
    "持仓数量": "holding_shares",
    "占净值比例": "net_value_ratio",
    "股票名称": "name",
    "持仓股票": "holding_symbol",
    "行业配置": "industry_allocation",
    "占净值比例": "ratio",
    "资产类型": "asset_type",
    "资产占比": "asset_ratio",
    "基金代码": "fund_code",
    "基金名称": "fund_name",
    "实时涨跌幅": "realtime_pct_change",
    "近1周": "week1",
    "近1月": "month1",
    "近3月": "month3",
    "近6月": "month6",
    "近1年": "year1",
    "近3年": "year3",
}
