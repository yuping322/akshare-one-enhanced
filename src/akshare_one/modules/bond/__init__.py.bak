"""
src/akshare_one/modules/bond/__init__.py
Bond module for conversion and standard bonds.
"""

from typing import Any, Optional

import pandas as pd

from ..factory_base import api_endpoint
from . import jsl
from .base import BondFactory


@api_endpoint(BondFactory, method_name="get_bond_list")
def get_bond_list(
    source: str | None = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get a comprehensive list of active conversion bonds.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_hist")
def get_bond_hist_data(
    symbol: str,
    start_date: str,
    end_date: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond historical daily data.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_spot")
def get_bond_realtime_data(
    source: str | None = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get bond realtime quotes.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_premium")
def get_bond_premium(
    symbol: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get conversion premium and related valuation metrics.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_deal_detail")
def get_bond_deal_detail(
    bond_code: str,
    max_count: int = 100,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond deal details.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_history_bill")
def get_bond_history_bill(
    bond_code: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond historical fund flow.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_today_bill")
def get_bond_today_bill(
    bond_code: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond today's fund flow.
    """
    pass


__all__ = [
    "get_bond_list",
    "get_bond_hist_data",
    "get_bond_realtime_data",
    "get_bond_premium",
    "get_bond_deal_detail",
    "get_bond_history_bill",
    "get_bond_today_bill",
    "BondFactory",
]
