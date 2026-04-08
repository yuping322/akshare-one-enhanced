"""
src/akshare_one/jq_compat/market.py
JQ-compatible market data APIs.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Union, List, Optional, Dict, Any

from ..modules.historical import get_hist_data
from .valuation import get_valuation as _get_valuation_jq
from .valuation import batch_get_fundamentals as _batch_get_fundamentals_jq
from ..modules.utils import normalize_symbol as _normalize_symbol_ak

logger = logging.getLogger(__name__)

_FREQ_MAP = {
    "daily": "day", "1d": "day", "minute": "minute", "1m": "minute",
    "5m": "minute", "15m": "minute", "30m": "minute", "60m": "minute",
    "weekly": "week", "1w": "week", "monthly": "month", "1M": "month",
}

_ADJUST_MAP = {
    "pre": "qfq", "post": "hfq", "none": "none", None: "none",
}


def _parse_frequency(frequency: str) -> tuple:
    if frequency in ("daily", "1d", "weekly", "1w", "monthly", "1M"):
        return _FREQ_MAP[frequency], 1
    if frequency.endswith("m"):
        try:
            return "minute", int(frequency[:-1])
        except ValueError:
            return "minute", 1
    return _FREQ_MAP.get(frequency, "day"), 1


def _normalize_symbol(symbol: str) -> str:
    return _normalize_symbol_ak(symbol)


def _normalize_date(date_val) -> Optional[str]:
    """Normalize date to YYYY-MM-DD string."""
    if date_val is None:
        return None
    if isinstance(date_val, str):
        return date_val
    try:
        return pd.to_datetime(date_val).strftime("%Y-%m-%d")
    except Exception:
        return str(date_val)


def get_price(security, start_date=None, end_date=None, frequency="daily",
              fields=None, skip_paused=False, fq="pre", count=None,
              panel=True, fill_paused=True, **kwargs):
    """Get historical price data. JQ-compatible."""
    interval, multiplier = _parse_frequency(frequency)
    adjust = _ADJUST_MAP.get(fq, "qfq")
    start_date = _normalize_date(start_date)
    end_date = _normalize_date(end_date)
    if count and not start_date:
        start_date = "1970-01-01"
    if isinstance(security, str):
        security = [security]
    results = {}
    for sym in security:
        try:
            df = get_hist_data(
                symbol=sym,
                interval=interval,
                interval_multiplier=multiplier,
                start_date=start_date or "1970-01-01",
                end_date=end_date or datetime.now().strftime("%Y-%m-%d"),
                adjust=adjust,
                source="duckdb_cache",
                **kwargs,
            )
            if df.empty:
                results[sym] = pd.DataFrame()
                continue
            if count:
                df = df.tail(count)
            results[sym] = df.reset_index(drop=True)
        except Exception as e:
            logger.warning(f"get_price failed for '{sym}': {e}")
            results[sym] = pd.DataFrame()
    if len(security) == 1 and not panel:
        return results[security[0]]
    return results if panel else pd.concat(results.values(), keys=results.keys())


def get_bars(security, count, unit="1d", fields=None, include_now=False,
             end_dt=None, fq="pre", skip_paused=False, **kwargs):
    """Get K-line bars. JQ-compatible."""
    return get_price(security, end_date=end_dt, frequency=unit, fields=fields,
                     skip_paused=skip_paused, fq=fq, count=count, panel=False, **kwargs)


def history(count, unit="1d", field="close", security_list=None, df=True,
            skip_paused=True, fq="pre", end_date=None, **kwargs):
    """Get historical data in JQ style."""
    if not security_list:
        return pd.DataFrame() if df else {}
    end_date = _normalize_date(end_date)
    res = get_price(security_list, end_date=end_date, frequency=unit,
                    fields=[field, "datetime"], skip_paused=skip_paused,
                    fq=fq, count=count, panel=True, **kwargs)
    if not df:
        return {s: d[field].values for s, d in res.items() if not d.empty and field in d.columns}
    all_series = []
    for s, d in res.items():
        if not d.empty and field in d.columns and "datetime" in d.columns:
            all_series.append(d.set_index("datetime")[field].rename(s))
    return pd.concat(all_series, axis=1) if all_series else pd.DataFrame()


def attribute_history(security, count, unit="1d", fields=None, skip_paused=True,
                      df=True, fq="pre", end_date=None, **kwargs):
    """Get attribute history for a single security. JQ-compatible."""
    end_date = _normalize_date(end_date)
    res = get_price(security, end_date=end_date, frequency=unit, fields=fields,
                    skip_paused=skip_paused, fq=fq, count=count, panel=False, **kwargs)
    if not df:
        return {c: res[c].values for c in res.columns if c != "datetime"}
    return res.set_index("datetime") if isinstance(res, pd.DataFrame) and "datetime" in res.columns else res


def get_valuation(security, date=None, fields=None, count=None, **kwargs):
    """Get stock valuation data. JQ-compatible (batch)."""
    return _get_valuation_jq(security, date=date, fields=fields, count=count, **kwargs)


def get_index_valuation(index_code, start_date=None, end_date=None,
                         fields=None, count=None, **kwargs):
    """Get index valuation history. JQ-compatible."""
    return get_valuation(index_code, date=end_date, fields=fields, count=count, **kwargs)


def batch_get_fundamentals(query, date=None, count=None):
    """Batch get fundamentals. JQ-compatible."""
    return _batch_get_fundamentals_jq(query, date=date, count=count)


def get_detailed_quote(security, date=None):
    """Get detailed real-time quote. JQ-compatible."""
    from ..modules.realtime import RealtimeDataFactory
    if isinstance(security, str):
        security = [security]
    results = {}
    for sym in security:
        try:
            df = RealtimeDataFactory.get_instance().get_realtime_data(sym)
            results[sym] = df.to_dict("records")[0] if not df.empty else {}
        except Exception as e:
            logger.warning(f"get_detailed_quote failed for '{sym}': {e}")
            results[sym] = {}
    return results[security[0]] if len(security) == 1 else results


def get_ticks_enhanced(security, count=100, fields=None, df=True, date=None):
    """Get tick data. JQ-compatible."""
    import akshare as ak
    sym = _normalize_symbol(security)
    try:
        result = ak.stock_zh_a_tick_tx_js(symbol=sym)
        if result is None:
            return pd.DataFrame()
        result = result.tail(count)
        if fields:
            result = result[[c for c in fields if c in result.columns]]
        return result if df else result.to_dict("records")
    except Exception as e:
        logger.warning(f"get_ticks_enhanced failed for '{security}': {e}")
        return pd.DataFrame() if df else []


def get_market(security, start_date=None, end_date=None, frequency="daily",
               fields=None, count=None, fq="pre"):
    """Get market data. JQ-compatible."""
    return get_price(security, start_date=start_date, end_date=end_date,
                     frequency=frequency, fields=fields, count=count,
                     fq=fq, panel=False)


def get_open_price(security, date=None):
    """Get open price. JQ-compatible."""
    return get_detailed_quote(security, date).get("open", 0.0)


def get_close_price(security, date=None):
    """Get close/last price. JQ-compatible."""
    return get_detailed_quote(security, date).get("price", 0.0)


def get_high_limit(security, date=None):
    """Get high limit price. JQ-compatible."""
    return get_detailed_quote(security, date).get("high_limit", 0.0)


def get_low_limit(security, date=None):
    """Get low limit price. JQ-compatible."""
    return get_detailed_quote(security, date).get("low_limit", 0.0)


get_price_jq = get_price
get_bars_jq = get_bars
get_valuation_jq = get_valuation
get_index_valuation_jq = get_index_valuation

__all__ = [
    "get_price", "get_bars", "history", "attribute_history",
    "get_valuation", "get_index_valuation", "get_market",
    "get_detailed_quote", "get_ticks_enhanced",
    "get_price_jq", "get_bars_jq", "get_valuation_jq", "get_index_valuation_jq",
    "batch_get_fundamentals",
    "get_open_price", "get_close_price", "get_high_limit", "get_low_limit",
]
