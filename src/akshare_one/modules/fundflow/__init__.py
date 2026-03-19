"""
Fund flow data module for PV.FundFlow.

This module provides interfaces to fetch fund flow data including:
- Individual stock fund flow
- Sector fund flow (industry and concept)
- Main fund flow rankings
- Industry and concept sector lists and constituents
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import FundFlowFactory
from . import eastmoney, sina  # 导入以触发 Provider 注册


@api_endpoint(FundFlowFactory)
def get_stock_fund_flow(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get individual stock fund flow data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(FundFlowFactory)
def get_sector_fund_flow(
    sector_type: Literal["industry", "concept"],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get sector fund flow data.

    Args:
        sector_type: Sector type ('industry' or 'concept')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(FundFlowFactory)
def get_main_fund_flow_rank(
    date: str,
    indicator: Literal["net_inflow", "net_inflow_rate"] = "net_inflow",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get main fund flow rankings.

    Args:
        date: Date in YYYY-MM-DD format
        indicator: Ranking indicator ('net_inflow' or 'net_inflow_rate')
    """
    pass


@api_endpoint(FundFlowFactory)
def get_industry_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get list of industry sectors.
    """
    pass


@api_endpoint(FundFlowFactory)
def get_industry_constituents(
    industry_code: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of an industry sector.

    Args:
        industry_code: Industry sector code
    """
    pass


@api_endpoint(FundFlowFactory)
def get_concept_list(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get list of concept sectors.
    """
    pass


@api_endpoint(FundFlowFactory)
def get_concept_constituents(
    concept_code: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of a concept sector.

    Args:
        concept_code: Concept sector code
    """
    pass


__all__ = [
    "get_stock_fund_flow",
    "get_sector_fund_flow",
    "get_main_fund_flow_rank",
    "get_industry_list",
    "get_industry_constituents",
    "get_concept_list",
    "get_concept_constituents",
    "FundFlowFactory",
]
