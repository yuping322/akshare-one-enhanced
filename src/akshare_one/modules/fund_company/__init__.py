"""
Fund company data module.

This module provides fund company information and related data.
"""

from . import lixinger
from .base import FundCompanyFactory, FundCompanyProvider

__all__ = ["FundCompanyProvider", "FundCompanyFactory"]
