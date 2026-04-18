"""
LOF (Listed Open-Ended Fund) data provider.
"""

from typing import Any

import pandas as pd

from ....core.base import ColumnsType, FilterType, SourceType
from ....core.factory import api_endpoint
from . import akshare
from .base import LOFFactory


@api_endpoint(LOFFactory)
def get_lof_list(
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get a comprehensive list of LOF funds.
    """
    pass


@api_endpoint(LOFFactory, method_name="get_lof_hist")
def get_lof_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get LOF historical data.
    """
    pass


@api_endpoint(LOFFactory, method_name="get_lof_spot")
def get_lof_spot(
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get LOF realtime quotes.
    """
    pass


@api_endpoint(LOFFactory, method_name="get_lof_nav")
def get_lof_nav(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get LOF Net Asset Value (NAV) history.
    """
    pass


__all__ = [
    "get_lof_list",
    "get_lof_hist_data",
    "get_lof_spot",
    "get_lof_nav",
    "LOFFactory",
]
