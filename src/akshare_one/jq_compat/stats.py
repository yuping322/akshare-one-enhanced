"""
src/akshare_one/jq_compat/stats.py
JQ-compatible statistical analysis APIs.
"""

import logging
import pandas as pd
import numpy as np
from typing import Union, List, Dict, Optional
from scipy import stats
from .market import get_price as _get_price_jq, history as _history_jq

logger = logging.getLogger(__name__)


def get_ols(
    x: Union[pd.Series, np.ndarray, list],
    y: Union[pd.Series, np.ndarray, list],
    method: str = "linear",
) -> Dict[str, Union[float, pd.Series]]:
    """Linear regression (OLS). JQ-compatible."""
    if isinstance(x, pd.Series):
        x_values = x.values.copy()
        x_index = x.index
    else:
        x_values = np.array(x, dtype=float)
        x_index = pd.RangeIndex(len(x_values))

    y_values = y.values.copy() if isinstance(y, pd.Series) else np.array(y, dtype=float)

    mask = ~(np.isnan(x_values) | np.isnan(y_values))
    x_clean = x_values[mask]
    y_clean = y_values[mask]

    if len(x_clean) < 2:
        return {
            "beta": np.nan, "alpha": np.nan, "r_squared": np.nan,
            "residual": pd.Series([np.nan] * len(x_values), index=x_index),
            "p_value": np.nan, "std_err": np.nan,
        }

    x_transformed = np.log(x_clean) if method == "log" else x_clean
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_transformed, y_clean)

    if method == "log":
        predicted = intercept + slope * np.log(np.where(x_values > 0, x_values, np.nan))
    else:
        predicted = intercept + slope * x_values

    residual = pd.Series(y_values - predicted, index=x_index)
    return {
        "beta": float(slope), "alpha": float(intercept),
        "r_squared": float(r_value ** 2), "residual": residual,
        "p_value": float(p_value), "std_err": float(std_err),
    }


def get_zscore(
    data: Union[pd.Series, np.ndarray, list],
    window: Optional[int] = None,
) -> pd.Series:
    """Z-Score calculation. JQ-compatible."""
    s = data if isinstance(data, pd.Series) else pd.Series(data)
    if window is None:
        mean, std = s.mean(), s.std()
        return (s - mean) / std if std != 0 else pd.Series([np.nan] * len(s), index=s.index)
    rolling = s.rolling(window=window)
    mean = rolling.mean()
    std = rolling.std().replace(0, np.nan)
    return (s - mean) / std


def get_rank(
    data: Union[pd.Series, np.ndarray, list, Dict[str, float]],
    method: str = "asc",
) -> pd.Series:
    """Ranking function. JQ-compatible."""
    s = pd.Series(data)
    if method == "asc":
        return s.rank(ascending=True)
    if method == "desc":
        return s.rank(ascending=False)
    if method == "pct":
        return s.rank(ascending=True, pct=True)
    if method == "dense":
        return s.rank(method="dense", ascending=True)
    return s.rank()


def get_num(stock: str, field: str, date: Optional[str] = None) -> float:
    """Extract numeric value for a specific field. JQ-compatible."""
    field_lower = field.lower()
    try:
        if field_lower in ["open", "close", "high", "low", "volume", "money"]:
            df = _get_price_jq(stock, end_date=date, count=1, fields=[field_lower])
            return float(df[field_lower].iloc[-1]) if not df.empty else np.nan
        from .market import get_valuation as _get_val
        val_df = _get_val(stock, date=date, count=1)
        if not val_df.empty and field_lower in val_df.columns:
            return float(val_df[field_lower].iloc[-1])
    except (ValueError, TypeError, KeyError, IndexError) as e:
        logger.debug(f"get_num failed for '{stock}' field '{field}': {e}")
    return np.nan


def get_beta(
    security: Union[str, List[str]],
    benchmark: str = "000300.XSHG",
    window: int = 252,
    end_date: Optional[str] = None,
    start_date: Optional[str] = None,
    frequency: str = "1d",
) -> Union[float, Dict[str, float]]:
    """Beta coefficient calculation. JQ-compatible."""
    if isinstance(security, str):
        securities = [security]
        is_single = True
    else:
        securities = list(security)
        is_single = False

    try:
        bench_df = _history_jq(count=window + 1, unit=frequency, field="close",
                               security_list=[benchmark], end_date=end_date)
        if bench_df.empty:
            return 1.0 if is_single else {s: 1.0 for s in securities}
        bench_ret = bench_df[benchmark].pct_change().dropna()
    except Exception as e:
        logger.warning(f"get_beta benchmark fetch failed: {e}")
        return 1.0 if is_single else {s: 1.0 for s in securities}

    results = {}
    for sec in securities:
        try:
            stock_df = _history_jq(count=window + 1, unit=frequency, field="close",
                                   security_list=[sec], end_date=end_date)
            if stock_df.empty:
                results[sec] = 1.0
                continue
            stock_ret = stock_df[sec].pct_change().dropna()
            combined = pd.DataFrame({"s": stock_ret, "b": bench_ret}).dropna()
            if len(combined) < 20:
                results[sec] = 1.0
                continue
            cov = combined["s"].cov(combined["b"])
            var = combined["b"].var()
            results[sec] = float(cov / var) if var != 0 else 1.0
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"get_beta failed for '{sec}': {e}")
            results[sec] = 1.0

    return results[securities[0]] if is_single else results


def get_factor_filter_list(
    factor_data: pd.Series,
    quantile: float = 0.8,
    ascending: bool = False,
) -> List[str]:
    """Filter stocks by factor quantile. JQ-compatible."""
    if factor_data.empty:
        return []
    threshold = factor_data.quantile(quantile)
    if ascending:
        return factor_data[factor_data <= threshold].index.tolist()
    return factor_data[factor_data >= threshold].index.tolist()


__all__ = ["get_ols", "get_zscore", "get_rank", "get_num", "get_beta", "get_factor_filter_list"]
