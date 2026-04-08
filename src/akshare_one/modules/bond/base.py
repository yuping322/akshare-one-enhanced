"""
src/akshare_one/modules/bond/base.py
Base classes for bond data providers.
"""

import pandas as pd
from ..base import BaseProvider
from ..factory_base import BaseFactory

class BondProvider(BaseProvider):
    """Base class for bond data providers."""
    def get_data_type(self) -> str:
        return "bond"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_bond_list(self) -> pd.DataFrame:
        """Get list of active bonds (Conversion bonds)."""
        return self._execute_api_mapped("get_bond_list")

    def get_bond_premium(self, symbol: str) -> pd.DataFrame:
        """Get bond premium rates and valuation."""
        return self._execute_api_mapped("get_bond_premium", symbol=symbol)

class BondFactory(BaseFactory[BondProvider]):
    """Factory for bond data providers."""
    _providers: dict[str, type[BondProvider]] = {}
