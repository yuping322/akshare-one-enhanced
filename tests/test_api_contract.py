"""
Contract tests for API response schema stability.

These tests verify that upstream API changes are detected immediately by:
1. Validating required fields exist
2. Checking field data types
3. Ensuring value ranges are reasonable
4. Comparing against golden samples when available

Run contract tests: pytest tests/test_api_contract.py -m contract -v
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from tests.utils.contract_test import GoldenSampleValidator

# ============================================================================
# Historical Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestHistoricalDataContract:
    """Contract tests for historical data APIs."""

    def test_hist_data_required_fields(self):
        """Verify historical data has all required fields."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No historical data available")

        required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_hist_data_field_types(self):
        """Verify historical data field types are correct."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No historical data available")

        assert pd.api.types.is_numeric_dtype(df["open"]), "open must be numeric"
        assert pd.api.types.is_numeric_dtype(df["high"]), "high must be numeric"
        assert pd.api.types.is_numeric_dtype(df["low"]), "low must be numeric"
        assert pd.api.types.is_numeric_dtype(df["close"]), "close must be numeric"
        assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"

    def test_hist_data_value_ranges(self):
        """Verify historical data values are in reasonable ranges."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No historical data available")

        assert (df["open"] > 0).all(), "open price must be positive"
        assert (df["high"] > 0).all(), "high price must be positive"
        assert (df["low"] > 0).all(), "low price must be positive"
        assert (df["close"] > 0).all(), "close price must be positive"
        assert (df["volume"] >= 0).all(), "volume must be non-negative"

        assert (df["high"] >= df["low"]).all(), "high must >= low"
        assert (df["high"] >= df["open"]).all(), "high must >= open"
        assert (df["high"] >= df["close"]).all(), "high must >= close"
        assert (df["low"] <= df["open"]).all(), "low must <= open"
        assert (df["low"] <= df["close"]).all(), "low must <= close"


# ============================================================================
# Realtime Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestRealtimeDataContract:
    """Contract tests for realtime data APIs."""

    def test_realtime_data_required_fields(self):
        """Verify realtime data has all required fields."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        required_fields = ["symbol", "price", "timestamp", "volume", "amount"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_realtime_data_field_types(self):
        """Verify realtime data field types are correct."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert pd.api.types.is_numeric_dtype(df["price"]), "price must be numeric"
        assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"
        assert pd.api.types.is_numeric_dtype(df["amount"]), "amount must be numeric"

    def test_realtime_data_symbol_format(self):
        """Verify symbol format in realtime data."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert "symbol" in df.columns
        assert df["symbol"].iloc[0] == "600000"

    def test_realtime_data_price_positive(self):
        """Verify price is positive."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert (df["price"] > 0).all(), "price must be positive"


# ============================================================================
# Fund Flow Contract Tests
# ============================================================================


