"""
Financial statements and metrics module.
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import cninfo, eastmoney_direct, lixinger, sina
from .base import FinancialDataFactory


@api_endpoint(FinancialDataFactory)
def get_balance_sheet(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get balance sheet data for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(FinancialDataFactory)
def get_income_statement(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get income statement data for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(FinancialDataFactory)
def get_cash_flow(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get cash flow statement data for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(FinancialDataFactory)
def get_financial_metrics(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get financial metrics for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


@api_endpoint(FinancialDataFactory)
def get_dividend_history(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dividend history for a stock.

    Args:
        symbol: Stock symbol
    """
    pass


__all__ = [
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
    "get_financial_metrics",
    "get_dividend_history",
    "FinancialDataFactory",
]
