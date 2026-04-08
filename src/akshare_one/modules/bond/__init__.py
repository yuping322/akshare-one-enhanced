"""
src/akshare_one/modules/bond/__init__.py
Bond module for conversion and standard bonds.
"""

from .base import BondFactory
from . import akshare
from ..factory_base import api_endpoint
from typing import Optional, Any
import pandas as pd


@api_endpoint(BondFactory)
def get_bond_list(
    source: Optional[str] = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
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
    source: Optional[str] = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get bond historical daily data.
    """
    pass


@api_endpoint(BondFactory, method_name="get_bond_spot")
def get_bond_realtime_data(
    source: Optional[str] = None, columns: list[str] | None = None, row_filter: dict[str, Any] | None = None
) -> pd.DataFrame:
    """
    Get bond realtime quotes.
    """
    pass


@api_endpoint(BondFactory)
def get_bond_premium(
    symbol: str,
    source: Optional[str] = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get conversion premium and related valuation metrics.
    """
    pass


__all__ = ["get_bond_list", "get_bond_hist_data", "get_bond_realtime_data", "get_bond_premium", "BondFactory"]
