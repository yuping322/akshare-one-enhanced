"""
Fund flow data module for PV.FundFlow.

This module provides interfaces to fetch fund flow data including:
- Individual stock fund flow
- Sector fund flow (industry and concept)
- Main fund flow rankings
- Industry and concept sector lists and constituents
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import FundFlowFactory


def get_stock_fund_flow(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get individual stock fund flow data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized fund flow data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_stock_fund_flow", symbol, start_date, end_date)
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_stock_fund_flow(symbol, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


def get_sector_fund_flow(
    sector_type: Literal["industry", "concept"],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get sector fund flow data.

    Args:
        sector_type: Sector type ('industry' or 'concept')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized sector fund flow data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_sector_fund_flow", sector_type, start_date, end_date)
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_sector_fund_flow(sector_type, start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


def get_main_fund_flow_rank(
    date: str,
    indicator: Literal["net_inflow", "net_inflow_rate"] = "net_inflow",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get main fund flow rankings.

    Args:
        date: Date in YYYY-MM-DD format
        indicator: Ranking indicator ('net_inflow' or 'net_inflow_rate')
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Ranked fund flow data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_main_fund_flow_rank", date, indicator)
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_main_fund_flow_rank(date, indicator)

    return apply_data_filter(df, columns, row_filter)


def get_industry_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get list of industry sectors.

    Args:
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Industry sector list
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_industry_list")
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_industry_list()

    return apply_data_filter(df, columns, row_filter)


def get_industry_constituents(
    industry_code: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of an industry sector.

    Args:
        industry_code: Industry sector code
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Constituent stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_industry_constituents", industry_code)
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_industry_constituents(industry_code)

    return apply_data_filter(df, columns, row_filter)


def get_concept_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get list of concept sectors.

    Args:
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Concept sector list
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_concept_list")
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_concept_list()

    return apply_data_filter(df, columns, row_filter)


def get_concept_constituents(
    concept_code: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of a concept sector.

    Args:
        concept_code: Concept sector code
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Constituent stocks
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FundFlowFactory.create_router(sources=source)
        df = router.execute("get_concept_constituents", concept_code)
    else:
        provider = FundFlowFactory.get_provider(source=source)
        df = provider.get_concept_constituents(concept_code)

    return apply_data_filter(df, columns, row_filter)


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
