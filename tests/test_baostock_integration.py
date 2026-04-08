"""
Test Baostock integration.

This test file demonstrates how to use Baostock as a data source.
"""

import pytest
import pandas as pd

from akshare_one.modules.historical import HistoricalDataFactory
from akshare_one.modules.historical.baostock import BaostockHistorical


class TestBaostockProvider:
    """Test Baostock historical data provider."""

    @pytest.mark.integration
    def test_get_hist_data_daily(self):
        """Test getting daily historical data from Baostock."""
        provider = HistoricalDataFactory.get_provider(
            "baostock", symbol="sh.600000", interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "Should return historical data"
        assert "timestamp" in df.columns
        assert "close" in df.columns

    @pytest.mark.integration
    def test_get_hist_data_with_adjust(self):
        """Test getting historical data with price adjustment."""
        provider = HistoricalDataFactory.get_provider(
            "baostock", symbol="sh.600000", interval="day", start_date="2024-01-01", end_date="2024-01-10", adjust="hfq"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "timestamp" in df.columns
            assert "close" in df.columns

    @pytest.mark.integration
    def test_symbol_conversion(self):
        """Test symbol conversion to baostock format."""
        provider1 = BaostockHistorical(symbol="600000", interval="day")
        bs_code1 = provider1._convert_symbol_to_baostock_format("600000")
        assert bs_code1 == "sh.600000"

        provider2 = BaostockHistorical(symbol="000001", interval="day")
        bs_code2 = provider2._convert_symbol_to_baostock_format("000001")
        assert bs_code2 == "sz.000001"

    @pytest.mark.integration
    def test_week_interval(self):
        """Test getting weekly historical data."""
        provider = HistoricalDataFactory.get_provider(
            "baostock", symbol="sh.600000", interval="week", start_date="2024-01-01", end_date="2024-01-31"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "timestamp" in df.columns
            assert "close" in df.columns

    @pytest.mark.integration
    def test_month_interval(self):
        """Test getting monthly historical data."""
        provider = HistoricalDataFactory.get_provider(
            "baostock", symbol="sh.600000", interval="month", start_date="2024-01-01", end_date="2024-03-31"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "timestamp" in df.columns
            assert "close" in df.columns

    def test_minute_interval_not_supported(self):
        """Test that minute interval raises error."""
        provider = BaostockHistorical(symbol="600000", interval="minute")

        with pytest.raises(ValueError, match="does not support minute"):
            provider.get_hist_data()

    def test_hour_interval_not_supported(self):
        """Test that hour interval raises error."""
        provider = BaostockHistorical(symbol="600000", interval="hour")

        with pytest.raises(ValueError, match="does not support minute or hour"):
            provider.get_hist_data()

    def test_adjust_flag_mapping(self):
        """Test adjust flag mapping."""
        provider = BaostockHistorical(symbol="600000")

        assert provider._map_adjust_param("none") == "3"
        assert provider._map_adjust_param("qfq") == "2"
        assert provider._map_adjust_param("hfq") == "1"

    @pytest.mark.integration
    def test_logout(self):
        """Test logout functionality."""
        BaostockHistorical.logout()
        assert not BaostockHistorical._is_logged_in

        # Re-login for subsequent tests
        BaostockHistorical._ensure_login()
        assert BaostockHistorical._is_logged_in


class TestBaostockMultiSource:
    """Test using Baostock alongside other sources."""

    @pytest.mark.integration
    def test_list_sources(self):
        """Test that Baostock is registered in factories."""
        historical_sources = HistoricalDataFactory.list_sources()
        assert "baostock" in historical_sources

    @pytest.mark.integration
    def test_compare_with_eastmoney(self):
        """Compare data from Baostock and Eastmoney."""
        symbol = "600000"

        baostock_provider = HistoricalDataFactory.get_provider(
            "baostock", symbol=f"sh.{symbol}", interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )
        baostock_df = baostock_provider.get_hist_data()

        eastmoney_provider = HistoricalDataFactory.get_provider(
            "eastmoney", symbol=symbol, interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )
        eastmoney_df = eastmoney_provider.get_hist_data()

        assert isinstance(baostock_df, pd.DataFrame)
        assert isinstance(eastmoney_df, pd.DataFrame)

        if not baostock_df.empty and not eastmoney_df.empty:
            assert "timestamp" in baostock_df.columns
            assert "timestamp" in eastmoney_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
