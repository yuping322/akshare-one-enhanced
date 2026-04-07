"""
Technical indicator calculation module.
"""

from typing import Type

from .base import BaseIndicatorCalculator
from .simple import SimpleIndicatorCalculator

try:
    import talib  # type: ignore[import-not-found]
    from .talib import TalibIndicatorCalculator
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


class IndicatorFactory:
    """Factory for creating indicator calculators"""

    _calculators: dict[str, Type[BaseIndicatorCalculator]] = {
        "simple": SimpleIndicatorCalculator,
    }

    if TALIB_AVAILABLE:
        _calculators["talib"] = TalibIndicatorCalculator

    @classmethod
    def get_calculator(cls, calculator_type: str = "talib") -> BaseIndicatorCalculator:
        """Get an indicator calculator instance

        Args:
            calculator_type: ('talib', 'simple')
        """
        if calculator_type == "talib" and not TALIB_AVAILABLE:
            calculator_type = "simple"

        calculator_cls = cls._calculators.get(calculator_type)
        if not calculator_cls:
            raise ValueError(f"Unsupported calculator type: {calculator_type}")

        return calculator_cls()


__all__ = [
    "IndicatorFactory",
    "BaseIndicatorCalculator",
    "SimpleIndicatorCalculator",
    "TALIB_AVAILABLE",
]
