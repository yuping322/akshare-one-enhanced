"""
Alpha computation module.

DEPRECATED: Use modules.calculators (factors, signals, risk, backtest, preprocessing) instead.
"""

import warnings

warnings.warn(
    "Import from 'modules.alpha' is deprecated. Use 'modules.calculators' submodules instead.",
    DeprecationWarning,
    stacklevel=2,
)

from ..calculators.factors import (
    FactorRegistry,
    align_to_trade_days,
    global_factor_registry,
    normalize_factor_name,
    safe_divide,
    compute_market_cap,
    compute_pb_ratio,
    compute_momentum,
    get_factor_values,
)
from ..calculators.preprocessing.normalization import (
    neutralize,
    standardlize,
    winsorize_med,
)
from ..calculators.backtest.metrics import (
    compute_drawdown,
    get_performance_metrics,
    print_performance_summary,
)
from ..calculators.risk.position_sizing import (
    check_max_drawdown_limit,
    compute_atr_stop_loss,
    get_position_size_fixed_risk,
)
from ..calculators.signals import (
    compute_breakthrough,
    compute_ma_cross,
    compute_rsrs,
    get_signal_for_sec,
)

__all__ = [
    # Base
    "normalize_factor_name",
    "global_factor_registry",
    "align_to_trade_days",
    "safe_divide",
    "FactorRegistry",
    # Preprocess
    "winsorize_med",
    "standardlize",
    "neutralize",
    # Factors
    "compute_market_cap",
    "compute_pb_ratio",
    "compute_momentum",
    "get_factor_values",
    # Signals
    "compute_rsrs",
    "compute_ma_cross",
    "compute_breakthrough",
    "get_signal_for_sec",
    # Evaluation
    "get_performance_metrics",
    "print_performance_summary",
    "compute_drawdown",
    # Risk
    "compute_atr_stop_loss",
    "get_position_size_fixed_risk",
    "check_max_drawdown_limit",
]
