"""
Risk management calculation module.
"""

from .volatility import compute_annual_volatility, compute_atr, detect_volatility_regime
from .drawdown import compute_drawdown_series, compute_max_drawdown, compute_recovery_time
from .position_sizing import (
    kelly_fraction,
    risk_parity_weights,
    atr_position_size,
    get_position_size_fixed_risk,
    compute_atr_stop_loss,
    check_max_drawdown_limit,
)

__all__ = [
    "compute_annual_volatility",
    "compute_atr",
    "detect_volatility_regime",
    "compute_drawdown_series",
    "compute_max_drawdown",
    "compute_recovery_time",
    "kelly_fraction",
    "risk_parity_weights",
    "atr_position_size",
    "get_position_size_fixed_risk",
    "compute_atr_stop_loss",
    "check_max_drawdown_limit",
]
