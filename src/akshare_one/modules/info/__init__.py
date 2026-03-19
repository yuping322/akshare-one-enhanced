import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import InfoDataFactory


@doc_params
def get_basic_info(
    symbol: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get basic stock information.

    Args:
        symbol: Stock symbol
    """
    return InfoDataFactory.call_provider_method(
        "get_basic_info",
        source=source,
        columns=columns,
        row_filter=row_filter,
        symbol=symbol,
    )


__all__ = ["get_basic_info", "InfoDataFactory"]
