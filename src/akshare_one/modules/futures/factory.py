"""
Factory for creating futures data providers.
"""

from ..factory_base import BaseFactory
from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .eastmoney import EastmoneyFuturesHistoricalProvider, EastmoneyFuturesRealtimeProvider
from .sina import SinaFuturesHistorical, SinaFuturesRealtime


class FuturesHistoricalFactory(BaseFactory[HistoricalFuturesDataProvider]):
    """Factory for historical futures data providers."""
    _providers = {
        "sina": SinaFuturesHistorical,
        "eastmoney": EastmoneyFuturesHistoricalProvider,
    }


class FuturesRealtimeFactory(BaseFactory[RealtimeFuturesDataProvider]):
    """Factory for realtime futures data providers."""
    _providers = {
        "sina": SinaFuturesRealtime,
        "eastmoney": EastmoneyFuturesRealtimeProvider,
    }


class FuturesDataFactory:
    """Factory for creating futures data providers (for backward compatibility)."""

    @staticmethod
    def get_historical_provider(source: str, **kwargs) -> HistoricalFuturesDataProvider:
        """Get a historical futures data provider."""
        return FuturesHistoricalFactory.get_provider(source, **kwargs)

    @staticmethod
    def get_realtime_provider(source: str, **kwargs) -> RealtimeFuturesDataProvider:
        """Get a realtime futures data provider."""
        return FuturesRealtimeFactory.get_provider(source, **kwargs)
