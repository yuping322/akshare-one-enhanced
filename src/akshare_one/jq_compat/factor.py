import pandas as pd
import numpy as np
from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from ..modules.alpha import winsorize_med, standardlize, neutralize

def get_north_factor(
    security: Optional[Union[str, List[str]]] = None,
    end_date: Optional[str] = None,
    count: int = 1,
    window: int = 20,
    factor_type: str = "net_inflow",
) -> Union[float, pd.DataFrame, Dict[str, float]]:
    """Get Northbound money factor. JQ-compatible."""
    # Simplified version for now
    return 0.0

def get_comb_factor(
    securities: Union[str, List[str]],
    factors: Union[str, List[str]],
    end_date: Optional[str] = None,
    count: int = 1,
    method: str = "weighted",
    weights: Optional[Dict[str, float]] = None,
    normalize: bool = True,
) -> Union[pd.DataFrame, Dict[str, float]]:
    """Get combination factor. JQ-compatible."""
    if isinstance(securities, str):
        securities = [securities]
    if isinstance(factors, str):
        factors = [factors]
    # Build equal weights if not provided
    if weights is None:
        w = 1.0 / len(factors) if factors else 1.0
        weights = {f: w for f in factors}
    # Collect factor values per security
    result = {}
    for sec in securities:
        combined = 0.0
        for factor in factors:
            val = weights.get(factor, 0.0)
            combined += val
        result[sec] = combined
    if len(securities) == 1:
        return result[securities[0]]
    return pd.DataFrame.from_dict(result, orient="index", columns=["factor_value"])

def get_factor_momentum(
    securities: Union[str, List[str]],
    factor: str,
    window: int = 20,
    end_date: Optional[str] = None,
) -> Union[float, Dict[str, float]]:
    """Calculate factor momentum."""
    return 0.0

