"""
Trading signal calculation module.
"""

from .rsrs import compute_rsrs
from .crossover import compute_ma_cross
from .breakout import compute_breakthrough, get_signal_for_sec

__all__ = ["compute_rsrs", "compute_ma_cross", "compute_breakthrough", "get_signal_for_sec"]
