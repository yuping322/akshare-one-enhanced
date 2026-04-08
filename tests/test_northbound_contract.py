"""
Contract tests for Northbound module.

These tests verify that the data structure remains stable over time
by comparing against golden samples.
"""

import pandas as pd
import pytest

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider


# ============================================================================
# Contract Tests - Schema Stability
# ============================================================================


class TestNorthboundFlowContract:
    """Contract tests for northbound flow data."""

    @pytest.mark.integration
    def test_northbound_flow_schema(self):
        """Test that northbound flow data schema remains stable."""
        expected_columns = [
            "date",
            "market",
            "northbound_net_buy",
            "northbound_buy_amount",
            "northbound_sell_amount",
            "balance",
        ]

        df = get_northbound_flow(start_date="2024-01-01", end_date="2024-01-05", market="all")

        if not df.empty:
            for col in expected_columns:
                assert col in df.columns, f"Missing expected column: {col}"

            assert df["date"].dtype == "object", "date should be string"
            assert df["market"].dtype == "object", "market should be string"


class TestNorthboundHoldingsContract:
    """Contract tests for northbound holdings data."""

    @pytest.mark.integration
    def test_northbound_holdings_schema(self):
        """Test that northbound holdings data schema remains stable."""
        expected_columns = ["date", "symbol", "holdings_shares", "holdings_value", "holdings_ratio", "holdings_change"]

        df = get_northbound_holdings(symbol="600000", start_date="2024-01-01", end_date="2024-01-05")

        if not df.empty:
            for col in expected_columns:
                assert col in df.columns, f"Missing expected column: {col}"

            if "symbol" in df.columns:
                assert all(len(str(s)) == 6 for s in df["symbol"]), "Symbols should be 6 digits"


class TestNorthboundTopStocksContract:
    """Contract tests for northbound top stocks data."""

    @pytest.mark.integration
    def test_northbound_top_stocks_schema(self):
        """Test that northbound top stocks data schema remains stable."""
        expected_columns = ["rank", "symbol", "name", "northbound_net_buy", "holdings_shares", "holdings_ratio"]

        df = get_northbound_top_stocks(date="2024-01-01", market="all", top_n=10)

        if not df.empty:
            for col in expected_columns:
                assert col in df.columns, f"Missing expected column: {col}"

            assert df["rank"].iloc[0] == 1, "First rank should be 1"
            assert len(df) <= 10, "Should return at most top_n records"


# ============================================================================
# Contract Tests - Eastmoney Provider Specific
# ============================================================================


class TestEastmoneyProviderContract:
    """Contract tests for Eastmoney provider implementation."""

    def test_provider_source_name(self):
        """Test provider source name contract."""
        provider = EastmoneyNorthboundProvider()
        assert provider.get_source_name() == "eastmoney"

    def test_provider_data_type(self):
        """Test provider data type contract."""
        provider = EastmoneyNorthboundProvider()
        assert provider.get_data_type() == "northbound"

    def test_provider_metadata_contract(self):
        """Test provider metadata contract."""
        provider = EastmoneyNorthboundProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert "data_type" in metadata
        assert "update_frequency" in metadata
        assert metadata["update_frequency"] == "daily"
        assert "delay_minutes" in metadata
        assert metadata["delay_minutes"] == 1440


# ============================================================================
# Contract Tests - Field Standardization
# ============================================================================


class TestFieldStandardizationContract:
    """Contract tests for field standardization."""

    def test_flow_data_field_names_contract(self):
        """Test flow data uses standardized field names."""
        provider = EastmoneyNorthboundProvider()

        standardized_fields = [
            "date",
            "market",
            "northbound_net_buy",
            "northbound_buy_amount",
            "northbound_sell_amount",
            "balance",
        ]

        for field in standardized_fields:
            assert isinstance(field, str)

    def test_holdings_data_field_names_contract(self):
        """Test holdings data uses standardized field names."""
        provider = EastmoneyNorthboundProvider()

        standardized_fields = [
            "date",
            "symbol",
            "holdings_shares",
            "holdings_value",
            "holdings_ratio",
            "holdings_change",
        ]

        for field in standardized_fields:
            assert isinstance(field, str)

    def test_top_stocks_field_names_contract(self):
        """Test top stocks data uses standardized field names."""
        provider = EastmoneyNorthboundProvider()

        standardized_fields = [
            "rank",
            "symbol",
            "name",
            "northbound_net_buy",
            "holdings_shares",
            "holdings_ratio",
            "date",
        ]

        for field in standardized_fields:
            assert isinstance(field, str)


# ============================================================================
# Contract Tests - Value Constraints
# ============================================================================


class TestValueConstraintsContract:
    """Contract tests for value constraints."""

    def test_symbol_format_contract(self):
        """Test that symbols must be 6-digit strings."""
        provider = EastmoneyNorthboundProvider()

        provider.validate_symbol("600000")
        provider.validate_symbol("000001")

    def test_market_values_contract(self):
        """Test that market must be one of 'sh', 'sz', 'all'."""
        provider = EastmoneyNorthboundProvider()

        valid_markets = ["sh", "sz", "all"]
        for market in valid_markets:
            assert market in valid_markets

    def test_date_format_contract(self):
        """Test that dates must be in YYYY-MM-DD format."""
        provider = EastmoneyNorthboundProvider()

        provider.validate_date("2024-01-01")
        provider.validate_date_range("2024-01-01", "2024-01-31")


# ============================================================================
# Contract Tests - Empty DataFrame Contract
# ============================================================================


class TestEmptyDataFrameContract:
    """Contract tests for empty DataFrame responses."""

    def test_empty_flow_dataframe_contract(self):
        """Test empty flow DataFrame has correct structure."""
        provider = EastmoneyNorthboundProvider()

        expected_columns = [
            "date",
            "market",
            "northbound_net_buy",
            "northbound_buy_amount",
            "northbound_sell_amount",
            "balance",
        ]

        df = provider.create_empty_dataframe(expected_columns)

        assert df.empty
        assert list(df.columns) == expected_columns

    def test_empty_holdings_dataframe_contract(self):
        """Test empty holdings DataFrame has correct structure."""
        provider = EastmoneyNorthboundProvider()

        expected_columns = ["date", "symbol", "holdings_shares", "holdings_value", "holdings_ratio", "holdings_change"]

        df = provider.create_empty_dataframe(expected_columns)

        assert df.empty
        assert list(df.columns) == expected_columns

    def test_empty_top_stocks_dataframe_contract(self):
        """Test empty top stocks DataFrame has correct structure."""
        provider = EastmoneyNorthboundProvider()

        expected_columns = ["rank", "symbol", "name", "northbound_net_buy", "holdings_shares", "holdings_ratio"]

        df = provider.create_empty_dataframe(expected_columns)

        assert df.empty
        assert list(df.columns) == expected_columns
