"""
Factory for creating limit up/down data providers.
"""

from ..factory_base import BaseFactory
from .base import LimitUpDownProvider
from .eastmoney import EastmoneyLimitUpDownProvider
from .sina import SinaLimitUpDownProvider


class LimitUpDownFactory(BaseFactory[LimitUpDownProvider]):
    """Factory class for creating limit up/down data providers."""

    _providers: dict[str, type[LimitUpDownProvider]] = {
        "eastmoney": EastmoneyLimitUpDownProvider,
        "sina": SinaLimitUpDownProvider,
    }
