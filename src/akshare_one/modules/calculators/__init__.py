"""
Calculator module for technical indicators, alpha factors, signals, risk, and backtest.
"""

from .technical.base import BaseIndicatorCalculator
from .technical.simple_indicators import SimpleIndicatorCalculator

try:
    from .technical.talib_indicators import TalibIndicatorCalculator

    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from .technical import IndicatorFactory

__all__ = [
    "IndicatorFactory",
    "BaseIndicatorCalculator",
    "SimpleIndicatorCalculator",
    "TALIB_AVAILABLE",
]
