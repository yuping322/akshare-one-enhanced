"""
src/akshare_one/modules/etf/__init__.py
ETF and fund data module.
"""

from .base import ETFFactory
from . import eastmoney
from . import akshare
from . import lixinger
from ..factory_base import api_endpoint
from typing import Optional, List, Any
import pandas as pd


@api_endpoint(ETFFactory)
def get_etf_list(
    fund_type: str = "etf",
    source: Optional[str] = None,
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
    source: Optional[str] = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ETF historical data.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_etf_spot")
def get_etf_realtime_data(
    source: Optional[str] = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get all ETF realtime quotes.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_fund_manager")
def get_fund_manager_info(
    source: Optional[str] = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get fund manager information.
    """
    pass


@api_endpoint(ETFFactory, method_name="get_fund_rating")
def get_fund_rating_data(
    source: Optional[str] = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get fund ratings.
    """
    pass


@api_endpoint(ETFFactory)
def get_fund_nav(
    symbol: str,
    source: Optional[str] = None,
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
