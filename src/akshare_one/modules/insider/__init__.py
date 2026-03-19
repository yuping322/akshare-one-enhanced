import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import InsiderDataFactory


@doc_params
def get_inner_trade_data(
    symbol: str,
    source: SourceType = "xueqiu",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get insider trading data.

    Args:
        symbol: Stock symbol
    """
    return InsiderDataFactory.call_provider_method(
        "get_inner_trade_data",
        source=source,
        columns=columns,
        row_filter=row_filter,
        symbol=symbol,
    )


__all__ = ["get_inner_trade_data", "InsiderDataFactory"]
