"""
Industry sector (行业板块) data module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import IndustryFactory
from . import eastmoney


@api_endpoint(IndustryFactory)
def get_industry_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get industry sector list.
    """
    pass


@api_endpoint(IndustryFactory)
def get_industry_stocks(
    industry: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stocks in an industry sector.

    Args:
        industry: Industry name or code
    """
    pass


__all__ = ["get_industry_list", "get_industry_stocks", "IndustryFactory"]
