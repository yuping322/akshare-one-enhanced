"""
Factory for creating financial data providers.
"""

from ..factory_base import BaseFactory
from .base import FinancialDataProvider
from .cninfo import CninfoFinancialReport
from .eastmoney_direct import EastMoneyDirectFinancialReport
from .sina import SinaFinancialReport


class FinancialDataFactory(BaseFactory[FinancialDataProvider]):
    """Factory class for creating financial data providers."""

    _providers: dict[str, type[FinancialDataProvider]] = {
        "sina": SinaFinancialReport,
        "eastmoney_direct": EastMoneyDirectFinancialReport,
        "cninfo": CninfoFinancialReport,
    }
