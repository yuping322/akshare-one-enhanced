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
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get individual stock fund flow data.

    Args:
        symbol: Stock symbol (e.g., '600000')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all). E.g., ["date", "main_net_inflow", "pct_change"]
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "pct_change > 5"}

    Returns:
        pd.DataFrame: Standardized fund flow data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - close: Closing price
            - pct_change: Price change percentage
            - main_net_inflow: Main fund net inflow
            - main_net_inflow_rate: Main fund net inflow rate
            - super_large_net_inflow: Super large order net inflow
            - large_net_inflow: Large order net inflow
            - medium_net_inflow: Medium order net inflow
            - small_net_inflow: Small order net inflow

    Example:
        >>> df = get_stock_fund_flow("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>> # Filter columns for LLM
        >>> df = get_stock_fund_flow("600000", columns=["date", "main_net_inflow"])
        >>> # Get top 10 rows
        >>> df = get_stock_fund_flow("600000", row_filter={"top_n": 10})
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_stock_fund_flow(symbol, start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_sector_fund_flow(
    sector_type: Literal["industry", "concept"],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get sector fund flow data.

    Args:
        sector_type: Sector type ('industry' or 'concept')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Standardized sector fund flow data with columns:
            - date: Date (YYYY-MM-DD)
            - sector_code: Sector code
            - sector_name: Sector name
            - sector_type: Sector type ('industry' or 'concept')
            - main_net_inflow: Main fund net inflow
            - pct_change: Price change percentage
            - leading_stock: Leading stock symbol
            - leading_stock_pct: Leading stock price change percentage

    Example:
        >>> df = get_sector_fund_flow("industry", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_sector_fund_flow(sector_type, start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_main_fund_flow_rank(
    date: str,
    indicator: Literal["net_inflow", "net_inflow_rate"] = "net_inflow",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get main fund flow ranking.

    Args:
        date: Date in YYYY-MM-DD format
        indicator: Ranking indicator ('net_inflow' or 'net_inflow_rate')
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Ranked fund flow data with columns:
            - rank: Ranking position
            - symbol: Stock symbol
            - name: Stock name
            - main_net_inflow: Main fund net inflow
            - pct_change: Price change percentage

    Example:
        >>> df = get_main_fund_flow_rank("2024-01-01", indicator="net_inflow")
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_main_fund_flow_rank(date, indicator)
    return provider.apply_data_filter(df, columns, row_filter)


def get_industry_list(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get list of industry sectors.

    Args:
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Industry sector list with columns:
            - sector_code: Sector code
            - sector_name: Sector name
            - constituent_count: Number of constituent stocks

    Example:
        >>> df = get_industry_list()
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_industry_list()
    return provider.apply_data_filter(df, columns, row_filter)


def get_industry_constituents(
    industry_code: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of an industry sector.

    Args:
        industry_code: Industry sector code
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Constituent stocks with columns:
            - symbol: Stock symbol
            - name: Stock name
            - weight: Weight in the sector (may be None)

    Example:
        >>> df = get_industry_constituents("BK0001")
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_industry_constituents(industry_code)
    return provider.apply_data_filter(df, columns, row_filter)


def get_concept_list(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get list of concept sectors.

    Args:
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Concept sector list with columns:
            - sector_code: Sector code
            - sector_name: Sector name
            - constituent_count: Number of constituent stocks

    Example:
        >>> df = get_concept_list()
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_concept_list()
    return provider.apply_data_filter(df, columns, row_filter)


def get_concept_constituents(
    concept_code: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get constituent stocks of a concept sector.

    Args:
        concept_code: Concept sector code
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Constituent stocks with columns:
            - symbol: Stock symbol
            - name: Stock name
            - weight: Weight in the sector (may be None)

    Example:
        >>> df = get_concept_constituents("BK0001")
        >>> print(df.head())
    """
    provider = FundFlowFactory.get_provider(source=source)
    df = provider.get_concept_constituents(concept_code)
    return provider.apply_data_filter(df, columns, row_filter)


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
