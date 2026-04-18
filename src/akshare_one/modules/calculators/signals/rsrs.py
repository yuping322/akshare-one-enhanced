"""
RSRS (Resistance Support Relative Strength) timing signal.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm


def compute_rsrs(high: pd.Series, low: pd.Series, n: int = 18, m: int = 600) -> pd.Series:
    """Calculate RSRS (Resistance Support Relative Strength) signal."""
    beta_series = pd.Series(index=high.index, data=np.nan)
    for i in range(n, len(high)):
        h_win = high.iloc[i - n + 1 : i + 1]
        l_win = low.iloc[i - n + 1 : i + 1]
        x = sm.add_constant(l_win.values)
        y = h_win.values
        res = sm.OLS(y, x).fit()
        beta_series.iloc[i] = res.params[1]

    beta_mean = beta_series.rolling(window=m).mean()
    beta_std = beta_series.rolling(window=m).std()
    z_score = (beta_series - beta_mean) / beta_std
    return beta_series * z_score