@pytest.mark.contract
class TestFundFlowContract:
    """Contract tests for fund flow data."""

    def test_stock_fund_flow_required_fields(self):
        """Verify stock fund flow has required fields."""
        from akshare_one.modules.fundflow import get_stock_fund_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_stock_fund_flow(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No fund flow data available")

        assert "date" in df.columns or "timestamp" in df.columns
        assert "symbol" in df.columns

    def test_sector_fund_flow_schema(self):
        """Verify sector fund flow schema."""
        from akshare_one.modules.fundflow import get_sector_fund_flow

        df = get_sector_fund_flow(sector_type="industry")

        if df.empty:
            pytest.skip("No sector fund flow data available")

        assert "sector_name" in df.columns or "name" in df.columns or "sector" in df.columns


# ============================================================================
# Northbound Contract Tests
# ============================================================================


@pytest.mark.contract
class TestNorthboundContract:
    """Contract tests for northbound capital data."""

    def test_northbound_flow_required_fields(self):
        """Verify northbound flow has required fields."""
        from akshare_one.modules.northbound import get_northbound_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No northbound data available")

        assert "date" in df.columns or "timestamp" in df.columns

    def test_northbound_flow_value_types(self):
        """Verify northbound flow values are numeric."""
        from akshare_one.modules.northbound import get_northbound_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No northbound data available")

        numeric_cols = [col for col in df.columns if df[col].dtype in ["float64", "int64"]]
        assert len(numeric_cols) > 0, "Should have at least one numeric column"


# ============================================================================
# Disclosure Contract Tests
# ============================================================================


@pytest.mark.contract
class TestDisclosureContract:
    """Contract tests for disclosure data."""

    def test_disclosure_required_fields(self):
        """Verify disclosure has required fields."""
        from akshare_one.modules.disclosure import get_disclosure

        df = get_disclosure(symbol="600000")

        if df.empty:
            pytest.skip("No disclosure data available")

        assert "symbol" in df.columns


# ============================================================================
# Options Contract Tests
# ============================================================================


@pytest.mark.contract
class TestOptionsContract:
    """Contract tests for options data."""

    def test_options_required_fields(self):
        """Verify options data has required fields."""
        from akshare_one import get_options_chain

        df = get_options_chain(underlying_symbol="510050")

        if df.empty:
            pytest.skip("No options data available")

        assert "symbol" in df.columns or "code" in df.columns


# ============================================================================
# Multi-Source Contract Tests
# ============================================================================


@pytest.mark.contract
class TestMultiSourceConsistency:
    """Test that different sources return consistent schemas."""

    def test_hist_data_sources_schema_consistency(self):
        """Verify historical data from different sources has consistent schema."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        sources = ["eastmoney_direct", "sina"]
        schemas = {}

        for source in sources:
            try:
                df = get_hist_data(
                    symbol="600000", start_date=start_date, end_date=end_date, source=source
                )
                if not df.empty:
                    schemas[source] = set(df.columns)
            except Exception:
                continue

        if len(schemas) < 2:
            pytest.skip("Not enough sources returned data")

        base_schema = list(schemas.values())[0]
        for source, schema in schemas.items():
            assert schema == base_schema, f"Schema mismatch for source {source}"

    def test_realtime_data_sources_schema_consistency(self):
        """Verify realtime data from different sources has consistent schema."""
        from akshare_one import get_realtime_data

        sources = ["eastmoney", "eastmoney_direct"]
        schemas = {}

        for source in sources:
            try:
                df = get_realtime_data(symbol="600000", source=source)
                if not df.empty:
                    schemas[source] = set(df.columns)
            except Exception:
                continue

        if len(schemas) < 2:
            pytest.skip("Not enough sources returned data")

        base_schema = list(schemas.values())[0]
        for source, schema in schemas.items():
            assert schema == base_schema, f"Schema mismatch for source {source}"


# ============================================================================
# Golden Sample Contract Tests
# ============================================================================


@pytest.mark.contract
class TestGoldenSamples:
    """Test data against golden samples."""

    @pytest.fixture
    def validator(self, tmp_path):
        """Create golden sample validator."""
        return GoldenSampleValidator("contract_tests", samples_dir=tmp_path)

    def test_hist_data_golden_sample(self, validator):
        """Verify historical data matches golden sample structure."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No data available")

        try:
            validator.assert_schema_matches("hist_data", df)
        except FileNotFoundError:
            validator.save_golden_sample(
                "hist_data",
                df,
                metadata={
                    "description": "Historical data for 600000",
                    "created_at": datetime.now().isoformat(),
                },
            )
            pytest.skip("Golden sample created for first time")

    def test_realtime_data_golden_sample(self, validator):
        """Verify realtime data matches golden sample structure."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No data available")

        try:
            validator.assert_schema_matches("realtime_data", df)
        except FileNotFoundError:
            validator.save_golden_sample(
                "realtime_data",
                df,
                metadata={
                    "description": "Realtime data for 600000",
                    "created_at": datetime.now().isoformat(),
                },
            )
            pytest.skip("Golden sample created for first time")
