"""
src/akshare_one/modules/alpha/sentiment.py
Market sentiment, valuation, and macroeconomic indicators.
"""

import logging
import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def compute_crowding_ratio(date: Optional[str] = None, threshold: float = 0.05) -> Dict[str, float]:
    """Calculate market crowding (ratio of top turnover stocks)."""
    try:
        df = ak.stock_zh_a_spot_em()
        if df.empty: return {"ratio": 0, "desc": "no data"}
        df = df.rename(columns={"代码": "code", "成交额": "amount"})
        total = df["amount"].sum()
        df_sorted = df.sort_values("amount", ascending=False)
        top_n = int(len(df) * threshold)
        top_amount = df_sorted["amount"].head(top_n).sum()
        ratio = top_amount / total
        return {"ratio": ratio, "total": total}
    except Exception as e:
        logger.warning(f"compute_crowding_ratio failed: {e}")
        return {"ratio": 0, "desc": "failed", "error": str(e)}

def compute_fed_model(index_code: str = "000300", bond_rate: Optional[float] = None) -> Dict[str, float]:
    """Calculate FED model: 1/PE - Long-term Bond Yield."""
    try:
        df = ak.stock_a_pe_and_pb(symbol="沪深300")
        if df.empty: return {"fed": 0, "error": "no data"}
        latest_pe = df["pe"].iloc[-1]

        if bond_rate is None:
            bond_rate = 0.025

        fed_val = 1.0 / latest_pe - bond_rate
        return {"fed": fed_val, "pe": latest_pe, "bond_rate": bond_rate}
    except Exception as e:
        logger.warning(f"compute_fed_model failed: {e}")
        return {"fed": 0, "error": str(e)}

def compute_graham_index(index_code: str = "000300") -> Dict[str, float]:
    """Calculate Graham Index: (1/PE) / Bond Yield."""
    res = compute_fed_model(index_code=index_code)
    if res.get("pe", 0) == 0: return {"graham": 0}
    graham = (1.0 / res["pe"]) / res["bond_rate"]
    return {"graham": graham}

def compute_below_net_ratio() -> Dict[str, float]:
    """Calculate ratio of stocks trading below book value (PB < 1)."""
    try:
        df = ak.stock_zh_a_spot_em()
        if df.empty: return {"ratio": 0, "error": "no data"}
        df = df.rename(columns={"市净率": "pb"})
        below = len(df[df["pb"] < 1.0])
        return {"ratio": below / len(df), "count": below, "total": len(df)}
    except Exception as e:
        logger.warning(f"compute_below_net_ratio failed: {e}")
        return {"ratio": 0, "error": str(e)}

__all__ = ["compute_crowding_ratio", "compute_fed_model", "compute_graham_index", "compute_below_net_ratio"]
