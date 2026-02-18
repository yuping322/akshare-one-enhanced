"""
Macro economic data module for PV.MacroCN.

This module provides interfaces to fetch Chinese macro economic data including:
- LPR interest rates
- PMI indices (manufacturing, non-manufacturing, Caixin)
- CPI/PPI data
- M2 money supply
- Shibor interest rates
- Social financing scale
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import MacroFactory


def get_lpr_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get LPR (Loan Prime Rate) interest rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: LPR rate data with columns:
            - date: Date (YYYY-MM-DD)
            - lpr_1y: 1-year LPR rate (%)
            - lpr_5y: 5-year LPR rate (%)

    Example:
        >>> df = get_lpr_rate(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_lpr_rate(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_pmi_index(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    pmi_type: Literal["manufacturing", "non_manufacturing", "caixin"] = "manufacturing",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get PMI (Purchasing Managers' Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        pmi_type: PMI type ('manufacturing', 'non_manufacturing', or 'caixin')
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: PMI index data with columns:
            - date: Date (YYYY-MM-DD)
            - pmi_value: PMI value
            - yoy: Year-over-year change
            - mom: Month-over-month change

    Example:
        >>> df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_pmi_index(start_date, end_date, pmi_type)
    return provider.apply_data_filter(df, columns, row_filter)


def get_cpi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get CPI (Consumer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: CPI data with columns:
            - date: Date (YYYY-MM-DD)
            - current: Current month value
            - yoy: Year-over-year change (%)
            - mom: Month-over-month change (%)
            - cumulative: Cumulative value

    Example:
        >>> df = get_cpi_data(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_cpi_data(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_ppi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get PPI (Producer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: PPI data with columns:
            - date: Date (YYYY-MM-DD)
            - current: Current month value
            - yoy: Year-over-year change (%)
            - mom: Month-over-month change (%)
            - cumulative: Cumulative value

    Example:
        >>> df = get_ppi_data(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_ppi_data(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_m2_supply(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get M2 money supply data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: M2 supply data with columns:
            - date: Date (YYYY-MM-DD)
            - m2_balance: M2 balance (billion yuan)
            - yoy_growth_rate: Year-over-year growth rate (%)

    Example:
        >>> df = get_m2_supply(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_m2_supply(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_shibor_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get Shibor (Shanghai Interbank Offered Rate) interest rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Shibor rate data with columns:
            - date: Date (YYYY-MM-DD)
            - overnight: Overnight rate (%)
            - week_1: 1-week rate (%)
            - week_2: 2-week rate (%)
            - month_1: 1-month rate (%)
            - month_3: 3-month rate (%)
            - month_6: 6-month rate (%)
            - month_9: 9-month rate (%)
            - year_1: 1-year rate (%)

    Example:
        >>> df = get_shibor_rate(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_shibor_rate(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_social_financing(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["official"] = "official",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get social financing scale data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('official')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Social financing data with columns:
            - date: Date (YYYY-MM-DD)
            - total_scale: Total social financing scale (billion yuan)
            - yoy: Year-over-year change (%)
            - mom: Month-over-month change (%)
            - new_rmb_loans: New RMB loans (billion yuan)

    Example:
        >>> df = get_social_financing(start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = MacroFactory.get_provider(source=source)
    df = provider.get_social_financing(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_lpr_rate",
    "get_pmi_index",
    "get_cpi_data",
    "get_ppi_data",
    "get_m2_supply",
    "get_shibor_rate",
    "get_social_financing",
    "MacroFactory",
]
