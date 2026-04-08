"""
src/akshare_one/jq_compat/financial_indicator.py
JQ-compatible financial indicator APIs.
"""

import pandas as pd
import akshare as ak
from typing import Optional, List, Union

def _normalize_code(code: str) -> str:
    return code.replace(".XSHG", "").replace(".XSHE", "").replace("sh", "").replace("sz", "").zfill(6)

def _to_jq_code(code: str) -> str:
    code = _normalize_code(code)
    return f"{code}.XSHG" if code.startswith("6") else f"{code}.XSHE"

def bank_indicator(
    security: Optional[Union[str, List[str]]] = None,
    fields: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get bank industry indicators. JQ-compatible."""
    try:
        df = ak.stock_bank_indicator_em()
        if df is None or df.empty: return pd.DataFrame(columns=["code", "date"])
        
        df = df.rename(columns={"代码": "code", "名称": "name", "公告日期": "date"})
        df["code"] = df["code"].apply(_to_jq_code)
        
        if security:
            if isinstance(security, str): security = [security]
            df = df[df["code"].isin(security)]
            
        return df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["code", "date"])

def security_indicator(
    security: Optional[Union[str, List[str]]] = None,
    fields: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get security industry indicators. JQ-compatible."""
    try:
        df = ak.stock_zhengquan_indicator_em() # Correct name for securities
        if df is None or df.empty: return pd.DataFrame(columns=["code", "date"])
        
        df = df.rename(columns={"代码": "code", "名称": "name", "公告日期": "date"})
        df["code"] = df["code"].apply(_to_jq_code)
        
        if security:
            if isinstance(security, str): security = [security]
            df = df[df["code"].isin(security)]
            
        return df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["code", "date"])

def insurance_indicator(
    security: Optional[Union[str, List[str]]] = None,
    fields: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get insurance industry indicators. JQ-compatible."""
    # Insurance often doesn't have a dedicated "indicator" API in EM, using general
    return pd.DataFrame(columns=["code", "date"])

# Aliases
bank_indicator_jq = bank_indicator
security_indicator_jq = security_indicator
insurance_indicator_jq = insurance_indicator

__all__ = [
    "bank_indicator", "security_indicator", "insurance_indicator",
    "bank_indicator_jq", "security_indicator_jq", "insurance_indicator_jq"
]
