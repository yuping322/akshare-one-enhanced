"""Board providers."""
from .base import BoardFactory, BoardProvider
from .eastmoney import EastmoneyBoardProvider
from .efinance import EfinanceBoardProvider

__all__ = ["BoardFactory", "BoardProvider", "EastmoneyBoardProvider", "EfinanceBoardProvider"]
