from typing import Literal

import pandas as pd

from .....core.base import ColumnsType, FilterType, SourceType
from .....core.factory import api_endpoint
from . import (
    baostock,
    cached_provider,
    eastmoney,
    eastmoney_direct,
    efinance,
    lixinger,
    netease,
    sina,
    tickflow,
    tencent,
    tushare,
)
from .base import HistoricalDataFactory


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
