"""
Integration tests for Northbound module.

These tests verify end-to-end functionality with real data sources.
Run with: pytest tests/test_northbound_integration.py -v -m integration
"""

from datetime import datetime, timedelta

import pytest

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from tests.utils.integration_helpers import (
    DataFrameValidator,
    integration_rate_limiter,
    skip_if_no_network,
)

# ============================================================================
# Integration Tests - Real Data Fetching
# ============================================================================


@pytest.mark.integration
class TestNorthboundFlowIntegration:
    """Integration tests for northbound flow data."""

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_all_market(self):
        """Test fetching northbound flow for all markets."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["date", "market", "northbound_net_buy"])
        assert df["date"].dtype == "object", "date should be string type"
        assert df["market"].dtype == "object", "market should be string type"

        assert all(df["market"] == "all"), "All records should have market='all'"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_sh_market(self):
        """Test fetching northbound flow for Shanghai market."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="sh")

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["date", "market", "northbound_net_buy"])

        assert all(df["market"] == "sh"), "All records should have market='sh'"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_sz_market(self):
        """Test fetching northbound flow for Shenzhen market."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="sz")

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["date", "market", "northbound_net_buy"])

        assert all(df["market"] == "sz"), "All records should have market='sz'"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_with_date_range(self):
        """Test date range filtering in northbound flow."""
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")

        if not df.empty:
            assert all(df["date"] >= start_date), "All dates should be >= start_date"
            assert all(df["date"] <= end_date), "All dates should be <= end_date"
            assert df["date"].dtype == "object", "date should be string type"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_data_value_range(self):
        """Test numerical value ranges in northbound flow data."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")

        if not df.empty and "northbound_net_buy" in df.columns:
            assert df["northbound_net_buy"].dtype in ["float64", "int64", "object"]

            if "northbound_buy_amount" in df.columns:
                assert all(df["northbound_buy_amount"] >= 0)

            if "northbound_sell_amount" in df.columns:
                assert all(df["northbound_sell_amount"] >= 0)

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_empty_data_handling(self):
        """Test handling of empty data from API."""
        df = get_northbound_flow(start_date="2030-01-01", end_date="2030-01-10", market="all")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "market" in df.columns


@pytest.mark.integration
class TestNorthboundHoldingsIntegration:
    """Integration tests for northbound holdings data."""

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_specific_stock(self):
        """Test fetching northbound holdings for a specific stock."""
        symbol = "600000"
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_holdings(symbol=symbol, start_date=start_date, end_date=end_date)

        DataFrameValidator.validate_required_columns(df, ["date", "symbol", "holdings_shares"])

        if not df.empty:
            assert all(df["symbol"] == symbol), f"All records should have symbol={symbol}"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_all_stocks(self):
        """Test fetching northbound holdings for all stocks."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_holdings(symbol=None, start_date=start_date, end_date=end_date)

        DataFrameValidator.validate_required_columns(df, ["symbol", "holdings_shares"])

        if not df.empty and "symbol" in df.columns:
            assert all(len(str(s)) == 6 for s in df["symbol"]), "All symbols should be 6 digits"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_basic(self):
        """Test basic holdings data structure."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        df = get_northbound_holdings(symbol=None, start_date=start_date, end_date=end_date)

        if not df.empty:
            DataFrameValidator.validate_required_columns(df, ["symbol"])
            assert df["symbol"].dtype == "object", "symbol should be string type"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_with_symbol(self):
        """Test holdings data for specific symbol with validation."""
        symbol = "600519"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

        df = get_northbound_holdings(symbol=symbol, start_date=start_date, end_date=end_date)

        if not df.empty:
            DataFrameValidator.validate_required_columns(df, ["symbol", "holdings_shares"])
            assert all(df["symbol"] == symbol)

            if "holdings_ratio" in df.columns:
                assert all(df["holdings_ratio"] >= 0), "Holdings ratio should be >= 0"


