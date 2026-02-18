"""
Tests for Bond module.

This module tests bond (convertible bond) data functionality.
"""


import pandas as pd
import pytest

from akshare_one.modules.bond import (
    BondFactory,
    get_bond_hist_data,
    get_bond_list,
    get_bond_realtime_data,
)
from akshare_one.modules.bond.base import BondProvider
from akshare_one.modules.bond.eastmoney import EastmoneyBondProvider


class TestProviderBasics:
    """Test basic provider functionality."""

    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyBondProvider()
        assert provider is not None
        assert isinstance(provider, BondProvider)

    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyBondProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"
        assert "data_type" in metadata


class TestParameterValidation:
    """Test parameter validation."""

    def test_valid_symbol(self):
        """Test with valid bond symbol."""
        provider = EastmoneyBondProvider()
        provider.validate_symbol("sh113050")
        provider.validate_symbol("sz123456")

    def test_invalid_symbol_format(self):
        """Test with invalid symbol formats."""
        provider = EastmoneyBondProvider()

        with pytest.raises(ValueError):
            provider.validate_symbol("INVALID")


class TestGetBondList:
    """Test get_bond_list function."""

    def test_get_bond_list_eastmoney(self):
        """Test getting bond list from eastmoney."""
        df = get_bond_list(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "symbol" in df.columns

    def test_get_bond_list_jsl(self):
        """Test getting bond list from jsl."""
        df = get_bond_list(source="jsl")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetBondHistData:
    """Test get_bond_hist_data function."""

    def test_get_bond_hist_data(self):
        """Test getting bond historical data."""
        df = get_bond_hist_data(
            symbol="sh113050",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "close" in df.columns

    def test_get_bond_hist_data_empty_period(self):
        """Test with date range that returns no data."""
        df = get_bond_hist_data(
            symbol="sh113050",
            start_date="2099-01-01",
            end_date="2099-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetBondRealtimeData:
    """Test get_bond_realtime_data function."""

    def test_get_bond_realtime_data_eastmoney(self):
        """Test getting bond realtime data from eastmoney."""
        df = get_bond_realtime_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_bond_realtime_data_jsl(self):
        """Test getting bond realtime data from jsl."""
        df = get_bond_realtime_data(source="jsl")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "symbol" in df.columns
            assert "price" in df.columns


class TestInvalidSource:
    """Test invalid source handling."""

    def test_invalid_source_bond_list(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_bond_list(source="invalid")

    def test_invalid_source_bond_hist(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_bond_hist_data(symbol="sh113050", source="invalid")


class TestFactoryRegistration:
    """Test factory registration."""

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = BondFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyBondProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            BondFactory.get_provider(source="invalid")
