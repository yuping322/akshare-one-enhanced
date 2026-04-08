"""
src/akshare_one/modules/alpha/
Unified Quantitative Engine for AkShare-One Enhanced.
"""

from .backtest import (
    compute_drawdown,
    get_performance_metrics,
    print_performance_summary,
)
from .base import (
    FactorRegistry,
    align_to_trade_days,
    global_factor_registry,
    normalize_factor_name,
    safe_divide,
)
from .factors import (
    compute_market_cap,
    compute_momentum,
    compute_pb_ratio,
    get_factor_values,
)
from .preprocess import (
    neutralize,
    standardlize,
    winsorize_med,
)
from .risk import (
    check_max_drawdown_limit,
    compute_atr_stop_loss,
    get_position_size_fixed_risk,
)
from .signals import (
    compute_breakthrough,
    compute_ma_cross,
    compute_rsrs,
    get_signal_for_sec,
)

__all__ = [
    # Base
    "normalize_factor_name", "global_factor_registry", "align_to_trade_days",
    "safe_divide", "FactorRegistry",
    # Preprocess
    "winsorize_med", "standardlize", "neutralize",
    # Factors
    "compute_market_cap", "compute_pb_ratio", "compute_momentum", "get_factor_values",
    # Signals
    "compute_rsrs", "compute_ma_cross", "compute_breakthrough", "get_signal_for_sec",
    # Evaluation
    "get_performance_metrics", "print_performance_summary", "compute_drawdown",
    # Risk
    "compute_atr_stop_loss", "get_position_size_fixed_risk", "check_max_drawdown_limit",
]
