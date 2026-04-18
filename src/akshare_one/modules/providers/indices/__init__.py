"""Index providers."""

from .base import IndexFactory, IndexProvider
from .eastmoney import EastmoneyIndexProvider
from .efinance import EfinanceIndexProvider
from .lixinger import LixingerIndexProvider
from .sina import SinaIndexProvider
from .tushare import TushareIndexProvider
from .weights.base import IndexWeightsFactory, IndexWeightsProvider
from .weights.akshare import AkShareIndexWeightsProvider
from .weights.tushare import TushareIndexWeightsProvider

__all__ = [
    "IndexFactory",
    "IndexProvider",
    "EastmoneyIndexProvider",
    "EfinanceIndexProvider",
    "LixingerIndexProvider",
    "SinaIndexProvider",
    "TushareIndexProvider",
    "IndexWeightsFactory",
    "IndexWeightsProvider",
    "AkShareIndexWeightsProvider",
    "TushareIndexWeightsProvider",
]
