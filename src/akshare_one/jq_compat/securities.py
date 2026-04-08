"""
src/akshare_one/jq_compat/securities.py
JQ-compatible security information APIs.
"""

import logging
import pandas as pd
import akshare as ak
from functools import lru_cache
from typing import List, Optional, Union
from ..modules.utils import normalize_symbol as _normalize_ak

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


def get_all_securities(types: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
    """Get all securities info. JQ-compatible."""
    try:
        df = ak.stock_info_a_code_name()
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(columns={"code": "code", "name": "display_name"})
        df["code"] = df["code"].astype(str).str.zfill(6)
        df["jq_code"] = df["code"].apply(
            lambda x: f"{x}.XSHG" if x.startswith("6") else f"{x}.XSHE"
        )
        df = df.set_index("jq_code")
        df["start_date"] = "2000-01-01"
        df["type"] = "stock"
        return df
    except Exception as e:
        logger.warning(f"get_all_securities failed: {e}")
        return pd.DataFrame()


@lru_cache(maxsize=1000)
def get_security_info(code: str, date: Optional[str] = None):
    """Get info for a single security. JQ-compatible."""
    try:
        clean = code.split(".")[0].zfill(6)
        df = ak.stock_individual_info_em(symbol=clean)
        if df is None or df.empty:
            return {"code": code, "display_name": code, "name": code,
                    "start_date": "2000-01-01", "type": "stock"}
        info = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return {
            "code": code,
            "display_name": info.get("股票简称", code),
            "name": info.get("股票简称", code),
            "start_date": info.get("上市时间", "2000-01-01"),
            "type": "stock",
        }
    except Exception as e:
        logger.debug(f"get_security_info failed for '{code}': {e}")
        return {"code": code, "display_name": code, "name": code,
                "start_date": "2000-01-01", "type": "stock"}


@lru_cache(maxsize=100)
def cached_get_index_stocks(index_symbol: str, date: Optional[str] = None) -> List[str]:
    """Get index constituent stocks with cache. JQ-compatible."""
    try:
        code = index_symbol.split(".")[0]
        df = ak.index_stock_cons(symbol=code)
        if df is None or df.empty:
            return []
        col = next((c for c in ["品种代码", "成分券代码", "code"] if c in df.columns), None)
        if not col:
            return []
        stocks = df[col].astype(str).str.zfill(6).tolist()
        return [f"{s}.XSHG" if s.startswith("6") else f"{s}.XSHE" for s in stocks]
    except Exception as e:
        logger.warning(f"cached_get_index_stocks failed for '{index_symbol}': {e}")
        return []


__all__ = ["get_all_securities", "get_security_info", "cached_get_index_stocks"]
