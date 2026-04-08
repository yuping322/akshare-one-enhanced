"""
src/akshare_one/jq_compat/valuation.py
JQ-compatible valuation APIs.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Union, List, Optional, Dict
from ..modules.valuation import get_stock_valuation as _get_valuation_ak
from ..modules.valuation import get_market_valuation as _get_market_valuation_ak

logger = logging.getLogger(__name__)


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


def get_valuation(
    security: Union[str, List[str]],
    date: Optional[str] = None,
    fields: Optional[List[str]] = None,
    count: Optional[int] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Get stock valuation data. JQ-compatible.
    
    Fields mapping:
    - code: stock code
    - day: date
    - pe_ratio: PE
    - pb_ratio: PB
    - ps_ratio: PS
    - market_cap: total market cap (100M)
    - circulating_market_cap: circulating market cap (100M)
    """
    if isinstance(security, str):
        security = [security]
        
    date = _normalize_date(date)
    results = []
    
    for sym in security:
        try:
            # We use the underlying module which handles multiple sources
            df = _get_valuation_ak(
                symbol=sym,
                start_date=date or "1970-01-01",
                end_date=date or datetime.now().strftime("%Y-%m-%d"),
                **kwargs
            )
            
            if not df.empty:
                if count:
                    df = df.tail(count)
                df["code"] = sym
                results.append(df)
        except Exception as e:
            logger.warning(f"get_valuation failed for '{sym}': {e}")
            
    if not results:
        return pd.DataFrame()
        
    res = pd.concat(results, ignore_index=True)
    
    # Standardize column names to JQ style if they aren't already
    mapping = {
        "pe": "pe_ratio",
        "pb": "pb_ratio",
        "ps": "ps_ratio",
        "total_mv": "market_cap",
        "circ_mv": "circulating_market_cap",
        "date": "day"
    }
    res = res.rename(columns=mapping)
    
    # Filter fields if requested
    if fields:
        # Always include code and day if not specified but present
        final_fields = list(fields)
        if "code" not in final_fields and "code" in res.columns:
            final_fields.insert(0, "code")
        if "day" not in final_fields and "day" in res.columns:
            final_fields.insert(1, "day")
            
        res = res[[f for f in final_fields if f in res.columns]]
        
    return res


def get_index_valuation(
    index_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[List[str]] = None,
    count: Optional[int] = None,
    **kwargs
) -> pd.DataFrame:
    """Get index valuation history. JQ-compatible."""
    start_date = _normalize_date(start_date)
    end_date = _normalize_date(end_date)
    
    # Reuse stock valuation logic if applicable or call market valuation
    return get_valuation(index_code, date=end_date, fields=fields, count=count, **kwargs)


def batch_get_fundamentals(query, date: Optional[str] = None, count: Optional[int] = None) -> pd.DataFrame:
    """
    Batch get fundamentals (valuation only in this implementation).
    Deprecated: use get_fundamentals for full table support.
    """
    from .securities import get_all_securities
    date = _normalize_date(date)
    stocks = get_all_securities().index.tolist()
    return get_valuation(stocks, date=date, count=count)


get_valuation_jq = get_valuation
get_index_valuation_jq = get_index_valuation

__all__ = [
    "get_valuation", "get_index_valuation", "batch_get_fundamentals",
    "get_valuation_jq", "get_index_valuation_jq"
]
