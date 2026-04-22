"""Futures providers."""

from .base import FuturesDataFactory, FuturesHistoricalFactory, FuturesRealtimeFactory
from .eastmoney import EastmoneyFuturesHistoricalProvider, EastmoneyFuturesRealtimeProvider
from .efinance import EfinanceFuturesHistoricalProvider, EfinanceFuturesRealtimeProvider
from .margin import (
    CONTRACT_MULTIPLIERS,
    DEFAULT_MARGIN_RATE,
    FuturesMarginFactory,
    FuturesMarginProvider,
    calculate_position_value,
    calculate_required_margin,
    get_contract_multiplier,
    get_margin_rate_for_contract,
)
from .margin_sina import SinaFuturesMarginProvider
from .sina import SinaFuturesHistoricalProvider, SinaFuturesRealtimeProvider

__all__ = [
    "FuturesHistoricalFactory",
    "FuturesRealtimeFactory",
    "FuturesDataFactory",
    "FuturesMarginFactory",
    "FuturesMarginProvider",
    "SinaFuturesMarginProvider",
    "CONTRACT_MULTIPLIERS",
    "DEFAULT_MARGIN_RATE",
    "get_contract_multiplier",
    "get_margin_rate_for_contract",
    "calculate_position_value",
    "calculate_required_margin",
]
