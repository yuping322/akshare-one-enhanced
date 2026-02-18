"""
Factory for creating realtime data providers.
"""

from typing import Any

from ..factory_base import BaseFactory
from .base import RealtimeDataProvider
from .eastmoney import EastmoneyRealtime
from .eastmoney_direct import EastMoneyDirectRealtime
from .xueqiu import XueQiuRealtime


class RealtimeDataFactory(BaseFactory[RealtimeDataProvider]):
    """Factory class for creating realtime data providers."""

    _providers: dict[str, type[RealtimeDataProvider]] = {
        "eastmoney": EastmoneyRealtime,
        "xueqiu": XueQiuRealtime,
        "eastmoney_direct": EastMoneyDirectRealtime,
    }

    @classmethod
    def get_provider(cls, source: str, **kwargs: Any) -> RealtimeDataProvider:
        """
        Get a realtime data provider by name.

        Args:
            source: Name of the provider (e.g., 'eastmoney')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            RealtimeDataProvider: An instance of the requested provider
        """
        symbol = kwargs.get("symbol", "")
        if symbol is None:
            symbol = ""
        elif not isinstance(symbol, str):
            symbol = str(symbol)
        return super().get_provider(source, symbol=symbol)
