"""
src/akshare_one/jq_compat/billboard_futures.py
JQ-compatible futures and billboard APIs.
"""

import logging
import pandas as pd
import akshare as ak
from datetime import datetime
from typing import Optional, List, Union

from ..constants import SYMBOL_ZFILL_WIDTH

logger = logging.getLogger(__name__)


def _jq_symbol(code: str) -> str:
    code = str(code).zfill(SYMBOL_ZFILL_WIDTH)
    return f"{code}.XSHG" if code.startswith("6") else f"{code}.XSHE"


def _normalize_date(date_val) -> Optional[str]:
    if date_val is None:
        return None
    if isinstance(date_val, str):
        return date_val
    try:
        return pd.to_datetime(date_val).strftime("%Y-%m-%d")
    except Exception:
        return str(date_val)


def get_billboard_list(stock=None, start_date=None, end_date=None, count=None):
    """Get dragon-tiger list. JQ-compatible."""
    try:
        sd = (start_date or "2023-01-01").replace("-", "")
        ed = (end_date or datetime.now().strftime("%Y%m%d")).replace("-", "")
        df = ak.stock_lhb_detail_em(start_date=sd, end_date=ed)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(columns={"代码": "code", "名称": "name", "上榜日期": "date", "龙虎榜净买": "net_value"})
        df["code"] = df["code"].apply(_jq_symbol)
        if stock:
            if isinstance(stock, str):
                stock = [stock]
            df = df[df["code"].isin(stock)]
        return df.reset_index(drop=True)
    except Exception as e:
        logger.warning(f"get_billboard_list failed: {e}")
        return pd.DataFrame()


def get_institutional_holdings(stock: str, date: Optional[str] = None) -> pd.DataFrame:
    """Get institutional holdings. JQ-compatible."""
    try:
        clean_code = stock.split(".")[0]
        df = ak.stock_institute_hold(stock=clean_code)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(columns={"机构名称": "institution_name", "报告期": "report_date"})
        if date:
            date = _normalize_date(date)
            if "report_date" in df.columns:
                df = df[df["report_date"] <= date]
        return df
    except Exception as e:
        logger.warning(f"get_institutional_holdings failed for '{stock}': {e}")
        return pd.DataFrame()


def get_billboard_hot_stocks(start_date=None, end_date=None, top_n=20):
    """Get hot stocks from dragon-tiger list. JQ-compatible."""
    df = get_billboard_list(start_date=start_date, end_date=end_date)
    if df.empty:
        return df
    return df.groupby("code")["net_value"].sum().sort_values(ascending=False).head(top_n).reset_index()


def get_broker_statistics(start_date=None, end_date=None, top_n=20) -> pd.DataFrame:
    """Get broker statistics from dragon-tiger list. JQ-compatible."""
    try:
        sd = (start_date or "2023-01-01").replace("-", "")
        ed = (end_date or datetime.now().strftime("%Y%m%d")).replace("-", "")
        df = ak.stock_lhb_jgzz_em(start_date=sd, end_date=ed)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(
            columns={
                "机构名称": "broker_name",
                "买入总额": "buy_amount",
                "卖出总额": "sell_amount",
                "净买入": "net_buy",
            }
        )
        return df.head(top_n).reset_index(drop=True)
    except Exception as e:
        logger.warning(f"get_broker_statistics failed: {e}")
        return pd.DataFrame()


def get_settlement_price(contract_code: str, date: Optional[str] = None) -> float:
    """Get futures settlement price. JQ-compatible."""
    try:
        date = _normalize_date(date) or datetime.now().strftime("%Y-%m-%d")
        date_fmt = date.replace("-", "")
        df = ak.futures_zh_daily_sina(symbol=contract_code)
        if df is None or df.empty:
            return float("nan")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d")
            row = df[df["date"] <= date_fmt]
            if not row.empty:
                settle_col = next((c for c in ["settlement", "settle", "结算价"] if c in df.columns), None)
                if settle_col:
                    return float(row.iloc[-1][settle_col])
        return float("nan")
    except Exception as e:
        logger.warning(f"get_settlement_price failed for '{contract_code}': {e}")
        return float("nan")


def get_dominant_future(underlying_symbol: str, date: Optional[str] = None) -> str:
    """Get dominant futures contract. JQ-compatible."""
    try:
        date = _normalize_date(date)
        df = ak.futures_main_sina(symbol=underlying_symbol)
        if df is None or df.empty:
            return ""
        if date and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            row = df[df["date"] <= date]
            return str(row.iloc[-1]["contract"]) if not row.empty else str(df.iloc[0]["contract"])
        return str(df.iloc[0]["contract"])
    except Exception as e:
        logger.warning(f"get_dominant_future failed for '{underlying_symbol}': {e}")
        return ""


def get_future_contracts(
    underlying_symbol: str, exchange: Optional[str] = None, date: Optional[str] = None
) -> List[str]:
    """Get futures contract list. JQ-compatible."""
    try:
        df = ak.futures_display_main_sina()
        matches = df[df["symbol"].str.upper() == underlying_symbol.upper()]
        return matches["contract"].tolist() if not matches.empty else []
    except Exception as e:
        logger.warning(f"get_future_contracts failed for '{underlying_symbol}': {e}")
        return []


def get_futures_info(
    contract_code: Optional[str] = None, exchange: Optional[str] = None, fields: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get futures contract info. JQ-compatible."""
    try:
        df = ak.futures_comm_info(symbol="all")
        if contract_code:
            underlying = "".join([c for c in contract_code if not c.isdigit()])
            df = df[df["symbol"].str.upper() == underlying.upper()]
        if fields:
            df = df[[c for c in fields if c in df.columns]]
        return df
    except Exception as e:
        logger.warning(f"get_futures_info failed: {e}")
        return pd.DataFrame()


get_dominant_future_jq = get_dominant_future
get_futures_info_jq = get_futures_info
get_future_contracts_jq = get_future_contracts
get_dominant_contracts = get_dominant_future

__all__ = [
    "get_billboard_list",
    "get_institutional_holdings",
    "get_dominant_future",
    "get_billboard_hot_stocks",
    "get_broker_statistics",
    "get_futures_info",
    "get_future_contracts",
    "get_settlement_price",
    "get_dominant_future_jq",
    "get_futures_info_jq",
    "get_future_contracts_jq",
    "get_dominant_contracts",
]
