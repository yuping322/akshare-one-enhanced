"""
src/akshare_one/jq_compat/bond.py
JQ-compatible bond APIs.
"""

try:
    from ..modules.bond import get_bond_list as _get_list_ak, get_bond_premium as _get_premium_ak
except ImportError:
    from ..modules.providers.fixed_income.bonds import BondFactory

    def _get_list_ak():
        provider = BondFactory.get_provider("eastmoney")
        return provider.get_bond_list()

    def _get_premium_ak(symbol: str):
        provider = BondFactory.get_provider("eastmoney")
        return provider.get_bond_premium(symbol)


from typing import List, Optional, Union
import pandas as pd


def get_bond_list(date: Optional[str] = None) -> pd.DataFrame:
    """
    Get list of active conversion bonds. JQ-style.
    """
    return _get_list_ak()


def get_bond_premium(symbol: str) -> pd.DataFrame:
    """
    Get bond premium details. JQ-style.
    """
    return _get_premium_ak(symbol=symbol)


__all__ = ["get_bond_list", "get_bond_premium"]
