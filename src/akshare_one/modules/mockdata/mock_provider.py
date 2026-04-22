import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any
from ..core.base import BaseProvider
from .base import MockDataFactory


@MockDataFactory.register("mock")
class MockDataProvider(BaseProvider):
    """Mock data provider for testing"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._preset_data: dict[str, pd.DataFrame] = {}
        self._errors: dict[str, Exception] = {}
        self._random_config: dict[str, int] = {}

    def get_source_name(self) -> str:
        return "mock"

    def set_preset_data(self, method_name: str, data: pd.DataFrame) -> None:
        self._preset_data[method_name] = data

    def set_error_mode(self, method_name: str, error: Exception | None = None) -> None:
        if error is None:
            error = ValueError(f"Mock error for {method_name}")
        self._errors[method_name] = error

    def set_random_mode(self, method_name: str, rows: int = 100) -> None:
        self._random_config[method_name] = rows

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        method = "get_stock_daily"
        if method in self._errors:
            raise self._errors[method]
        if method in self._preset_data:
            return self._preset_data[method]

        rows = self._random_config.get(method, 100)
        return self._generate_stock_daily(symbol, start_date, end_date, rows)

    def get_realtime_data(self, symbol: str = "") -> pd.DataFrame:
        method = "get_realtime_data"
        if method in self._errors:
            raise self._errors[method]
        if method in self._preset_data:
            return self._preset_data[method]

        return self._generate_realtime_data(symbol)

    def get_basic_info(self, symbol: str) -> pd.DataFrame:
        method = "get_basic_info"
        if method in self._errors:
            raise self._errors[method]
        if method in self._preset_data:
            return self._preset_data[method]

        return self._generate_basic_info(symbol)

    def _generate_stock_daily(self, symbol: str, start_date: str, end_date: str, rows: int) -> pd.DataFrame:
        dates = pd.date_range(start=start_date, end=end_date, freq="B")[:rows]
        np.random.seed(42)
        base_price = 10.0
        prices = base_price * np.cumprod(1 + np.random.normal(0, 0.02, len(dates)))

        return pd.DataFrame(
            {
                "date": dates,
                "symbol": symbol,
                "open": prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
                "high": prices * (1 + np.random.uniform(0, 0.02, len(dates))),
                "low": prices * (1 - np.random.uniform(0, 0.02, len(dates))),
                "close": prices,
                "volume": np.random.randint(100000, 10000000, len(dates)),
                "amount": prices * np.random.randint(100000, 10000000, len(dates)),
            }
        )

    def _generate_realtime_data(self, symbol: str) -> pd.DataFrame:
        np.random.seed(42)
        data = {
            "symbol": [symbol] if symbol else ["600000", "000001", "000002"],
            "name": ["测试股票"] if symbol else ["测试股票1", "测试股票2", "测试股票3"],
            "price": np.random.uniform(10, 100, 1 if symbol else 3),
            "change_pct": np.random.uniform(-5, 5, 1 if symbol else 3),
            "volume": np.random.randint(100000, 10000000, 1 if symbol else 3),
            "amount": np.random.uniform(1000000, 100000000, 1 if symbol else 3),
        }
        return pd.DataFrame(data)

    def _generate_basic_info(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": [symbol],
                "name": ["测试股票"],
                "industry": ["测试行业"],
                "total_shares": [1000000000],
                "float_shares": [800000000],
                "listing_date": ["2020-01-01"],
            }
        )
