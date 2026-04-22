from ..core.base import BaseProvider
from ..core.factory import BaseFactory
import pandas as pd
from typing import Any


class MockDataProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "mockdata"

    def set_preset_data(self, method_name: str, data: pd.DataFrame) -> None:
        """Set preset data for a specific method"""
        pass

    def set_error_mode(self, method_name: str, error: Exception | None = None) -> None:
        """Set error mode for a specific method"""
        pass

    def set_random_mode(self, method_name: str, rows: int = 100) -> None:
        """Set random generation mode for a specific method"""
        pass


class MockDataFactory(BaseFactory[MockDataProvider]):
    _providers: dict[str, type[MockDataProvider]] = {}
