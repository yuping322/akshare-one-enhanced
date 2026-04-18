"""
src/akshare_one/modules/etf/__init__.py
ETF and fund data module.
"""

from typing import Any, List, Optional

import pandas as pd

from ..factory_base import api_endpoint
from . import eastmoney, lixinger
from .base import ETFFactory


@api_endpoint(ETFFactory)
def get_etf_list(
    fund_type: str = "etf",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
):
    """
    Get a comprehensive list of funds (etf, lof, or reits).
    """
    pass


@api_endpoint(ETFFactory, method_name="get_etf_hist")
def get_etf_hist_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "daily",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ETF historical data.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_etf_spot")
def get_etf_realtime_data(
    source: str | None = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get all ETF realtime quotes.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_fund_manager")
def get_fund_manager_info(
    source: str | None = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get fund manager information.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_fund_rating")
def get_fund_rating_data(
    source: str | None = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get fund ratings.
    """
    pass


@api_endpoint(ETFFactory)
def get_fund_nav(
    symbol: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get Net Asset Value (NAV) history for a given fund.
    """
    pass


# Aliases
get_fund_list = get_etf_list
FundFactory = ETFFactory

__all__ = [
    "get_etf_list",
    "get_fund_list",
    "get_etf_hist_data",
    "get_etf_realtime_data",
    "get_fund_manager_info",
    "get_fund_rating_data",
    "get_fund_nav",
    "ETFFactory",
    "FundFactory",
]
