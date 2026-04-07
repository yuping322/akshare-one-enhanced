from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import HistoricalDataFactory
from . import eastmoney, eastmoney_direct, sina, tencent, netease


@api_endpoint(HistoricalDataFactory)
def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get historical stock data.

    Args:
        symbol: Stock symbol
        interval: Data interval
        interval_multiplier: Interval multiplier
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        adjust: Adjustment type
    """
    pass


__all__ = ["get_hist_data", "HistoricalDataFactory"]
