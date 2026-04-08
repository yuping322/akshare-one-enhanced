"""
Fund data module for PV.Fund.

This module provides interfaces to fetch fund data including:
- Historical net value data
- Fund basic information
- Investment positions/holdings
- Industry distribution/allocation
- Asset allocation/types percentage
- Fund codes list
- Fund manager information
- Realtime increase rate
"""

from typing import Any, Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import efinance
from .base import FundFactory, FundProvider


@api_endpoint(FundFactory, method_name="get_quote_history")
def get_fund_quote_history(
    fund_code: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund historical net value data.

    Args:
        fund_code: Fund code (e.g., '000001')
    """
    pass


@api_endpoint(FundFactory, method_name="get_base_info")
def get_fund_base_info(
    fund_codes: str | list[str],
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund basic information.

    Args:
        fund_codes: Fund code or list of codes
    """
    pass


@api_endpoint(FundFactory, method_name="get_invest_position")
def get_fund_invest_position(
    fund_code: str,
    dates: str | list[str] | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund investment positions/holdings.

    Args:
        fund_code: Fund code
        dates: Date or list of dates for holdings
    """
    pass


@api_endpoint(FundFactory, method_name="get_industry_distribution")
def get_fund_industry_distribution(
    fund_code: str,
    dates: str | list[str] | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund industry distribution/allocation.

    Args:
        fund_code: Fund code
        dates: Date or list of dates
    """
    pass


@api_endpoint(FundFactory, method_name="get_types_percentage")
def get_fund_types_percentage(
    fund_code: str,
    dates: str | list[str] | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund asset allocation/types percentage.

    Args:
        fund_code: Fund code
        dates: Date or list of dates
    """
    pass


@api_endpoint(FundFactory, method_name="get_fund_codes")
def get_fund_codes(
    ft: Literal["open", "closed", "etf", "index", "all"] = "all",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get list of fund codes.

    Args:
        ft: Fund type filter ('open', 'closed', 'etf', 'index', 'all')
    """
    pass


@api_endpoint(FundFactory, method_name="get_fund_manager")
def get_fund_manager(
    ft: Literal["open", "closed", "etf", "index", "all"] = "all",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund manager information.

    Args:
        ft: Fund type filter ('open', 'closed', 'etf', 'index', 'all')
    """
    pass


@api_endpoint(FundFactory, method_name="get_realtime_increase_rate")
def get_fund_realtime_increase_rate(
    fund_codes: str | list[str],
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund realtime increase rate (change percentage).

    Args:
        fund_codes: Fund code or list of codes
    """
    pass


@api_endpoint(FundFactory, method_name="get_quote_history_multi")
def get_fund_quote_history_multi(
    fund_codes: list[str],
    pz: int = 100,
    source: SourceType = None,
) -> dict[str, pd.DataFrame]:
    """
    Get fund historical net value data for multiple funds.

    Args:
        fund_codes: List of fund codes
        pz: Number of records per fund
    """
    pass


@api_endpoint(FundFactory, method_name="get_public_dates")
def get_fund_public_dates(
    fund_code: str,
    source: SourceType = None,
) -> list[str]:
    """
    Get list of public announcement dates for a fund.

    Args:
        fund_code: Fund code
    """
    pass


@api_endpoint(FundFactory, method_name="get_period_change")
def get_fund_period_change(
    fund_code: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get fund performance in different periods (近1周, 近1月, 近3月, 近6月, 近1年, 近3年).

    Args:
        fund_code: Fund code
    """
    pass


@api_endpoint(FundFactory, method_name="get_pdf_reports")
def get_fund_pdf_reports(
    fund_code: str,
    max_count: int = 12,
    save_dir: str = "pdf",
    source: SourceType = None,
) -> list[str] | None:
    """
    Download PDF reports for a fund.

    Args:
        fund_code: Fund code
        max_count: Maximum number of PDF reports to download
        save_dir: Directory to save PDF reports
    """
    pass


__all__ = [
    "get_fund_quote_history",
    "get_fund_base_info",
    "get_fund_invest_position",
    "get_fund_industry_distribution",
    "get_fund_types_percentage",
    "get_fund_codes",
    "get_fund_manager",
    "get_fund_realtime_increase_rate",
    "get_fund_quote_history_multi",
    "get_fund_public_dates",
    "get_fund_period_change",
    "get_fund_pdf_reports",
    "FundFactory",
    "FundProvider",
]
