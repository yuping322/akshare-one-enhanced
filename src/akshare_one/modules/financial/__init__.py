from typing import Any, Literal

import pandas as pd

from .factory import FinancialDataFactory


def get_balance_sheet(
    symbol: str,
    source: Literal["sina", "eastmoney_direct", "cninfo"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_balance_sheet()
    return provider.apply_data_filter(df, columns, row_filter)


def get_income_statement(
    symbol: str,
    source: Literal["sina", "eastmoney_direct", "cninfo"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_income_statement()
    return provider.apply_data_filter(df, columns, row_filter)


def get_cash_flow(
    symbol: str,
    source: Literal["sina", "eastmoney_direct", "cninfo"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_cash_flow()
    return provider.apply_data_filter(df, columns, row_filter)


def get_financial_metrics(
    symbol: str,
    source: Literal["eastmoney_direct", "sina", "cninfo"] = "eastmoney_direct",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    provider = FinancialDataFactory.get_provider(source=source, symbol=symbol)
    df = provider.get_financial_metrics()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
    "get_financial_metrics",
    "FinancialDataFactory",
]
