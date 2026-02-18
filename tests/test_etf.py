"""
Tests for ETF module.

This module tests ETF data functionality.
"""


import pandas as pd
import pytest

from akshare_one.modules.etf import (
    ETFFactory,
    get_etf_hist_data,
    get_etf_list,
    get_etf_realtime_data,
    get_fund_manager_info,
    get_fund_rating_data,
)
from akshare_one.modules.etf.base import ETFProvider
from akshare_one.modules.etf.eastmoney import EastmoneyETFProvider


class TestProviderBasics:
    """Test basic provider functionality."""

    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyETFProvider()
        assert provider is not None
        assert isinstance(provider, ETFProvider)

    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyETFProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"


class TestGetETFHistData:
    """Test get_etf_hist_data function."""

    def test_get_etf_hist_data_eastmoney(self):
        """Test getting ETF historical data from eastmoney."""
        df = get_etf_hist_data(
            symbol="159915",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "close" in df.columns

    def test_get_etf_hist_data_with_filter(self):
        """Test ETF historical data with row filter."""
        df = get_etf_hist_data(
            symbol="159915",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
            row_filter={"top_n": 5},
        )

        assert df is not None
        if not df.empty:
            assert len(df) <= 5


class TestGetETFRealtimeData:
    """Test get_etf_realtime_data function."""

    def test_get_etf_realtime_data_eastmoney(self):
        """Test getting ETF realtime data from eastmoney."""
        df = get_etf_realtime_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "symbol" in df.columns

    def test_get_etf_realtime_data_sina(self):
        """Test getting ETF realtime data from sina."""
        df = get_etf_realtime_data(source="sina")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetETFList:
    """Test get_etf_list function."""

    def test_get_etf_list_all(self):
        """Test getting all ETF list."""
        df = get_etf_list(category="all", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_etf_list_stock(self):
        """Test getting stock ETF list."""
        df = get_etf_list(category="stock", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetFundManagerInfo:
    """Test get_fund_manager_info function."""

    def test_get_fund_manager_info(self):
        """Test getting fund manager info."""
        df = get_fund_manager_info(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetFundRatingData:
    """Test get_fund_rating_data function."""

    def test_get_fund_rating_data(self):
        """Test getting fund rating data."""
        df = get_fund_rating_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestInvalidSource:
    """Test invalid source handling."""

    def test_invalid_source_etf_hist(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_etf_hist_data(symbol="159915", source="invalid")

    def test_invalid_source_etf_realtime(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_etf_realtime_data(source="invalid")


class TestFactoryRegistration:
    """Test factory registration."""

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = ETFFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyETFProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            ETFFactory.get_provider(source="invalid")
