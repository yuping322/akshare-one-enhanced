"""
src/akshare_one/jq_compat/money_flow.py
JQ-compatible money flow APIs.
"""

import logging
import pandas as pd
import akshare as ak
from datetime import datetime
from typing import Union, List, Optional

logger = logging.getLogger(__name__)


def _normalize_code(stock: str) -> str:
    if "." in stock:
        return stock.split(".")[0].zfill(6)
    if stock.startswith("sh") or stock.startswith("sz"):
        return stock[2:].zfill(6)
    return stock.zfill(6)


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "代码": "code", "名称": "name", "日期": "date", "最新价": "close",
        "涨跌幅": "pct_change", "主力净流入-净额": "main_net_inflow",
        "主力净流入-净占比": "main_net_inflow_pct", "超大单净流入-净额": "xlarge_net_inflow",
        "大单净流入-净额": "large_net_inflow", "中单净流入-净额": "medium_net_inflow",
        "小单净流入-净额": "small_net_inflow", "主力净流入": "main_net_inflow",
        "超大单净流入": "xlarge_net_inflow", "大单净流入": "large_net_inflow",
    }
    return df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})


def get_money_flow(
    security: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    count: Optional[int] = None,
) -> pd.DataFrame:
    """Get individual stock money flow data. JQ-compatible."""
    try:
        if security is not None:
            if isinstance(security, str):
                code = _normalize_code(security)
                market = "sh" if code.startswith("6") else "sz"
                df = ak.stock_individual_fund_flow(stock=code, market=market)
                if df is not None and not df.empty:
                    df = _standardize_columns(df)
                    df["code"] = security
                    if start_date and "date" in df.columns:
                        df = df[df["date"] >= start_date]
                    if end_date and "date" in df.columns:
                        df = df[df["date"] <= end_date]
                    return df.tail(count) if count else df
                return pd.DataFrame()
            else:
                results = [get_money_flow(s, start_date, end_date, count) for s in security]
                return pd.concat([r for r in results if not r.empty], ignore_index=True) if results else pd.DataFrame()
        else:
            df = ak.stock_individual_fund_flow_rank(indicator="今日")
            return _standardize_columns(df) if df is not None else pd.DataFrame()
    except Exception as e:
        logger.warning(f"get_money_flow failed: {e}")
        return pd.DataFrame()


def get_sector_money_flow(sector: Optional[str] = None, date: Optional[str] = None) -> pd.DataFrame:
    """Get sector money flow. JQ-compatible."""
    try:
        df_ind = ak.stock_board_industry_fund_flow_rank(indicator="今日")
        df_con = ak.stock_board_concept_fund_flow_rank(indicator="今日")
        frames = [f for f in [df_ind, df_con] if f is not None and not f.empty]
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if df.empty:
            return df
        df = _standardize_columns(df)
        if sector:
            mask = df.get("name", pd.Series(dtype=str)).str.contains(sector, na=False)
            df = df[mask]
        return df
    except Exception as e:
        logger.warning(f"get_sector_money_flow failed: {e}")
        return pd.DataFrame()


def get_money_flow_rank(top_n: int = 50, direction: str = "inflow") -> pd.DataFrame:
    """Get money flow rank for today. JQ-compatible."""
    df = get_money_flow()
    if df.empty:
        return df
    asc = direction != "inflow"
    col = "main_net_inflow"
    if col not in df.columns:
        return df.head(top_n)
    return df.sort_values(col, ascending=asc).head(top_n)


__all__ = ["get_money_flow", "get_sector_money_flow", "get_money_flow_rank"]
