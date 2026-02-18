"""
Factory for creating historical data providers.
"""

from ..factory_base import BaseFactory
from .base import HistoricalDataProvider
from .eastmoney import EastMoneyHistorical
from .eastmoney_direct import EastMoneyDirectHistorical
from .netease import NetEaseHistorical
from .sina import SinaHistorical
from .tencent import TencentHistorical


class HistoricalDataFactory(BaseFactory[HistoricalDataProvider]):
    """Factory class for creating historical data providers."""

    _providers: dict[str, type[HistoricalDataProvider]] = {
        "eastmoney": EastMoneyHistorical,
        "eastmoney_direct": EastMoneyDirectHistorical,
        "sina": SinaHistorical,
        "tencent": TencentHistorical,
        "netease": NetEaseHistorical,
    }
