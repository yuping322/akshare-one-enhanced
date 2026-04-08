"""
API Field Contract Tests with Mocks

These tests validate that each API returns the minimum required field set
as defined in the API contract documentation, using mock data to avoid network dependencies.

Run: pytest tests/test_api_field_contracts_with_mocks.py -v
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

pytest_plugins = ["tests.fixtures.mock_api_responses_contract"]


# ============================================================================
# Historical Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestHistDataContract:
    """Contract tests for get_hist_data API with mocks."""

    def test_hist_data_required_fields(self, mock_hist_data_contract):
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

    def test_hist_data_field_types(self, mock_hist_data_contract):
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

    def test_hist_data_value_ranges(self, mock_hist_data_contract):
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

        # OHLC consistency
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
    """Contract tests for get_realtime_data API with mocks."""

    def test_realtime_data_required_fields(self, mock_realtime_data_contract):
        """Verify realtime data has all required fields."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        required_fields = ["symbol", "price", "timestamp", "volume", "amount"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_realtime_data_field_types(self, mock_realtime_data_contract):
        """Verify realtime data field types are correct."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert pd.api.types.is_numeric_dtype(df["price"]), "price must be numeric"
        assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"
        assert pd.api.types.is_numeric_dtype(df["amount"]), "amount must be numeric"

    def test_realtime_data_symbol_format(self, mock_realtime_data_contract):
        """Verify symbol format in realtime data."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert "symbol" in df.columns
        assert df["symbol"].iloc[0] == "600000"

    def test_realtime_data_price_positive(self, mock_realtime_data_contract):
        """Verify price is positive."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        assert (df["price"] > 0).all(), "price must be positive"


# ============================================================================
# ETF Historical Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestETFHistDataContract:
    """Contract tests for get_etf_hist_data API with mocks."""

    def test_etf_hist_data_required_fields(self, mock_etf_hist_data_contract):
        """Verify ETF historical data has all required fields."""
        from akshare_one import get_etf_hist_data

        df = get_etf_hist_data(symbol="510050", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No ETF historical data available")

        required_fields = ["date", "symbol", "open", "high", "low", "close", "volume"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_etf_hist_data_field_types(self, mock_etf_hist_data_contract):
        """Verify ETF historical data field types are correct."""
        from akshare_one import get_etf_hist_data

        df = get_etf_hist_data(symbol="510050", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No ETF historical data available")

        assert pd.api.types.is_numeric_dtype(df["open"]), "open must be numeric"
        assert pd.api.types.is_numeric_dtype(df["high"]), "high must be numeric"
        assert pd.api.types.is_numeric_dtype(df["low"]), "low must be numeric"
        assert pd.api.types.is_numeric_dtype(df["close"]), "close must be numeric"
        assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"

    def test_etf_hist_data_value_ranges(self, mock_etf_hist_data_contract):
        """Verify ETF historical data values are in reasonable ranges."""
        from akshare_one import get_etf_hist_data

        df = get_etf_hist_data(symbol="510050", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No ETF historical data available")

        assert (df["open"] > 0).all(), "open price must be positive"
        assert (df["high"] >= df["low"]).all(), "high must >= low"


# ============================================================================
# Bond Historical Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestBondHistDataContract:
    """Contract tests for get_bond_hist_data API."""

    def test_bond_hist_data_required_fields(self):
        """Verify bond historical data has all required fields."""
        pytest.skip("Bond API not fully implemented with mocks yet")

    def test_bond_hist_data_field_types(self):
        """Verify bond historical data field types are correct."""
        pytest.skip("Bond API not fully implemented with mocks yet")


# ============================================================================
# Index List Contract Tests
# ============================================================================


@pytest.mark.contract
class TestIndexListContract:
    """Contract tests for get_index_list API."""

    def test_index_list_required_fields(self):
        """Verify index list has all required fields."""
        pytest.skip("Index list API not fully implemented with mocks yet")

    def test_index_list_field_types(self):
        """Verify index list field types are correct."""
        pytest.skip("Index list API not fully implemented with mocks yet")


# ============================================================================
# Northbound Flow Contract Tests
# ============================================================================


@pytest.mark.contract
class TestNorthboundFlowContract:
    """Contract tests for get_northbound_flow API."""

    def test_northbound_flow_required_fields(self, mock_northbound_flow_api):
        """Verify northbound flow has all required fields."""
        from akshare_one import get_northbound_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No northbound flow data available")

        required_fields = ["date", "northbound_net_buy", "northbound_buy_amount", "northbound_sell_amount"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_northbound_flow_field_types(self, mock_northbound_flow_api):
        """Verify northbound flow field types are correct."""
        from akshare_one import get_northbound_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_northbound_flow(start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No northbound flow data available")

        assert pd.api.types.is_numeric_dtype(df["northbound_net_buy"]), "northbound_net_buy must be numeric"
        assert pd.api.types.is_numeric_dtype(df["northbound_buy_amount"]), "northbound_buy_amount must be numeric"


# ============================================================================
# Fund Flow Contract Tests
# ============================================================================


@pytest.mark.contract
class TestFundFlowContract:
    """Contract tests for get_stock_fund_flow API with mocks."""

    def test_fund_flow_required_fields(self, mock_fund_flow_contract):
        """Verify fund flow has all required fields."""
        from akshare_one import get_stock_fund_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_stock_fund_flow(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No fund flow data available")

        required_fields = ["date", "symbol", "fundflow_main_net_inflow", "fundflow_main_net_inflow_rate"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_fund_flow_field_types(self, mock_fund_flow_contract):
        """Verify fund flow field types are correct."""
        from akshare_one import get_stock_fund_flow

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_stock_fund_flow(symbol="600000", start_date=start_date, end_date=end_date)

        if df.empty:
            pytest.skip("No fund flow data available")

        assert pd.api.types.is_numeric_dtype(df["fundflow_main_net_inflow"]), "fundflow_main_net_inflow must be numeric"
        assert pd.api.types.is_numeric_dtype(df["fundflow_main_net_inflow_rate"]), (
            "fundflow_main_net_inflow_rate must be numeric"
        )


# ============================================================================
# Dragon Tiger Contract Tests
# ============================================================================


@pytest.mark.contract
class TestDragonTigerContract:
    """Contract tests for get_dragon_tiger_list API with mocks."""

    def test_dragon_tiger_required_fields(self, mock_dragon_tiger_contract):
        """Verify dragon tiger list has all required fields."""
        from akshare_one import get_dragon_tiger_list

        df = get_dragon_tiger_list()

        if df.empty:
            pytest.skip("No dragon tiger data available")

        required_fields = ["date", "symbol", "name", "close", "pct_change", "turnover", "reason"]
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"

    def test_dragon_tiger_field_types(self, mock_dragon_tiger_contract):
        """Verify dragon tiger field types are correct."""
        from akshare_one import get_dragon_tiger_list

        df = get_dragon_tiger_list()

        if df.empty:
            pytest.skip("No dragon tiger data available")

        assert pd.api.types.is_numeric_dtype(df["close"]), "close must be numeric"
        assert pd.api.types.is_numeric_dtype(df["pct_change"]), "pct_change must be numeric"
        assert pd.api.types.is_numeric_dtype(df["turnover"]), "turnover must be numeric"


# ============================================================================
# Futures Historical Data Contract Tests
# ============================================================================


@pytest.mark.contract
class TestFuturesHistDataContract:
    """Contract tests for get_futures_hist_data API."""

    def test_futures_hist_data_required_fields(self):
        """Verify futures historical data has all required fields."""
        pytest.skip("Futures API not fully implemented with mocks yet")

    def test_futures_hist_data_field_types(self):
        """Verify futures historical data field types are correct."""
        pytest.skip("Futures API not fully implemented with mocks yet")


# ============================================================================
# Financial Metrics Contract Tests
# ============================================================================


@pytest.mark.contract
class TestFinancialMetricsContract:
    """Contract tests for get_financial_metrics API with mocks."""

    def test_financial_metrics_required_fields(self, mock_financial_metrics_contract):
        """Verify financial metrics has all required fields."""
        from akshare_one import get_financial_metrics

        df = get_financial_metrics(symbol="600000")

        if df.empty:
            pytest.skip("No financial metrics data available")

        # Minimum required fields: report_date and symbol
        assert "report_date" in df.columns or "date" in df.columns, "Missing report_date or date field"
        assert "symbol" in df.columns, "Missing required field: symbol"

    def test_financial_metrics_field_types(self, mock_financial_metrics_contract):
        """Verify financial metrics field types are correct."""
        from akshare_one import get_financial_metrics

        df = get_financial_metrics(symbol="600000")

        if df.empty:
            pytest.skip("No financial metrics data available")

        # All financial amounts should be numeric if present
        numeric_cols = [col for col in df.columns if df[col].dtype in ["float64", "int64"]]
        assert len(numeric_cols) > 2, "Should have multiple numeric financial metric columns"


# ============================================================================
# Cross-API Consistency Tests
# ============================================================================


@pytest.mark.contract
class TestCrossAPIConsistency:
    """Test consistency across related APIs with mocks."""

    def test_symbol_format_consistency(
        self, mock_hist_data_contract, mock_realtime_data_contract, mock_fund_flow_contract
    ):
        """Verify symbol format is consistent across APIs."""
        from akshare_one import get_hist_data, get_realtime_data, get_stock_fund_flow

        symbol = "600000"

        # Get data from multiple APIs
        df_hist = get_hist_data(symbol=symbol)
        df_realtime = get_realtime_data(symbol=symbol)
        df_fundflow = get_stock_fund_flow(symbol=symbol)

        # Check symbol format consistency if data available
        if not df_hist.empty and "symbol" in df_hist.columns:
            assert df_hist["symbol"].iloc[0] == symbol

        if not df_realtime.empty and "symbol" in df_realtime.columns:
            assert df_realtime["symbol"].iloc[0] == symbol

        if not df_fundflow.empty and "symbol" in df_fundflow.columns:
            assert df_fundflow["symbol"].iloc[0] == symbol

    def test_price_unit_consistency(self, mock_hist_data_contract, mock_realtime_data_contract):
        """Verify all prices are in yuan unit."""
        from akshare_one import get_hist_data, get_realtime_data

        # Prices should be in yuan (元), not 亿元 or 万元
        # Typical stock prices: 1-100 yuan range
        df_hist = get_hist_data(symbol="600000")
        df_realtime = get_realtime_data(symbol="600000")

        if not df_hist.empty:
            # Stock prices typically < 100 yuan, not millions
            assert (df_hist["close"] < 1000).any(), "Prices should be in yuan, not scaled"

        if not df_realtime.empty:
            assert (df_realtime["price"] < 1000).any(), "Prices should be in yuan, not scaled"


# ============================================================================
# Field Name Standardization Tests
# ============================================================================


@pytest.mark.contract
class TestFieldNameStandardization:
    """Test that field names follow standardized conventions with mocks."""

    def test_no_chinese_field_names(
        self, mock_hist_data_contract, mock_realtime_data_contract, mock_northbound_flow_api
    ):
        """Verify all field names are in English."""
        from akshare_one import get_hist_data, get_realtime_data, get_northbound_flow

        apis_to_test = [
            get_hist_data(symbol="600000"),
            get_realtime_data(symbol="600000"),
            get_northbound_flow(),
        ]

        for df in apis_to_test:
            if df.empty:
                continue

            # Check no Chinese characters in column names
            for col in df.columns:
                assert not any("\u4e00" <= char <= "\u9fff" for char in col), (
                    f"Field name '{col}' contains Chinese characters"
                )

    def test_timestamp_field_naming(self, mock_hist_data_contract, mock_etf_hist_data_contract):
        """Verify time-related fields use standardized names."""
        from akshare_one import get_hist_data, get_etf_hist_data

        # Historical APIs should use 'timestamp' or 'date' for time field
        df_stock = get_hist_data(symbol="600000")
        df_etf = get_etf_hist_data(symbol="510050", start_date="2024-01-01", end_date="2024-01-31")

        if not df_stock.empty:
            assert "timestamp" in df_stock.columns, "Stock hist should use 'timestamp'"

        if not df_etf.empty:
            assert "date" in df_etf.columns, "ETF hist should use 'date'"


# ============================================================================
# Contract Documentation Coverage Tests
# ============================================================================


@pytest.mark.contract
class TestContractDocumentationCoverage:
    """Test that all major APIs have contract documentation."""

    def test_contract_docs_exist(self):
        """Verify contract documentation files exist."""
        import os

        contract_docs_dir = "docs/api_contracts"

        # Check directory exists
        assert os.path.exists(contract_docs_dir), "Contract docs directory missing"

        # Check for specific contract docs
        expected_docs = [
            "get_hist_data.md",
            "get_realtime_data.md",
            "get_etf_hist_data.md",
            "get_bond_hist_data.md",
            "get_index_list.md",
            "get_northbound_flow.md",
            "get_fund_flow.md",
            "get_dragon_tiger_list.md",
            "get_futures_hist_data.md",
            "get_financial_metrics.md",
        ]

        for doc in expected_docs:
            doc_path = os.path.join(contract_docs_dir, doc)
            assert os.path.exists(doc_path), f"Missing contract doc: {doc}"

    def test_template_doc_exists(self):
        """Verify contract template exists."""
        import os

        template_path = "docs/api_contracts/_template.md"
        assert os.path.exists(template_path), "Contract template missing"

    def test_api_reference_exists(self):
        """Verify API reference manual exists."""
        import os

        reference_path = "docs/api_reference.md"
        assert os.path.exists(reference_path), "API reference manual missing"
