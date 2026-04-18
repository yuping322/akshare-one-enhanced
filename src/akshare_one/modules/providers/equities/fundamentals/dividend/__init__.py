from typing import Literal

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import baostock
from .base import DividendDataFactory


@api_endpoint(DividendDataFactory)
def get_dividend_data(
    symbol: str,
    start_date: str = "1990-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dividend and bonus distribution data.

    Args:
        symbol: Stock symbol (6 digits)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    pass


@api_endpoint(DividendDataFactory)
def get_adjust_factor(
    symbol: str,
    start_date: str = "1990-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock price adjustment factor data.

    Args:
        symbol: Stock symbol (6 digits)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    pass


__all__ = ["get_dividend_data", "get_adjust_factor", "DividendDataFactory"]
