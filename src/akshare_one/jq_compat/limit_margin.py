"""
src/akshare_one/jq_compat/limit_margin.py
JQ-compatible limit up/down and margin trading APIs.
"""

import logging
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional, List, Union
from .market import get_price as _get_price_jq
from ..modules.utils import normalize_symbol as _normalize_symbol
from ..constants import SYMBOL_ZFILL_WIDTH

logger = logging.getLogger(__name__)


def _normalize_date(date_val) -> Optional[str]:
    if date_val is None:
        return None
    if isinstance(date_val, str):
        return date_val
    try:
        return pd.to_datetime(date_val).strftime("%Y-%m-%d")
    except Exception:
        return str(date_val)


def get_recent_limit_up_stock(
    stock_list: List[str], recent_days: int = 5, date: Optional[str] = None, context=None
) -> List[str]:
    """Get stocks that hit limit up recently. JQ-compatible."""
    if not stock_list:
        return []
    end_date = _normalize_date(date) or datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=recent_days + 10)).strftime("%Y-%m-%d")

    limit_up_stocks = []
    for stock in stock_list:
        try:
            df = _get_price_jq(stock, start_date=start_date, end_date=end_date, fields=["close", "high_limit"])
            if df is None or df.empty:
                continue
            recent_df = df.tail(recent_days + 2)
            for _, row in recent_df.iterrows():
                close = row.get("close")
                high_limit = row.get("high_limit")
                if close and high_limit and abs(close - high_limit) / high_limit < 0.001:
                    limit_up_stocks.append(stock)
                    break
        except Exception as e:
            logger.debug(f"get_recent_limit_up_stock skipped '{stock}': {e}")
    return limit_up_stocks


def get_recent_limit_down_stock(
    stock_list: List[str], recent_days: int = 5, date: Optional[str] = None, context=None
) -> List[str]:
    """Get stocks that hit limit down recently. JQ-compatible."""
    if not stock_list:
        return []
    end_date = _normalize_date(date) or datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=recent_days + 10)).strftime("%Y-%m-%d")

    limit_down_stocks = []
    for stock in stock_list:
        try:
            df = _get_price_jq(stock, start_date=start_date, end_date=end_date, fields=["close", "low_limit"])
            if df is None or df.empty:
                continue
            recent_df = df.tail(recent_days + 2)
            for _, row in recent_df.iterrows():
                close = row.get("close")
                low_limit = row.get("low_limit")
                if close and low_limit and abs(close - low_limit) / low_limit < 0.001:
                    limit_down_stocks.append(stock)
                    break
        except Exception as e:
            logger.debug(f"get_recent_limit_down_stock skipped '{stock}': {e}")
    return limit_down_stocks


def get_mtss(
    security: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    count: Optional[int] = None,
    fields: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Get margin trading and short selling data. JQ-compatible."""
    start_date = _normalize_date(start_date)
    end_date = _normalize_date(end_date)
    try:
        if security:
            codes = [security] if isinstance(security, str) else security
            results = []
            for sym in codes:
                code = sym.split(".")[0].zfill(SYMBOL_ZFILL_WIDTH)
                market = "sh" if code.startswith("6") else "sz"
                df = (
                    ak.stock_margin_detail_szse(symbol=code)
                    if market == "sz"
                    else ak.stock_margin_detail_sse(symbol=code)
                )
                if df is not None and not df.empty:
                    df["code"] = sym
                    if start_date and "date" in df.columns:
                        df = df[df["date"] >= start_date]
                    if end_date and "date" in df.columns:
                        df = df[df["date"] <= end_date]
                    results.append(df)
            if not results:
                return pd.DataFrame()
            res = pd.concat(results, ignore_index=True)
        else:
            # Market-wide summary
            df_sh = ak.stock_margin_account_info_sse()
            df_sz = ak.stock_margin_account_info_szse()
            res = (
                pd.concat([df_sh, df_sz], ignore_index=True)
                if df_sh is not None and df_sz is not None
                else pd.DataFrame()
            )

        if count and not res.empty:
            res = res.tail(count)
        if fields and not res.empty:
            res = res[[c for c in fields if c in res.columns]]
        return res
    except Exception as e:
        logger.warning(f"get_mtss failed: {e}")
        return pd.DataFrame()


def get_margincash_stocks(date: Optional[str] = None) -> List[str]:
    """Get list of stocks eligible for margin trading. JQ-compatible."""
    try:
        df_sh = ak.stock_margin_underlying_info_sse()
        df_sz = ak.stock_margin_underlying_info_szse()
        stocks = []
        if df_sh is not None and not df_sh.empty:
            stocks.extend([f"{str(c).zfill(SYMBOL_ZFILL_WIDTH)}.XSHG" for c in df_sh["证券代码"]])
        if df_sz is not None and not df_sz.empty:
            stocks.extend([f"{str(c).zfill(SYMBOL_ZFILL_WIDTH)}.XSHE" for c in df_sz["证券代码"]])
        return list(set(stocks))
    except Exception as e:
        logger.warning(f"get_margincash_stocks failed: {e}")
        return []


def get_marginsec_stocks(date: Optional[str] = None) -> List[str]:
    """Get list of stocks eligible for short selling. JQ-compatible."""
    return get_margincash_stocks(date)


# Aliases
get_mtss_jq = get_mtss
get_margincash_stocks_jq = get_margincash_stocks
get_marginsec_stocks_jq = get_marginsec_stocks
get_margine_stocks_jq = get_margincash_stocks
get_margine_stocks = get_margincash_stocks

__all__ = [
    "get_recent_limit_up_stock",
    "get_recent_limit_down_stock",
    "get_mtss",
    "get_margincash_stocks",
    "get_marginsec_stocks",
    "get_margine_stocks",
    "get_mtss_jq",
    "get_margincash_stocks_jq",
    "get_marginsec_stocks_jq",
    "get_margine_stocks_jq",
]
