from typing import Any, List
import pandas as pd
from .base import BatchQueryFactory
from . import akshare as akshare_provider


def query_shareholder_top10(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询前十大股东

    Args:
        symbols: 股票代码列表

    Returns:
        pd.DataFrame: 批量股东数据
    """
    from ..shareholder import get_top_shareholders

    results = []
    for sym in symbols:
        try:
            df = get_top_shareholders(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_shareholder_float_top10(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询前十大流通股东"""
    from ..shareholderdepth import get_shareholder_structure

    results = []
    for sym in symbols:
        try:
            df = get_shareholder_structure(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_shareholder_num(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询股东户数"""
    from ..shareholder import get_latest_holder_number

    results = []
    for sym in symbols:
        try:
            df = get_latest_holder_number(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_dividend(
    symbols: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询分红数据"""
    from ..disclosure import get_dividend_data

    results = []
    for sym in symbols:
        try:
            df = get_dividend_data(sym, start_date=start_date, end_date=end_date)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_dividend_right(
    symbols: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询除权除息数据"""
    from ..dividendcalc import get_stock_bonus

    results = []
    for sym in symbols:
        try:
            df = get_stock_bonus(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_share_change(
    symbols: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询股东变动数据"""
    from ..shareholder import get_shareholder_changes

    results = []
    for sym in symbols:
        try:
            df = get_shareholder_changes(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_unlock(
    symbols: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询解禁数据"""
    from ..restricted import get_restricted_release

    results = []
    for sym in symbols:
        try:
            df = get_restricted_release(sym, start_date=start_date, end_date=end_date)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_pledge_data(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询质押数据"""
    from ..pledge import get_equity_pledge

    results = []
    for sym in symbols:
        try:
            df = get_equity_pledge(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_freeze_data(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询冻结数据"""
    from ..sharechangedepth import get_freeze_info

    results = []
    for sym in symbols:
        try:
            df = get_freeze_info(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_capital_change(
    symbols: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询股本变动数据"""
    from ..sharechangedepth import get_capital_change

    results = []
    for sym in symbols:
        try:
            df = get_capital_change(sym, start_date=start_date, end_date=end_date)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_index_components(
    index_codes: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询指数成分股"""
    from ..index import get_index_constituents

    results = []
    for code in index_codes:
        try:
            df = get_index_constituents(code)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_company_basic_info(
    symbols: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询公司基本信息"""
    from ..info import InfoDataFactory

    results = []
    for sym in symbols:
        try:
            provider = InfoDataFactory.get_provider(source or "sina", symbol=sym)
            df = provider.get_basic_info()
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def query_conversion_bond(
    bond_codes: list[str],
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """批量查询可转债信息"""
    from ..convertbond import get_convert_bond_info

    results = []
    for code in bond_codes:
        try:
            df = get_convert_bond_info(code)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


__all__ = [
    "query_shareholder_top10",
    "query_shareholder_float_top10",
    "query_shareholder_num",
    "query_dividend",
    "query_dividend_right",
    "query_share_change",
    "query_unlock",
    "query_pledge_data",
    "query_freeze_data",
    "query_capital_change",
    "query_index_components",
    "query_company_basic_info",
    "query_conversion_bond",
    "BatchQueryFactory",
]
