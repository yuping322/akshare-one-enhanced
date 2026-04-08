"""
src/akshare_one/jq_compat/finance.py
JQ-compatible finance and fundamental data APIs.
"""

import logging
import pandas as pd
import akshare as ak
from typing import Optional, List, Union, Dict
from datetime import datetime
from ..modules.financial import get_balance_sheet as _get_bs_ak
from ..modules.financial import get_income_statement as _get_is_ak
from ..modules.financial import get_cash_flow as _get_cf_ak
from ..modules.financial import get_financial_metrics as _get_fm_ak
from .valuation import get_valuation as _get_valuation_jq

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


def get_locked_shares(
    stock_list: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    forward_count: int = 90,
) -> pd.DataFrame:
    """Get restricted shares release info. JQ-compatible."""
    try:
        df = ak.stock_restricted_release_summary_em()
        if df.empty:
            return pd.DataFrame(columns=["code", "unlock_date", "unlock_shares", "unlock_ratio", "unlock_value"])

        column_mapping = {
            "股票代码": "code", "解禁日期": "unlock_date",
            "解禁股数": "unlock_shares", "解禁市值": "unlock_value",
            "占流通股比例": "unlock_ratio",
        }
        df = df.rename(columns=column_mapping)

        if "code" in df.columns:
            df["code"] = df["code"].apply(lambda x: str(x).zfill(6))
            df["code"] = df["code"].apply(lambda x: f"{x}.XSHG" if x.startswith("6") else f"{x}.XSHE")

        if "unlock_date" in df.columns:
            df["unlock_date"] = pd.to_datetime(df["unlock_date"])
            if start_date:
                df = df[df["unlock_date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["unlock_date"] <= pd.to_datetime(end_date)]

        if stock_list:
            if isinstance(stock_list, str):
                stock_list = [stock_list]
            df = df[df["code"].isin(stock_list)]

        return df.reset_index(drop=True)
    except Exception as e:
        logger.warning(f"get_locked_shares failed: {e}")
        return pd.DataFrame(columns=["code", "unlock_date", "unlock_shares", "unlock_ratio", "unlock_value"])


def get_fund_info(fund_code: str, fields: Optional[List[str]] = None) -> Dict:
    """Get fund basic info. JQ-compatible."""
    try:
        df = ak.fund_name_em()
        if df.empty:
            return {}
        fund_row = df[df["基金代码"] == fund_code.zfill(6)]
        if fund_row.empty:
            return {}
        row = fund_row.iloc[0]
        result = {
            "fund_code": fund_code,
            "fund_name": row.get("基金简称", ""),
            "fund_type": row.get("基金类型", ""),
            "inception_date": row.get("成立日期", ""),
        }
        if fields:
            result = {k: v for k, v in result.items() if k in fields}
        return result
    except Exception as e:
        logger.warning(f"get_fund_info failed for '{fund_code}': {e}")
        return {}


def get_fundamentals(
    query,
    date: Optional[str] = None,
    statDate: Optional[str] = None,
) -> pd.DataFrame:
    """
    Query fundamental data. JQ-compatible.

    Args:
        query: Query object (with .table and .code attributes) or table name as string
        date: Query date (latest data as of this date)
        statDate: Statutory date (reporting period e.g. '2023' or '2023q1')
    """
    table_name = getattr(query, "table", str(query))
    security = getattr(query, "code", None)
    fields = getattr(query, "fields", None)

    date = _normalize_date(date)
    
    # If no security provided in query, get all active securities
    if not security:
        from .securities import get_all_securities
        security = get_all_securities().index.tolist()
    
    if isinstance(security, str):
        security = [security]

    results = []
    
    for sym in security:
        try:
            if table_name in ("valuation", "valuation_jq"):
                df = _get_valuation_jq(sym, date=date)
            elif table_name in ("balance_sheet", "balance"):
                df = _get_bs_ak(symbol=sym, source="sina")
            elif table_name in ("income_statement", "income"):
                df = _get_is_ak(symbol=sym, source="sina")
            elif table_name in ("cash_flow",):
                df = _get_cf_ak(symbol=sym, source="sina")
            elif table_name in ("indicator", "financial_indicator"):
                df = _get_fm_ak(symbol=sym, source="eastmoney_direct")
            else:
                logger.warning(f"Unknown table '{table_name}' in get_fundamentals")
                continue

            if not df.empty:
                # Basic report filtering by statDate if provided
                if statDate and "report_date" in df.columns:
                    df = df[df["report_date"].str.contains(statDate)]
                
                # JQ fundamentals usually return a single row per stock for latest data
                row = df.tail(1).copy()
                row["code"] = sym
                results.append(row)
        except Exception as e:
            logger.debug(f"get_fundamentals failed for '{sym}': {e}")

    if not results:
        return pd.DataFrame()
        
    res = pd.concat(results, ignore_index=True)
    
    # Filter fields if specified in query
    if fields:
        res = res[[f for f in fields if f in res.columns]]
        
    return res


def get_fundamentals_continuously(
    query_obj,
    start_date: str,
    end_date: Optional[str] = None,
    frequency: int = 1,
    count: Optional[int] = None,
    fields: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Continuously fetch fundamental data. JQ-compatible."""
    security = getattr(query_obj, "code", None)
    if not security:
        return pd.DataFrame()

    start_date = _normalize_date(start_date)
    end_date = _normalize_date(end_date)
    
    if end_date:
        dates = pd.date_range(start=start_date, end=end_date, freq=f"{frequency}D")
    elif count:
        dates = pd.date_range(start=start_date, periods=count, freq=f"{frequency}D")
    else:
        dates = pd.date_range(start=start_date, end=datetime.now(), freq=f"{frequency}D")

    all_frames = []
    for d in dates:
        date_str = d.strftime("%Y-%m-%d")
        df = get_fundamentals(query_obj, date=date_str)
        if not df.empty:
            df["day"] = date_str
            all_frames.append(df)
            
    if not all_frames:
        return pd.DataFrame()
        
    res = pd.concat(all_frames, ignore_index=True)
    if fields:
        res = res[[f for f in fields if f in res.columns]]
    return res


def bank_indicator(security_list: Union[str, List[str]], date: Optional[str] = None,
                   fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Get bank industry specific indicators. JQ-compatible."""
    if isinstance(security_list, str):
        security_list = [security_list]
    date = _normalize_date(date)
    results = []
    for sym in security_list:
        try:
            df = _get_fm_ak(symbol=sym, source="eastmoney_direct")
            if not df.empty:
                df["code"] = sym
                if date:
                    df = df[df.get("date", pd.Series()) <= date] if "date" in df.columns else df
                results.append(df.tail(1))
        except Exception as e:
            logger.warning(f"bank_indicator failed for '{sym}': {e}")
    if not results:
        return pd.DataFrame()
    res = pd.concat(results, ignore_index=True)
    return res[[c for c in fields if c in res.columns]] if fields else res


def security_indicator(security_list: Union[str, List[str]], date: Optional[str] = None,
                       fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Get securities industry specific indicators. JQ-compatible."""
    return bank_indicator(security_list, date, fields)


def insurance_indicator(security_list: Union[str, List[str]], date: Optional[str] = None,
                        fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Get insurance industry specific indicators. JQ-compatible."""
    return bank_indicator(security_list, date, fields)


# _jq aliases
bank_indicator_jq = bank_indicator
security_indicator_jq = security_indicator
insurance_indicator_jq = insurance_indicator

__all__ = [
    "get_locked_shares", "get_fund_info", "get_fundamentals",
    "get_fundamentals_continuously",
    "bank_indicator", "security_indicator", "insurance_indicator",
    "bank_indicator_jq", "security_indicator_jq", "insurance_indicator_jq",
]
