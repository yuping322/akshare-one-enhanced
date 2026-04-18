"""
Convertible Bond (可转债) data provider.

This module provides interfaces to fetch convertible bond data including:
- Convertible bond list
- Convertible bond details
- Historical quotes
- Realtime quotes
- Premium rates
- Stock-to-bond mapping
"""

from typing import Any

import pandas as pd

from ....core.base import ColumnsType, FilterType, SourceType
from ....core.factory import api_endpoint
from . import akshare
from .base import ConvertBondFactory


@api_endpoint(ConvertBondFactory)
def get_convert_bond_list(
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债列表

    返回当前市场上所有可转债的基本信息列表。

    Returns:
        pd.DataFrame: 可转债列表数据
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_info(
    symbol: str,
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债详细信息

    Args:
        symbol: 可转债代码

    Returns:
        pd.DataFrame: 可转债详细信息
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债历史行情

    Args:
        symbol: 可转债代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        pd.DataFrame: 可转债历史行情数据
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_spot(
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债实时行情

    返回当前市场上所有可转债的实时行情数据。

    Returns:
        pd.DataFrame: 可转债实时行情数据
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_premium(
    symbol: str,
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债溢价率

    Args:
        symbol: 可转债代码

    Returns:
        pd.DataFrame: 可转债溢价率数据
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_by_stock(
    stock_code: str,
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取正股对应的可转债

    Args:
        stock_code: 正股代码

    Returns:
        pd.DataFrame: 正股对应的可转债列表
    """
    pass


@api_endpoint(ConvertBondFactory)
def get_convert_bond_quote(
    symbol: str,
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债实时报价

    Args:
        symbol: 可转债代码

    Returns:
        pd.DataFrame: 可转债实时报价数据
    """
    pass


def calculate_conversion_value(conversion_price: float, stock_price: float) -> float:
    """
    计算转股价值

    转股价值 = (100 / 转股价格) * 正股价格

    Args:
        conversion_price: 转股价格
        stock_price: 正股价格

    Returns:
        float: 转股价值
    """
    if conversion_price <= 0:
        return 0.0
    return (100.0 / conversion_price) * stock_price


def calculate_premium_rate(bond_price: float, conversion_value: float) -> float:
    """
    计算溢价率

    溢价率 = (债券价格 - 转股价值) / 转股价值 * 100

    Args:
        bond_price: 债券价格
        conversion_value: 转股价值

    Returns:
        float: 溢价率（百分比）
    """
    if conversion_value <= 0:
        return 0.0
    return (bond_price - conversion_value) / conversion_value * 100.0


def get_convert_bond_daily(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "akshare",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    获取可转债日线数据（get_convert_bond_hist 的别名）

    Args:
        symbol: 可转债代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        pd.DataFrame: 可转债日线数据
    """
    return get_convert_bond_hist(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_convert_bond_list",
    "get_convert_bond_info",
    "get_convert_bond_hist",
    "get_convert_bond_spot",
    "get_convert_bond_premium",
    "get_convert_bond_by_stock",
    "get_convert_bond_quote",
    "get_convert_bond_daily",
    "calculate_conversion_value",
    "calculate_premium_rate",
    "ConvertBondFactory",
]
