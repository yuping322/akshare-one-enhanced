"""
src/akshare_one/modules/alpha/backtest.py
Backtest performance metrics and evaluation.
"""


import numpy as np
import pandas as pd


def compute_drawdown(returns: pd.Series) -> pd.DataFrame:
    """Calculate drawdown series."""
    cum_ret = (1 + returns).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max
    return pd.DataFrame({"cum_ret": cum_ret, "max_ret": running_max, "drawdown": drawdown})

def get_performance_metrics(returns: pd.Series, risk_free_rate: float = 0.02) -> dict[str, float]:
    """Calculate key performance metrics (Sharpe, Sortino, MDD)."""
    if len(returns) < 2: return {}
    
    ann_ret = (1 + returns.mean()) ** 252 - 1
    ann_std = returns.std() * np.sqrt(252)
    sharpe = (ann_ret - risk_free_rate) / ann_std if ann_std != 0 else 0
    
    neg_returns = returns[returns < 0]
    downside_std = neg_returns.std() * np.sqrt(252)
    sortino = (ann_ret - risk_free_rate) / downside_std if downside_std != 0 else 0
    
    dd = compute_drawdown(returns)
    mdd = dd["drawdown"].min()
    
    return {
        "annual_return": ann_ret,
        "annual_volatility": ann_std,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": mdd,
        "win_rate": (returns > 0).mean()
    }

def print_performance_summary(metrics: dict[str, float]):
    """Print a user-friendly performance summary."""
    print("--- Strategy Performance Summary ---")
    for k, v in metrics.items():
        print(f"{k.replace('_', ' ').title():<20}: {v:.2%}" if isinstance(v, float) else f"{k}: {v}")

__all__ = ["get_performance_metrics", "print_performance_summary", "compute_drawdown"]
