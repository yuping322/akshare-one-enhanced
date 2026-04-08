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

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import MacroFactory
from . import official, sina, lixinger


@api_endpoint(MacroFactory)
def get_lpr_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get LPR (Loan Prime Rate) interest rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_pmi_index(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    pmi_type: Literal["manufacturing", "non_manufacturing", "caixin"] = "manufacturing",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get PMI (Purchasing Managers' Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        pmi_type: PMI type ('manufacturing', 'non_manufacturing', or 'caixin')
    """
    pass


@api_endpoint(MacroFactory)
def get_cpi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get CPI (Consumer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_ppi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get PPI (Producer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_m2_supply(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get M2 money supply data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_shibor_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get Shibor (Shanghai Interbank Offered Rate) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_social_financing(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get social financing scale data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


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
