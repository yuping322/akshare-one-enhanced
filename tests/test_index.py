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
    get_index_list,
    get_index_realtime_data,
)
from akshare_one.modules.index.base import IndexProvider
from akshare_one.modules.index.eastmoney import EastmoneyIndexProvider


class TestProviderBasics:
    """Test basic provider functionality."""

    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyIndexProvider()
        assert provider is not None
        assert isinstance(provider, IndexProvider)

    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyIndexProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"


class TestGetIndexHistData:
    """Test get_index_hist_data function."""

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


class TestGetIndexRealtimeData:
    """Test get_index_realtime_data function."""

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


class TestGetIndexList:
    """Test get_index_list function."""

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


class TestGetIndexConstituents:
    """Test get_index_constituents function."""

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


class TestInvalidSource:
    """Test invalid source handling."""

    def test_invalid_source_index_hist(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_hist_data(symbol="000001", source="invalid")

    def test_invalid_source_index_realtime(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_realtime_data(source="invalid")


class TestFactoryRegistration:
    """Test factory registration."""

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = IndexFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyIndexProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            IndexFactory.get_provider(source="invalid")
