import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import RealtimeDataFactory
from . import eastmoney, xueqiu, eastmoney_direct  # 触发 Provider 注册


@api_endpoint(RealtimeDataFactory)
def get_realtime_data(
    symbol: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get realtime stock data.

    Args:
        symbol: Stock symbol
    """
    pass


__all__ = ["get_realtime_data", "RealtimeDataFactory"]
