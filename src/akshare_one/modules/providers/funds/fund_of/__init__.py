"""
FOF (Fund of Funds) data provider.
"""

from typing import Any

import pandas as pd

from ....core.base import ColumnsType, FilterType, SourceType
from ....core.factory import api_endpoint
from . import akshare
from .base import FOFFactory


@api_endpoint(FOFFactory)
def get_fof_list(
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get a comprehensive list of FOF funds.
    """
    pass


@api_endpoint(FOFFactory, method_name="get_fof_nav")
def get_fof_nav(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get FOF Net Asset Value (NAV) history.
    """
    pass


@api_endpoint(FOFFactory, method_name="get_fof_info")
def get_fof_info(
    symbol: str,
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get FOF fund information.
    """
    pass


__all__ = [
    "get_fof_list",
    "get_fof_nav",
    "get_fof_info",
    "FOFFactory",
]
