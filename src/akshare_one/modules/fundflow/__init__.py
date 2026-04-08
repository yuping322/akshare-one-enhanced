"""
Fund flow (资金流向) data module for PV.FundFlow.

This module provides interfaces to fetch fund flow data including:
- Individual stock fund flow (main/small/large/medium/retail orders)
- Sector fund flow (industry and concept sectors)
- Main fund flow rankings by date and indicator
- Sector constituents and listings
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, efinance, sina
from .base import FundFlowFactory


@api_endpoint(FundFlowFactory)
def get_stock_fund_flow(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
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
    sector_type: Literal["industry", "concept"] = "industry",
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
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
    indicator: str = "main_net_inflow",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get main fund flow ranking.

    Args:
        date: Query date in YYYY-MM-DD format
        indicator: Ranking indicator (e.g., 'main_net_inflow', 'main_net_inflow_ratio')
    """
    pass


@api_endpoint(FundFlowFactory)
def get_industry_list(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(FundFlowFactory)
def get_industry_constituents(
    industry_code: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(FundFlowFactory)
def get_concept_list(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(FundFlowFactory)
def get_concept_constituents(
    concept_code: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(FundFlowFactory)
def get_sector_list(
    sector_type: Literal["industry", "concept"] = "industry",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get sector list.

    Args:
        sector_type: Sector type ('industry' or 'concept')
    """
    pass


@api_endpoint(FundFlowFactory)
def get_sector_constituents(
    sector_code: str,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of a sector.

    Args:
        sector_code: Sector code or name
    """
    pass


@api_endpoint(FundFlowFactory, method_name="get_history_bill")
def get_fundflow_history(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get historical fund flow data for a stock.

    Args:
        symbol: Stock symbol (e.g., '600000')
        source: Data source (default: None, will auto-select)
    """
    pass


@api_endpoint(FundFlowFactory, method_name="get_today_bill")
def get_fundflow_today(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get today's fund flow data for a stock.

    Args:
        symbol: Stock symbol (e.g., '600000')
        source: Data source (default: None, will auto-select)
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
    "get_sector_list",
    "get_sector_constituents",
    "get_fundflow_history",
    "get_fundflow_today",
    "FundFlowFactory",
]
