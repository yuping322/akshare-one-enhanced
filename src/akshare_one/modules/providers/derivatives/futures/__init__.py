"""Futures providers."""

from .base import FuturesHistoricalFactory, FuturesRealtimeFactory, FuturesDataFactory
from .eastmoney import EastmoneyFuturesHistoricalProvider, EastmoneyFuturesRealtimeProvider
from .efinance import EfinanceFuturesHistoricalProvider, EfinanceFuturesRealtimeProvider
from .sina import SinaFuturesHistoricalProvider, SinaFuturesRealtimeProvider
from .margin import (
    FuturesMarginFactory,
    FuturesMarginProvider,
    AkShareFuturesMarginProvider,
    CONTRACT_MULTIPLIERS,
    DEFAULT_MARGIN_RATE,
    get_contract_multiplier,
    get_margin_rate_for_contract,
    calculate_position_value,
    calculate_required_margin,
)

__all__ = [
    "FuturesHistoricalFactory",
    "FuturesRealtimeFactory",
    "FuturesDataFactory",
    "FuturesMarginFactory",
    "FuturesMarginProvider",
    "AkShareFuturesMarginProvider",
    "CONTRACT_MULTIPLIERS",
    "DEFAULT_MARGIN_RATE",
    "get_contract_multiplier",
    "get_margin_rate_for_contract",
    "calculate_position_value",
    "calculate_required_margin",
]
