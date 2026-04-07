"""
Tests for Index module.

This module tests index data functionality.
"""


import pandas as pd
import pytest

from akshare_one.modules.index import (
    IndexFactory,
    get_index_constituents,
    get_index_hist_data,
    get_index_realtime_data,
    get_index_list,
)
from akshare_one.modules.index.base import IndexProvider
from akshare_one.modules.index.eastmoney import EastmoneyIndexProvider
from akshare_one.modules.index.sina import SinaIndexProvider


class TestProviderBasics:
    """Test basic provider functionality (unit tests, no network required)."""

    def test_provider_initialization_eastmoney(self):
        """Test eastmoney provider can be initialized."""
        provider = EastmoneyIndexProvider()
        assert provider is not None
        assert isinstance(provider, IndexProvider)

    def test_provider_initialization_sina(self):
        """Test sina provider can be initialized."""
        provider = SinaIndexProvider()
        assert provider is not None
        assert isinstance(provider, IndexProvider)

    def test_provider_metadata_eastmoney(self):
        """Test eastmoney provider metadata properties."""
        provider = EastmoneyIndexProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"

    def test_provider_metadata_sina(self):
        """Test sina provider metadata properties."""
        provider = SinaIndexProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "sina"

    def test_provider_data_type(self):
        """Test provider data type identifier."""
        provider = EastmoneyIndexProvider()
        assert provider.get_data_type() == "index"

    def test_provider_update_frequency(self):
        """Test provider update frequency."""
        provider = EastmoneyIndexProvider()
        assert provider.get_update_frequency() == "daily"


class TestFactoryRegistration:
    """Test factory registration (unit tests, no network required)."""

    def test_factory_list_sources(self):
        """Test factory lists available sources."""
        sources = IndexFactory.list_sources()
        assert "eastmoney" in sources
        assert "sina" in sources

    def test_factory_has_source(self):
        """Test factory has_source method."""
        assert IndexFactory.has_source("eastmoney") is True
        assert IndexFactory.has_source("sina") is True
        assert IndexFactory.has_source("invalid") is False

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = IndexFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyIndexProvider)

    def test_factory_get_provider_sina(self):
        """Test factory creates sina provider."""
        provider = IndexFactory.get_provider(source="sina")
        assert isinstance(provider, SinaIndexProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            IndexFactory.get_provider(source="invalid")


class TestInvalidSource:
    """Test invalid source handling (unit tests, no network required)."""

    def test_invalid_source_index_hist(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_hist_data(symbol="000001", source="invalid")

    def test_invalid_source_index_realtime(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_realtime_data(source="invalid")

    def test_invalid_source_index_list(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_list(source="invalid")

    def test_invalid_source_index_constituents(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_constituents(symbol="000300", source="invalid")


@pytest.mark.integration
class TestGetIndexHistData:
    """Test get_index_hist_data function (integration tests, require network)."""

    def test_get_index_hist_data_eastmoney(self):
        """Test getting index historical data from eastmoney."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "close" in df.columns

    def test_get_index_hist_data_sina(self):
        """Test getting index historical data from sina."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sina",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_hist_data_with_filter(self):
        """Test index historical data with row filter."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
            row_filter={"top_n": 5},
        )

        assert df is not None
        if not df.empty:
            assert len(df) <= 5


@pytest.mark.integration
class TestGetIndexRealtimeData:
    """Test get_index_realtime_data function (integration tests, require network)."""

    def test_get_index_realtime_data_all(self):
        """Test getting all index realtime data."""
        df = get_index_realtime_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_realtime_data_single(self):
        """Test getting single index realtime data."""
        df = get_index_realtime_data(symbol="000001", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


@pytest.mark.integration
class TestGetIndexList:
    """Test get_index_list function (integration tests, require network)."""

    def test_get_index_list_cn(self):
        """Test getting Chinese index list."""
        df = get_index_list(category="cn", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_list_global(self):
        """Test getting global index list."""
        df = get_index_list(category="global", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


@pytest.mark.integration
class TestGetIndexConstituents:
    """Test get_index_constituents function (integration tests, require network)."""

    def test_get_index_constituents_csi300(self):
        """Test getting CSI 300 constituents."""
        df = get_index_constituents(symbol="000300", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "symbol" in df.columns

    def test_get_index_constituents_without_weight(self):
        """Test getting constituents without weight."""
        df = get_index_constituents(
            symbol="000300",
            include_weight=False,
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)