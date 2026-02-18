"""
Tests for Valuation module.

This module tests valuation data functionality.
"""


import pandas as pd
import pytest

from akshare_one.modules.valuation import (
    ValuationFactory,
    get_market_valuation,
    get_stock_valuation,
)
from akshare_one.modules.valuation.base import ValuationProvider
from akshare_one.modules.valuation.eastmoney import EastmoneyValuationProvider


class TestProviderBasics:
    """Test basic provider functionality."""

    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyValuationProvider()
        assert provider is not None
        assert isinstance(provider, ValuationProvider)

    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyValuationProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"


class TestGetStockValuation:
    """Test get_stock_valuation function."""

    def test_get_stock_valuation_eastmoney(self):
        """Test getting stock valuation data from eastmoney."""
        df = get_stock_valuation(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "pe_ttm" in df.columns or "pe" in df.columns
            assert "pb" in df.columns

    def test_get_stock_valuation_empty_period(self):
        """Test with date range that returns no data."""
        df = get_stock_valuation(
            symbol="600000",
            start_date="2099-01-01",
            end_date="2099-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_stock_valuation_different_symbol(self):
        """Test with different stock symbol."""
        df = get_stock_valuation(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestGetMarketValuation:
    """Test get_market_valuation function."""

    def test_get_market_valuation_eastmoney(self):
        """Test getting market valuation from eastmoney."""
        df = get_market_valuation(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "pe" in df.columns or "pb" in df.columns

    def test_get_market_valuation_legu(self):
        """Test getting market valuation from legu."""
        df = get_market_valuation(source="legu")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


class TestValuationDataQuality:
    """Test valuation data quality."""

    def test_pe_ratio_reasonable_range(self):
        """Test PE ratio is in reasonable range."""
        df = get_stock_valuation(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        if not df.empty and "pe_ttm" in df.columns:
            pe_values = df["pe_ttm"].dropna()
            if len(pe_values) > 0:
                assert (pe_values > 0).all() or (pe_values < 1000).all()

    def test_pb_ratio_positive(self):
        """Test PB ratio is positive."""
        df = get_stock_valuation(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        if not df.empty and "pb" in df.columns:
            pb_values = df["pb"].dropna()
            if len(pb_values) > 0:
                assert (pb_values > 0).all()


class TestInvalidSource:
    """Test invalid source handling."""

    def test_invalid_source_stock_valuation(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_stock_valuation(symbol="600000", source="invalid")

    def test_invalid_source_market_valuation(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_market_valuation(source="invalid")


class TestFactoryRegistration:
    """Test factory registration."""

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = ValuationFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyValuationProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            ValuationFactory.get_provider(source="invalid")
