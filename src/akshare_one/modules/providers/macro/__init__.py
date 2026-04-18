"""Macro economic data providers."""

from .base import MacroFactory, MacroProvider
from .baostock import BaostockMacroProvider
from .lixinger import LixingerMacroProvider
from .official import OfficialMacroProvider
from .sina import SinaMacroProvider
from .tushare import TushareMacroProvider
from .akshare_source import MacroAkShareFactory, MacroAkShareProvider, AkShareMacroAkShareProvider

__all__ = [
    "MacroFactory",
    "MacroProvider",
    "BaostockMacroProvider",
    "LixingerMacroProvider",
    "OfficialMacroProvider",
    "SinaMacroProvider",
    "TushareMacroProvider",
    "MacroAkShareFactory",
    "MacroAkShareProvider",
    "AkShareMacroAkShareProvider",
]
