import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import FinancialDataFactory
from . import sina, cninfo, eastmoney_direct  # 触发 Provider 注册


@api_endpoint(FinancialDataFactory)
def get_balance_sheet(
    symbol: str,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get balance sheet data.

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
    Get income statement data.

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
    Get cash flow statement data.

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
    Get key financial metrics.

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
    Get dividend and bonus history.

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
