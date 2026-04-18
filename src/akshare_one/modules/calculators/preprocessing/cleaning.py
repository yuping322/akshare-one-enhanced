"""
Data cleaning: NaN/Inf handling, type inference.
"""

import numpy as np
import pandas as pd


def handle_nan_inf(df: pd.DataFrame, fill_method: str = "nan", fill_value: float = 0.0) -> pd.DataFrame:
    """Handle NaN and Inf values in DataFrame."""
    df = df.copy()
    df = df.replace([np.inf, -np.inf], np.nan)
    if fill_method == "zero":
        df = df.fillna(fill_value)
    elif fill_method == "ffill":
        df = df.ffill()
    elif fill_method == "bfill":
        df = df.bfill()
    elif fill_method == "mean":
        df = df.fillna(df.mean())
    return df


def infer_numeric_types(df: pd.DataFrame) -> pd.DataFrame:
    """Infer and convert columns to numeric types."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_factor_data(
    df: pd.DataFrame, drop_na_cols: list[str] | None = None, fill_method: str = "nan"
) -> pd.DataFrame:
    """Clean factor data by handling missing values and type conversion."""
    df = infer_numeric_types(df)
    df = handle_nan_inf(df, fill_method=fill_method)
    if drop_na_cols:
        df = df.dropna(subset=drop_na_cols)
    return df