@pytest.mark.integration
class TestNorthboundTopStocksIntegration:
    """Integration tests for northbound top stocks."""

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_all_market(self):
        """Test fetching top northbound stocks for all markets."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df = get_northbound_top_stocks(date=date, market="all", top_n=20)

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["rank", "symbol", "name"])

        assert df["rank"].iloc[0] == 1, "First rank should be 1"
        assert len(df) <= 20, "Should return at most 20 records"

        # Validate symbols are 6 digits
        assert all(len(str(s)) == 6 for s in df["symbol"]), "All symbols should be 6 digits"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_sh_market(self):
        """Test fetching top northbound stocks for Shanghai market."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df = get_northbound_top_stocks(date=date, market="sh", top_n=10)

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["rank", "symbol", "name"])

        # Validate Shanghai stocks (start with 6)
        if not df.empty:
            assert all(str(s).startswith("6") for s in df["symbol"]), "Shanghai stocks should start with 6"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_sz_market(self):
        """Test fetching top northbound stocks for Shenzhen market."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df = get_northbound_top_stocks(date=date, market="sz", top_n=10)

        assert not df.empty, "DataFrame should not be empty"
        DataFrameValidator.validate_required_columns(df, ["rank", "symbol", "name"])

        if not df.empty:
            assert all(str(s).startswith(("0", "3")) for s in df["symbol"]), "Shenzhen stocks should start with 0 or 3"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_basic(self):
        """Test basic top stocks data structure."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df = get_northbound_top_stocks(date=date, market="all", top_n=10)

        if not df.empty:
            DataFrameValidator.validate_required_columns(df, ["rank", "symbol", "name"])
            assert df["rank"].iloc[0] == 1
            assert df["symbol"].dtype == "object", "symbol should be string type"

    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_with_market_filter(self):
        """Test top stocks with market filter validation."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df_sh = get_northbound_top_stocks(date=date, market="sh", top_n=5)
        if not df_sh.empty:
            assert all(str(s).startswith("6") for s in df_sh["symbol"])

        df_sz = get_northbound_top_stocks(date=date, market="sz", top_n=5)
        if not df_sz.empty:
            assert all(str(s).startswith(("0", "3")) for s in df_sz["symbol"])

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_data_field_validation(self):
        """Test data field validation across all functions."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        df_flow = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")
        if not df_flow.empty:
            DataFrameValidator.validate_required_columns(df_flow, ["date", "market"])

        df_holdings = get_northbound_holdings(symbol="600000", start_date=start_date, end_date=end_date)
        if not df_holdings.empty:
            DataFrameValidator.validate_required_columns(df_holdings, ["symbol"])

        df_top = get_northbound_top_stocks(date=end_date, market="all", top_n=5)
        if not df_top.empty:
            DataFrameValidator.validate_required_columns(df_top, ["rank", "symbol"])


# ============================================================================
# Integration Tests - JSON Compatibility
# ============================================================================


@pytest.mark.integration
class TestJSONCompatibilityIntegration:
    """Test JSON compatibility with real data."""

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_flow_json_serializable(self):
        """Test that northbound flow data can be serialized to JSON."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")

        json_str = df.to_json(orient="records")
        assert json_str is not None
        assert len(json_str) > 0

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_top_stocks_json_serializable(self):
        """Test that northbound top stocks data can be serialized to JSON."""
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        df = get_northbound_top_stocks(date=date, market="all", top_n=10)

        json_str = df.to_json(orient="records")
        assert json_str is not None
        assert len(json_str) > 0

    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_json_compatibility(self):
        """Test JSON compatibility across all functions."""
        import json

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

        df_flow = get_northbound_flow(start_date=start_date, end_date=end_date, market="all")
        json_flow = df_flow.to_json(orient="records")
        records_flow = json.loads(json_flow)
        assert isinstance(records_flow, list)

        df_top = get_northbound_top_stocks(date=end_date, market="all", top_n=5)
        json_top = df_top.to_json(orient="records")
        records_top = json.loads(json_top)
        assert isinstance(records_top, list)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
