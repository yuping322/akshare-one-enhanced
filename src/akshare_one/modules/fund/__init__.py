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


__all__ = [
    "get_fund_quote_history",
    "get_fund_base_info",
    "get_fund_invest_position",
    "get_fund_industry_distribution",
    "get_fund_types_percentage",
    "get_fund_codes",
    "get_fund_manager",
    "get_fund_realtime_increase_rate",
    "FundFactory",
    "FundProvider",
]