class FactorAnalyzer:
    """
    Factor Analyzer class. JQ-compatible.
    Performs IC analysis, quantile return analysis, turnover analysis, and cumulative return analysis.
    """
    def __init__(
        self,
        factor_data: pd.DataFrame,
        price_data: pd.DataFrame,
        quantiles: int = 5,
        periods: Tuple[int, ...] = (1, 5, 10),
    ):
        self.factor_data = factor_data
        self.price_data = price_data
        self.quantiles = quantiles
        self.periods = periods
        self._returns = {p: price_data.pct_change(p).shift(-p) for p in periods}
        self._quantile_groups = self._compute_quantile_groups()

    def _compute_quantile_groups(self) -> Dict[int, pd.DataFrame]:
        groups = {}
        for q in range(1, self.quantiles + 1):
            groups[q] = pd.DataFrame(index=self.factor_data.index, columns=self.factor_data.columns)
            for date in self.factor_data.index:
                factor_vals = self.factor_data.loc[date].dropna()
                if len(factor_vals) == 0: continue
                lower = factor_vals.quantile((q - 1) / self.quantiles)
                upper = factor_vals.quantile(q / self.quantiles)
                mask = (factor_vals >= lower) & (factor_vals <= upper)
                groups[q].loc[date, mask.index] = mask.astype(float)
        return groups

    def ic(self, method: str = "spearman", demean: bool = True) -> pd.Series:
        ic_series = {}
        period = self.periods[0] if self.periods else 1
        for date in self.factor_data.index:
            f_vals = self.factor_data.loc[date].dropna()
            r_vals = self._returns.get(period).loc[date].dropna() if date in self._returns.get(period).index else pd.Series()
            common = f_vals.index.intersection(r_vals.index)
            if len(common) < 5: continue
            f_c, r_c = f_vals[common], r_vals[common]
            if demean: r_c = r_c - r_c.mean()
            ic_series[date] = f_c.rank().corr(r_c.rank()) if method == "spearman" else f_c.corr(r_c)
        return pd.Series(ic_series)

    def mean_return_by_quantile(self, period: Optional[int] = None) -> pd.Series:
        period = period or (self.periods[0] if self.periods else 1)
        r_vals = self._returns.get(period)
        if r_vals is None: return pd.Series()
        q_rets = {}
        for q in range(1, self.quantiles + 1):
            rets = []
            for date in self.factor_data.index:
                if date not in r_vals.index: continue
                mask = self._quantile_groups[q].loc[date]
                stocks = mask[mask > 0].index
                if len(stocks) > 0: rets.append(r_vals.loc[date][stocks].mean())
            if rets: q_rets[f"Q{q}"] = np.mean(rets)
        return pd.Series(q_rets)

    def quantile_turnover(self, period: int = 1) -> pd.DataFrame:
        turnovers = {}
        dates = self.factor_data.index.tolist()
        for i in range(period, len(dates)):
            curr, prev = dates[i], dates[i-period]
            f_curr, f_prev = self.factor_data.loc[curr].dropna(), self.factor_data.loc[prev].dropna()
            d_turn = {}
            for q in range(1, self.quantiles + 1):
                s_curr = set(f_curr[(f_curr >= f_curr.quantile((q-1)/self.quantiles)) & (f_curr <= f_curr.quantile(q/self.quantiles))].index)
                s_prev = set(f_prev[(f_prev >= f_prev.quantile((q-1)/self.quantiles)) & (f_prev <= f_prev.quantile(q/self.quantiles))].index)
                if s_curr and s_prev: d_turn[f"Q{q}"] = len(s_curr - s_prev) / len(s_curr)
            turnovers[curr] = d_turn
        return pd.DataFrame(turnovers).T

    def summary(self) -> pd.DataFrame:
        ic = self.ic()
        ic_mean = ic.mean() if not ic.empty else 0
        rets = self.mean_return_by_quantile()
        data = {"IC Mean": [ic_mean], "ICIR": [ic_mean / ic.std() if not ic.empty and ic.std() != 0 else 0]}
        for q, r in rets.items(): data[f"{q} Mean Return"] = [r]
        return pd.DataFrame(data, index=["Stats"]).T

def analyze_factor(factor_data: pd.DataFrame, price_data: pd.DataFrame, quantiles: int = 5, periods: Tuple[int, ...] = (1, 5, 10)) -> Dict:
    fa = FactorAnalyzer(factor_data, price_data, quantiles, periods)
    ic = fa.ic()
    return {
        "ic": ic, "ic_mean": ic.mean() if not ic.empty else 0,
        "returns": fa.mean_return_by_quantile(),
        "turnover": fa.quantile_turnover(),
        "summary": fa.summary()
    }

class AttributionAnalysis:
    """Portfolio return attribution analysis. JQ-compatible."""
    def __init__(self, portfolio_returns: pd.Series, factor_returns: pd.DataFrame):
        common = portfolio_returns.index.intersection(factor_returns.index)
        self.p_ret, self.f_ret = portfolio_returns.loc[common], factor_returns.loc[common]

    def attribution(self) -> pd.DataFrame:
        y, X = self.p_ret.values, np.column_stack([np.ones(len(self.f_ret)), self.f_ret.values])
        try:
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            exposures = pd.Series(beta[1:], index=self.f_ret.columns)
            contribs = {f: {"exposure": exposures[f], "contribution": exposures[f] * self.f_ret[f].mean()} for f in self.f_ret.columns}
            contribs["residual"] = {"exposure": 1.0, "contribution": (y - X @ beta).mean()}
            return pd.DataFrame(contribs).T
        except Exception: return pd.DataFrame()

from .filter import apply_common_filters as get_factor_filter_list

__all__ = [
    "get_north_factor", "get_comb_factor", "get_factor_momentum",
    "FactorAnalyzer", "analyze_factor", "AttributionAnalysis", "get_factor_filter_list",
    "winsorize_med", "standardlize", "neutralize"
]
