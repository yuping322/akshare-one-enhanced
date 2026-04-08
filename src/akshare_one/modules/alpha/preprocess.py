"""
src/akshare_one/modules/alpha/preprocess.py
Factor preprocessing: Winsorization, Standardization, Neutralization.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional
import warnings

def _winsorize_med_series(series: pd.Series, scale: float, inclusive: bool, inf2nan: bool) -> pd.Series:
    s = series.copy()
    if inf2nan: s = s.replace([np.inf, -np.inf], np.nan)
    valid = s.dropna()
    if len(valid) == 0: return s
    med = valid.median()
    mad = (valid - med).abs().median()
    if mad == 0:
        mad = valid.std() / 1.4826
        if mad == 0: return s
    upper = med + scale * mad * 1.4826
    lower = med - scale * mad * 1.4826
    if inclusive: s = s.clip(lower=lower, upper=upper)
    else: s[(s < lower) | (s > upper)] = np.nan
    return s

def winsorize_med(factor_data: Union[pd.DataFrame, pd.Series], scale: float = 3.0, inclusive: bool = True, inf2nan: bool = True, axis: int = 0) -> Union[pd.DataFrame, pd.Series]:
    """Winsorize factor data using MAD method."""
    if isinstance(factor_data, pd.Series): return _winsorize_med_series(factor_data, scale, inclusive, inf2nan)
    df = factor_data.copy()
    if inf2nan: df = df.replace([np.inf, -np.inf], np.nan)
    if axis == 0:
        for col in df.columns: df[col] = _winsorize_med_series(df[col], scale, inclusive, inf2nan=False)
    else:
        for idx in df.index: df.loc[idx] = _winsorize_med_series(df.loc[idx], scale, inclusive, inf2nan=False)
    return df

def standardlize(factor_data: Union[pd.DataFrame, pd.Series], inf2nan: bool = True, axis: int = 0) -> Union[pd.DataFrame, pd.Series]:
    """Standardize factor data to Z-Score (Mean=0, Std=1)."""
    df = factor_data.copy()
    if inf2nan: df = df.replace([np.inf, -np.inf], np.nan)
    if isinstance(df, pd.Series):
        mean, std = df.mean(), df.std()
        return (df - mean) / std if std != 0 else df
    if axis == 0:
        return (df - df.mean()) / df.std().replace(0, np.nan)
    else:
        return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1).replace(0, np.nan), axis=0)

def neutralize(factor_data: Union[pd.DataFrame, pd.Series], how: Optional[List[str]] = None, market_cap: Optional[pd.Series] = None, industry_data: Optional[pd.DataFrame] = None) -> Union[pd.DataFrame, pd.Series]:
    """Neutralize factor data against Market Cap and/or Industry."""
    if how is None: how = ["market_cap"]
    is_series = isinstance(factor_data, pd.Series)
    df = factor_data.to_frame().T if is_series else factor_data.copy()
    securities = df.columns.tolist()
    X = np.ones((len(securities), 1))  # Intercept
    
    if "market_cap" in how and market_cap is not None:
        mc = np.log(market_cap.reindex(securities).fillna(market_cap.mean()))
        X = np.column_stack([X, mc.values])
    
    if "industry" in how and industry_data is not None:
        ind = industry_data.reindex(securities).fillna(0)
        X = np.column_stack([X, ind.values])
        
    for idx in df.index:
        y = df.loc[idx].values
        mask = ~np.isnan(y)
        if mask.sum() > X.shape[1]:
            beta = np.linalg.lstsq(X[mask], y[mask], rcond=None)[0]
            df.loc[idx, mask] = y[mask] - X[mask] @ beta
            
    return df.iloc[0] if is_series else df

__all__ = ["winsorize_med", "standardlize", "neutralize"]
