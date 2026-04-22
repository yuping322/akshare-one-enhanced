"""
Index weights data provider.
"""

from typing import Any

import pandas as pd

from ....core.base import ColumnsType, FilterType, SourceType
from ....core.factory import api_endpoint
from . import csindex, tushare
from .base import IndexWeightsFactory


@api_endpoint(IndexWeightsFactory)
def get_index_weights(
    index_code: str,
    date: str = "",
    source: SourceType = "csindex",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """Get index component weights."""
    pass


@api_endpoint(IndexWeightsFactory)
def get_index_weights_history(
    index_code: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "csindex",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """Get index component weights history."""
    pass


@api_endpoint(IndexWeightsFactory)
def get_index_info(
    index_code: str = "",
    source: SourceType = "csindex",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """Get index basic information."""
    pass


__all__ = ["get_index_weights", "get_index_weights_history", "get_index_info", "IndexWeightsFactory"]
