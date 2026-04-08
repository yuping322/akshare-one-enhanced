"""
src/akshare_one/jq_compat/filter.py
JQ-compatible stock filtering APIs.
"""

import logging
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import Union, List, Optional

logger = logging.getLogger(__name__)


def _get_code_num(stock: str) -> str:
    """Normalize stock code to 6 digits."""
    if "." in stock:
        return stock.split(".")[0].zfill(6)
    return stock.zfill(6)


def _normalize_date(date_val) -> Optional[str]:
    if date_val is None:
        return None
    if isinstance(date_val, str):
        return date_val
    try:
        return pd.to_datetime(date_val).strftime("%Y-%m-%d")
    except Exception:
        return str(date_val)


def filter_st_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out ST stocks. JQ-compatible."""
    try:
        st_df = ak.stock_zh_a_st_em()
        if st_df is None or st_df.empty:
            return stock_list
        st_codes = set(st_df["代码"].astype(str).str.zfill(6).values)
        return [stock for stock in stock_list if _get_code_num(stock) not in st_codes]
    except Exception as e:
        logger.warning(f"filter_st_stock failed: {e}")
        return stock_list


filter_st = filter_st_stock


def filter_paused_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out suspended (paused) stocks. JQ-compatible."""
    try:
        stop_df = ak.stock_zh_a_stop_em()
        if stop_df is None or stop_df.empty:
            return stock_list
        paused_codes = set(stop_df["代码"].astype(str).str.zfill(6).values)
        return [stock for stock in stock_list if _get_code_num(stock) not in paused_codes]
    except Exception as e:
        logger.warning(f"filter_paused_stock failed: {e}")
        return stock_list


filter_paused = filter_paused_stock


def filter_limitup_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out stocks that have hit limit up. JQ-compatible."""
    from .market import get_detailed_quote as _get_quote
    clean_stocks = []
    for stock in stock_list:
        try:
            q = _get_quote(stock)
            if q.get("last_price", 0) < q.get("high_limit", 999999):
                clean_stocks.append(stock)
        except Exception:
            clean_stocks.append(stock)
    return clean_stocks


filter_limit_up = filter_limitup_stock


def filter_limitdown_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out stocks that have hit limit down. JQ-compatible."""
    from .market import get_detailed_quote as _get_quote
    clean_stocks = []
    for stock in stock_list:
        try:
            q = _get_quote(stock)
            if q.get("last_price", 0) > q.get("low_limit", 0):
                clean_stocks.append(stock)
        except Exception:
            clean_stocks.append(stock)
    return clean_stocks


filter_limit_down = filter_limitdown_stock


def filter_new_stock(stock_list: List[str], days: int = 250, date: Optional[str] = None) -> List[str]:
    """Filter out new stocks (listed less than 'days' ago). JQ-compatible."""
    from .securities import get_all_securities as _get_all_securities_jq
    try:
        securities = _get_all_securities_jq()
        if securities.empty:
            return stock_list
        date = _normalize_date(date)
        ref_date = pd.to_datetime(date) if date else datetime.now()
        cutoff_date = ref_date - pd.Timedelta(days=days)

        clean_stocks = []
        for stock in stock_list:
            match = securities[securities.index == stock]
            if not match.empty:
                start_date = pd.to_datetime(match.iloc[0]["start_date"])
                if start_date <= cutoff_date:
                    clean_stocks.append(stock)
            else:
                clean_stocks.append(stock)
        return clean_stocks
    except Exception as e:
        logger.warning(f"filter_new_stock failed: {e}")
        return stock_list


filter_new_stocks = filter_new_stock


def apply_common_filters(
    stock_list: List[str],
    date: Optional[str] = None,
    filter_st: bool = True,
    filter_paused: bool = True,
    filter_new: bool = True,
    new_stock_days: int = 250,
) -> List[str]:
    """Apply common filters (ST, Paused, New). JQ-compatible."""
    res = list(stock_list)
    if filter_st:
        res = filter_st_stock(res, date)
    if filter_paused:
        res = filter_paused_stock(res, date)
    if filter_new:
        res = filter_new_stock(res, new_stock_days, date)
    return res


def get_dividend_ratio_filter_list(threshold: float = 0.03, date: Optional[str] = None) -> List[str]:
    """Get stocks with dividend yield >= threshold. JQ-compatible."""
    try:
        df = ak.stock_dividend_cninfo()
        if df is None or df.empty:
            return []
        # 找股息率列
        yield_col = next((c for c in df.columns if "股息率" in c or "yield" in c.lower()), None)
        code_col = next((c for c in df.columns if "代码" in c or "code" in c.lower()), None)
        if not yield_col or not code_col:
            return []
        df[yield_col] = pd.to_numeric(df[yield_col].astype(str).str.replace("%", ""), errors="coerce") / 100
        filtered = df[df[yield_col] >= threshold]
        codes = filtered[code_col].astype(str).str.zfill(6).tolist()
        return [f"{c}.XSHG" if c.startswith("6") else f"{c}.XSHE" for c in codes]
    except Exception as e:
        logger.warning(f"get_dividend_ratio_filter_list failed: {e}")
        return []


def get_margine_stocks(date: Optional[str] = None) -> List[str]:
    """Get list of margin trading eligible stocks. JQ-compatible alias."""
    from .limit_margin import get_margincash_stocks
    return get_margincash_stocks(date)


def filter_kcb_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out Star Market (STAR) stocks (starting with 688). JQ-compatible."""
    return [s for s in stock_list if not _get_code_num(s).startswith("688")]


def filter_kcbj_stock(stock_list: List[str], date: Optional[str] = None) -> List[str]:
    """Filter out STAR and BJ market stocks. JQ-compatible."""
    return [s for s in stock_list if not (
        _get_code_num(s).startswith("688") or
        _get_code_num(s).startswith("8") or
        _get_code_num(s).startswith("4")
    )]


__all__ = [
    "filter_st", "filter_st_stock", "filter_paused", "filter_paused_stock",
    "filter_limit_up", "filter_limitup_stock", "filter_limit_down", "filter_limitdown_stock",
    "filter_new_stock", "filter_new_stocks", "apply_common_filters",
    "get_dividend_ratio_filter_list", "get_margine_stocks",
    "filter_kcb_stock", "filter_kcbj_stock",
]
