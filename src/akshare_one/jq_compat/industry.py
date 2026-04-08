"""
src/akshare_one/jq_compat/industry.py
JQ-compatible industry APIs.
"""

from ..modules.industry import (
    get_industry_classify as _get_classify_ak,
    get_industry_stocks as _get_stocks_ak,
    get_industry_stocks_jq, get_industry_daily, get_market_breadth
)
from typing import List, Optional, Union
import pandas as pd

def get_industry_classify(level: str = "sw_l1") -> pd.DataFrame:
    """Get industry classification list."""
    return _get_classify_ak()

def get_industry_stocks(industry: str, date: Optional[str] = None) -> List[str]:
    """
    Get constituent stocks for a given industry. JQ-compatible.
    Falls back to Shenwan (SW) indices if direct board lookup fails.
    """
    try:
        # Try primary factory method first (Eastmoney/Direct)
        df = _get_stocks_ak(industry=industry)
        if df is not None and not df.empty:
            if "symbol" in df.columns:
                stocks = df["symbol"].tolist()
                return [f"{str(s).zfill(6)}.XSHG" if str(s).startswith("6") else f"{str(s).zfill(6)}.XSHE" for s in stocks]
        
        # Fallback to jk2bt-style SW Level 1 logic
        return get_industry_stocks_jq(industry)
    except Exception:
        return get_industry_stocks_jq(industry)

__all__ = ["get_industry_classify", "get_industry_stocks", "get_industry_daily", "get_market_breadth"]
