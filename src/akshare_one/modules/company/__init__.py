"""
Company data module.

This module provides company profile and related data.
"""

from .base import CompanyFactory, CompanyProvider
from . import lixinger

__all__ = ["CompanyProvider", "CompanyFactory"]
