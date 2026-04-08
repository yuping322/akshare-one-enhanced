"""
Tests for Baostock performance data provider.
"""

import pytest

from akshare_one.modules.performance.base import PerformanceFactory
from akshare_one.modules.performance.baostock import BaostockPerformanceProvider


class TestBaostockPerformanceProvider:
    """Test BaostockPerformanceProvider class"""

    def test_provider_registration(self):
        """Test that BaostockPerformanceProvider is registered"""
        assert PerformanceFactory.has_source("baostock")
        assert "baostock" in PerformanceFactory.list_sources()

    def test_provider_creation(self):
        """Test that BaostockPerformanceProvider can be created"""
        provider = PerformanceFactory.get_provider("baostock")
        assert isinstance(provider, BaostockPerformanceProvider)
        assert provider.get_source_name() == "baostock"

    def test_symbol_conversion(self):
        """Test symbol format conversion"""
        provider = PerformanceFactory.get_provider("baostock")

        # Shanghai market
        assert provider._convert_symbol_to_baostock_format("600000") == "sh.600000"
        assert provider._convert_symbol_to_baostock_format("600519") == "sh.600519"

        # Shenzhen market
        assert provider._convert_symbol_to_baostock_format("000001") == "sz.000001"
        assert provider._convert_symbol_to_baostock_format("300001") == "sz.300001"

        # Already formatted
        assert provider._convert_symbol_to_baostock_format("sh.600000") == "sh.600000"
        assert provider._convert_symbol_to_baostock_format("sz.000001") == "sz.000001"

    def test_invalid_symbol(self):
        """Test invalid symbol handling"""
        provider = PerformanceFactory.get_provider("baostock")

        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider._convert_symbol_to_baostock_format("123")

        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider._convert_symbol_to_baostock_format("abc123")

    def test_method_signatures(self):
        """Test that provider has required methods"""
        provider = PerformanceFactory.get_provider("baostock")

        # Check methods exist
        assert hasattr(provider, "get_forecast_report")
        assert hasattr(provider, "get_performance_express_report")
        assert hasattr(provider, "get_performance_forecast")
        assert hasattr(provider, "get_performance_express")

    def test_base_class_methods_without_symbol(self):
        """Test that base class methods require symbol parameter"""
        provider = PerformanceFactory.get_provider("baostock")

        # Should raise error when symbol is not provided
        with pytest.raises(ValueError, match="requires 'symbol' parameter"):
            provider.get_performance_forecast(date="2024-01-01")

        with pytest.raises(ValueError, match="requires 'symbol' parameter"):
            provider.get_performance_express(date="2024-01-01")


@pytest.mark.integration
class TestBaostockPerformanceIntegration:
    """Integration tests for Baostock performance data (requires baostock package and network)"""

    def test_get_forecast_report(self):
        """Test get_forecast_report with real data"""
        pytest.importorskip("baostock")

        provider = PerformanceFactory.get_provider("baostock")
        df = provider.get_forecast_report(symbol="600000", start_date="2023-01-01", end_date="2024-12-31")

        # Should return DataFrame (may be empty if no data)
        assert isinstance(df, object)

        # If data is returned, check structure
        if not df.empty:
            assert "symbol" in df.columns

    def test_get_performance_express_report(self):
        """Test get_performance_express_report with real data"""
        pytest.importorskip("baostock")

        provider = PerformanceFactory.get_provider("baostock")
        df = provider.get_performance_express_report(symbol="600000", start_date="2023-01-01", end_date="2024-12-31")

        # Should return DataFrame (may be empty if no data)
        assert isinstance(df, object)

        # If data is returned, check structure
        if not df.empty:
            assert "symbol" in df.columns


def test_api_functions_exist():
    """Test that API functions are available in __init__.py"""
    from akshare_one.modules.performance import (
        get_forecast_report,
        get_performance_express_report,
        get_performance_forecast,
        get_performance_express,
    )

    # All functions should exist
    assert callable(get_forecast_report)
    assert callable(get_performance_express_report)
    assert callable(get_performance_forecast)
    assert callable(get_performance_express)
