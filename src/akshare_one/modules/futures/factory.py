"""
Factory for creating futures data providers.
"""

from typing import Any

from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .eastmoney import EastmoneyFuturesHistoricalProvider, EastmoneyFuturesRealtimeProvider
from .sina import SinaFuturesHistorical, SinaFuturesRealtime


class FuturesDataFactory:
    """Factory class for creating futures data providers."""

    _historical_providers: dict[str, type[HistoricalFuturesDataProvider]] = {
        "sina": SinaFuturesHistorical,
        "eastmoney": EastmoneyFuturesHistoricalProvider,
    }

    _realtime_providers: dict[str, type[RealtimeFuturesDataProvider]] = {
        "sina": SinaFuturesRealtime,
        "eastmoney": EastmoneyFuturesRealtimeProvider,
    }

    @classmethod
    def get_historical_provider(cls, source: str, **kwargs: Any) -> HistoricalFuturesDataProvider:
        """Get a historical futures data provider by name."""
        if source not in cls._historical_providers:
            available = ", ".join(cls._historical_providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._historical_providers[source](**kwargs)

    @classmethod
    def get_realtime_provider(cls, source: str, **kwargs: Any) -> RealtimeFuturesDataProvider:
        """Get a realtime futures data provider by name."""
        if source not in cls._realtime_providers:
            available = ", ".join(cls._realtime_providers.keys())
            raise ValueError(f"Unsupported source: {source}. Available: {available}")
        return cls._realtime_providers[source](**kwargs)

    @classmethod
    def register_historical_provider(
        cls, name: str, provider_class: type[HistoricalFuturesDataProvider]
    ) -> None:
        """Register a new historical futures data provider."""
        cls._historical_providers[name] = provider_class

    @classmethod
    def register_realtime_provider(
        cls, name: str, provider_class: type[RealtimeFuturesDataProvider]
    ) -> None:
        """Register a new realtime futures data provider."""
        cls._realtime_providers[name] = provider_class

    @classmethod
    def list_historical_sources(cls) -> list[str]:
        """List all available historical data sources."""
        return list(cls._historical_providers.keys())

    @classmethod
    def list_realtime_sources(cls) -> list[str]:
        """List all available realtime data sources."""
        return list(cls._realtime_providers.keys())
