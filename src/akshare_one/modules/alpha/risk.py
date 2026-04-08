"""
src/akshare_one/modules/alpha/risk.py
Risk management, stop-loss, and position sizing.
"""

import pandas as pd


def compute_atr_stop_loss(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14, multiplier: float = 2.0) -> pd.Series:
    """Calculate ATR-based trailing stop-loss."""
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window).mean()
    return close - (atr * multiplier)

def get_position_size_fixed_risk(portfolio_value: float, risk_per_trade: float, entry_price: float, stop_loss_price: float) -> int:
    """Calculate position size based on a fixed risk amount (Total Value * Risk%)."""
    risk_amount = portfolio_value * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)
    if risk_per_share == 0: return 0
    shares = risk_amount / risk_per_share
    return int(shares // 100) * 100  # Round to lot size

def check_max_drawdown_limit(current_drawdown: float, limit: float = -0.1) -> bool:
    """Check if max drawdown limit is breached (-10% default)."""
    return current_drawdown < limit

__all__ = ["compute_atr_stop_loss", "get_position_size_fixed_risk", "check_max_drawdown_limit"]
