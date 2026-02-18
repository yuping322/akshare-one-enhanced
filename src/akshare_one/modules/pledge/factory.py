"""
Factory for creating equity pledge data providers.
"""

from ..factory_base import BaseFactory
from .base import EquityPledgeProvider
from .eastmoney import EastmoneyEquityPledgeProvider
from .sina import SinaEquityPledgeProvider


class EquityPledgeFactory(BaseFactory[EquityPledgeProvider]):
    """Factory class for creating equity pledge data providers."""

    _providers: dict[str, type[EquityPledgeProvider]] = {
        "eastmoney": EastmoneyEquityPledgeProvider,
        "sina": SinaEquityPledgeProvider,
    }
