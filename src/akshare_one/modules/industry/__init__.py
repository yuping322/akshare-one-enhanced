"""
Industry sector (行业板块) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import IndustryFactory


@doc_params
def get_industry_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get industry sector list.
    """
    return IndustryFactory.call_provider_method(
        "get_industry_list",
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_industry_stocks(
    industry: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stocks in an industry sector.

    Args:
        industry: Industry name (e.g., '银行', '房地产')
    """
    return IndustryFactory.call_provider_method(
        "get_industry_stocks",
        industry,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = ["get_industry_list", "get_industry_stocks", "IndustryFactory"]
