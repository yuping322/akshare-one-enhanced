from typing import Any, Literal

import pandas as pd

from .factory import FinancialDataFactory


def get_balance_sheet(
    symbol: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get balance sheet data.

    Args:
        symbol: Stock symbol
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Balance sheet data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FinancialDataFactory.create_router(sources=source, symbol=symbol)
        df = router.execute("get_balance_sheet")
    else:
        provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
        df = provider.get_balance_sheet()

    return apply_data_filter(df, columns, row_filter)


def get_income_statement(
    symbol: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get income statement data.

    Args:
        symbol: Stock symbol
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Income statement data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FinancialDataFactory.create_router(sources=source, symbol=symbol)
        df = router.execute("get_income_statement")
    else:
        provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
        df = provider.get_income_statement()

    return apply_data_filter(df, columns, row_filter)


def get_cash_flow(
    symbol: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get cash flow statement data.

    Args:
        symbol: Stock symbol
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Cash flow data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FinancialDataFactory.create_router(sources=source, symbol=symbol)
        df = router.execute("get_cash_flow")
    else:
        provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
        df = provider.get_cash_flow()

    return apply_data_filter(df, columns, row_filter)


def get_financial_metrics(
    symbol: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get financial metrics data.

    Args:
        symbol: Stock symbol
        source: Data source(s)
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Financial metrics data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = FinancialDataFactory.create_router(sources=source, symbol=symbol)
        df = router.execute("get_financial_metrics")
    else:
        provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
        df = provider.get_financial_metrics()

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
    "get_financial_metrics",
    "FinancialDataFactory",
]
