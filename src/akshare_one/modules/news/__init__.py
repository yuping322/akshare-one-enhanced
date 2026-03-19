import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import NewsDataFactory


@doc_params
def get_news_data(
    symbol: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stock news data.

    Args:
        symbol: Stock symbol
    """
    return NewsDataFactory.call_provider_method(
        "get_news_data",
        source=source,
        columns=columns,
        row_filter=row_filter,
        symbol=symbol,
    )


__all__ = ["get_news_data", "NewsDataFactory"]
