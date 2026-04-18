"""News providers."""
from .base import NewsDataFactory, NewsDataProvider
from .eastmoney import EastmoneyNewsProvider
from .sina import SinaNewsProvider

__all__ = ["NewsDataFactory", "NewsDataProvider", "EastmoneyNewsProvider", "SinaNewsProvider"]
