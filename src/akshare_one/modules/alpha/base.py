"""
src/akshare_one/modules/alpha/base.py
Alpha computation infrastructure.
"""

import os
import pickle
import warnings
from typing import Callable, Dict, List, Optional, Union
import pandas as pd
import numpy as np
from ..date import get_trade_dates_between, is_trade_date

# Alias map: JQ style -> Internal normalized name
FACTOR_ALIAS_MAP: Dict[str, str] = {
    "PE_ratio": "pe_ratio", "pe_ratio": "pe_ratio",
    "PB_ratio": "pb_ratio", "pb_ratio": "pb_ratio",
    "PS_ratio": "ps_ratio", "ps_ratio": "ps_ratio",
    "market_cap": "market_cap", "circulating_market_cap": "circulating_market_cap",
    "ROE": "roe", "ROA_TTM": "roa_ttm",
    "BIAS5": "bias_5", "ROC20": "roc_20", "VOL20": "vol_20",
    "beta": "beta", "momentum": "momentum",
}

def normalize_factor_name(name: str) -> str:
    """Normalize factor name to internal standard."""
    if name in FACTOR_ALIAS_MAP: return FACTOR_ALIAS_MAP[name]
    return name.lower()

def get_trade_days(start_date: str, end_date: str) -> List[str]:
    """Get trade days between two dates."""
    try:
        return get_trade_dates_between(start_date, end_date)
    except Exception:
        dates = pd.date_range(start=start_date, end=end_date, freq="B")
        return [d.strftime("%Y-%m-%d") for d in dates]

def align_to_trade_days(df: pd.DataFrame, date_col: str = "date", start_date: Optional[str] = None, end_date: Optional[str] = None, fill_method: str = "ffill") -> pd.DataFrame:
    """Align DataFrame to trade days index."""
    if df is None or df.empty: return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
    s_date = start_date or df[date_col].min()
    e_date = end_date or df[date_col].max()
    trade_days = get_trade_days(s_date, e_date)
    df = df.set_index(date_col).reindex(trade_days)
    if fill_method == "ffill": df = df.ffill()
    elif fill_method == "bfill": df = df.bfill()
    return df.reset_index().rename(columns={"index": date_col})

class FactorRegistry:
    """Registry for factor computation functions."""
    def __init__(self):
        self._factors: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict] = {}

    def register(self, name: str, func: Callable, window: Optional[int] = None, dependencies: Optional[List[str]] = None, description: str = ""):
        norm_name = normalize_factor_name(name)
        self._factors[norm_name] = func
        self._metadata[norm_name] = {"window": window, "dependencies": dependencies or [], "description": description}

    def get(self, name: str) -> Optional[Callable]:
        return self._factors.get(normalize_factor_name(name))

    def list_factors(self) -> List[str]:
        return list(self._factors.keys())

global_factor_registry = FactorRegistry()

def safe_divide(a: Union[float, np.ndarray, pd.Series], b: Union[float, np.ndarray, pd.Series]):
    """Safe division returning NaN for zero denominator."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((b == 0) | np.isnan(b), np.nan, np.divide(a, b))

__all__ = ["normalize_factor_name", "global_factor_registry", "align_to_trade_days", "safe_divide", "FactorRegistry"]
