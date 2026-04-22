from typing import Any
import pandas as pd
from .base import MockDataFactory, MockDataProvider
from . import mock_provider


def create_mock_with_sample_data() -> MockDataProvider:
    """Create a mock provider with sample stock data"""
    provider = MockDataFactory.get_provider("mock")
    return provider


def create_mock_with_error(error_msg: str = "Mock error") -> MockDataProvider:
    """Create a mock provider that always raises errors"""
    provider = MockDataFactory.get_provider("mock")
    provider.set_error_mode("get_stock_daily", ValueError(error_msg))
    return provider


__all__ = ["create_mock_with_sample_data", "create_mock_with_error", "MockDataFactory"]
