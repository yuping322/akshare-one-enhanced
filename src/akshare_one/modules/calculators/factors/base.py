"""
Alpha computation infrastructure.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd

from ...core.calendar import get_trade_dates_between

# Alias map: JQ style -> Internal normalized name
FACTOR_ALIAS_MAP: dict[str, str] = {
    "PE_ratio": "pe_ratio",
    "pe_ratio": "pe_ratio",
    "PB_ratio": "pb_ratio",
    "pb_ratio": "pb_ratio",
    "PS_ratio": "ps_ratio",
    "ps_ratio": "ps_ratio",
    "market_cap": "market_cap",
    "circulating_market_cap": "circulating_market_cap",
    "ROE": "roe",
    "ROA_TTM": "roa_ttm",
    "BIAS5": "bias_5",
    "ROC20": "roc_20",
    "VOL20": "vol_20",
    "beta": "beta",
    "momentum": "momentum",
}


def normalize_factor_name(name: str) -> str:
    """Normalize factor name to internal standard."""
    if name in FACTOR_ALIAS_MAP:
        return FACTOR_ALIAS_MAP[name]
    return name.lower()


def get_trade_days(start_date: str, end_date: str) -> list[str]:
    """Get trade days between two dates."""
    try:
        return get_trade_dates_between(start_date, end_date)
    except Exception:
        dates = pd.date_range(start=start_date, end=end_date, freq="B")
        return [d.strftime("%Y-%m-%d") for d in dates]


def align_to_trade_days(
    df: pd.DataFrame,
    date_col: str = "date",
    start_date: str | None = None,
    end_date: str | None = None,
    fill_method: str = "ffill",
) -> pd.DataFrame:
    """Align DataFrame to trade days index."""
    if df is None or df.empty:
        return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
    s_date = start_date or df[date_col].min()
    e_date = end_date or df[date_col].max()
    trade_days = get_trade_days(s_date, e_date)
    df = df.set_index(date_col).reindex(trade_days)
    if fill_method == "ffill":
        df = df.ffill()
    elif fill_method == "bfill":
        df = df.bfill()
    return df.reset_index().rename(columns={"index": date_col})


class FactorRegistry:
    """Registry for factor computation functions."""

    def __init__(self):
        self._factors: dict[str, Callable] = {}
        self._metadata: dict[str, dict] = {}

    def register(
        self,
        name: str,
        func: Callable,
        window: int | None = None,
        dependencies: list[str] | None = None,
        description: str = "",
    ):
        norm_name = normalize_factor_name(name)
        self._factors[norm_name] = func
        self._metadata[norm_name] = {"window": window, "dependencies": dependencies or [], "description": description}

    def get(self, name: str) -> Callable | None:
        return self._factors.get(normalize_factor_name(name))

    def list_factors(self) -> list[str]:
        return list(self._factors.keys())


global_factor_registry = FactorRegistry()


def safe_divide(a: float | np.ndarray | pd.Series, b: float | np.ndarray | pd.Series):
    """Safe division returning NaN for zero denominator."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((b == 0) | np.isnan(b), np.nan, np.divide(a, b))


def get_factor_values(securities: list[str], factor_names: list[str], end_date: str, count: int = 1) -> pd.DataFrame:
    """Calculate multiple factors for a list of securities."""
    from ...providers.equities.fundamentals.valuation import get_stock_valuation
    from ...providers.equities.quotes.historical import get_hist_data

    results = {}
    for sec in securities:
        sec_results = {}
        for name in factor_names:
            func = global_factor_registry.get(name)
            if func:
                try:
                    val = func(sec, end_date=end_date, count=count)
                    sec_results[name] = val
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).warning(f"Factor '{name}' calculation failed for '{sec}': {e}")
                    sec_results[name] = np.nan
        results[sec] = sec_results
    return pd.DataFrame(results).T


__all__ = [
    "normalize_factor_name",
    "global_factor_registry",
    "align_to_trade_days",
    "safe_divide",
    "FactorRegistry",
    "get_factor_values",
]
