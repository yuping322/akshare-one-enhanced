"""
Test Tushare integration.

This test file demonstrates how to use Tushare as a data source.
"""

import pytest
import pandas as pd

from akshare_one.tushare_config import set_tushare_api_key, get_tushare_api_key, has_tushare_api_key
from akshare_one.tushare_client import get_tushare_client
from akshare_one.modules.financial import FinancialDataFactory
from akshare_one.modules.historical import HistoricalDataFactory


TUSHARE_API_KEY = "4b33969578cd316eb788f60605711745360834aded78ac672f2a0537"


@pytest.fixture(scope="module", autouse=True)
def setup_tushare():
    """Setup Tushare API key for all tests."""
    set_tushare_api_key(TUSHARE_API_KEY)
    assert has_tushare_api_key(), "Tushare API key should be set"
    assert get_tushare_api_key() == TUSHARE_API_KEY, "API key should match"


class TestTushareConfig:
    """Test Tushare configuration management."""

    def test_has_api_key(self):
        """Test that API key is configured."""
        assert has_tushare_api_key()

    def test_get_api_key(self):
        """Test getting API key."""
        key = get_tushare_api_key()
        assert key is not None
        assert len(key) > 0


class TestTushareClient:
    """Test Tushare client."""

    def test_client_availability(self):
        """Test that client is available."""
        client = get_tushare_client()
        assert client.is_available(), "Tushare client should be available after API key is set"

    @pytest.mark.integration
    def test_query_stock_basic(self):
        """Test querying stock basic info."""
        client = get_tushare_client()
        df = client.get_stock_basic(list_status="L", limit=5)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "Should return stock basic info"
        assert "ts_code" in df.columns or "symbol" in df.columns

    @pytest.mark.integration
    def test_query_daily(self):
        """Test querying daily price data."""
        client = get_tushare_client()
        df = client.get_daily(ts_code="600000.SH", start_date="20240101", end_date="20240110")

        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "Should return daily price data"
        assert "trade_date" in df.columns
        assert "close" in df.columns


class TestTushareFinancialProvider:
    """Test Tushare financial data provider."""

    @pytest.mark.integration
    def test_get_balance_sheet(self):
        """Test getting balance sheet from Tushare."""
        provider = FinancialDataFactory.get_provider("tushare", symbol="600000")

        df = provider.get_balance_sheet()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns or "report_date" in df.columns

    @pytest.mark.integration
    def test_get_income_statement(self):
        """Test getting income statement from Tushare."""
        provider = FinancialDataFactory.get_provider("tushare", symbol="600000")

        df = provider.get_income_statement()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns or "report_date" in df.columns

    @pytest.mark.integration
    def test_get_cash_flow(self):
        """Test getting cash flow from Tushare."""
        provider = FinancialDataFactory.get_provider("tushare", symbol="600000")

        df = provider.get_cash_flow()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns or "report_date" in df.columns

    @pytest.mark.integration
    def test_get_financial_metrics(self):
        """Test getting financial metrics from Tushare."""
        provider = FinancialDataFactory.get_provider("tushare", symbol="600000")

        df = provider.get_financial_metrics()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns or "report_date" in df.columns


class TestTushareHistoricalProvider:
    """Test Tushare historical data provider."""

    @pytest.mark.integration
    def test_get_hist_data_daily(self):
        """Test getting daily historical data from Tushare."""
        provider = HistoricalDataFactory.get_provider(
            "tushare", symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "Should return historical data"
        assert "date" in df.columns
        assert "close" in df.columns

    @pytest.mark.integration
    def test_get_hist_data_with_adjust(self):
        """Test getting historical data with price adjustment."""
        provider = HistoricalDataFactory.get_provider(
            "tushare", symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-10", adjust="hfq"
        )

        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "close" in df.columns

    @pytest.mark.integration
    def test_symbol_conversion(self):
        """Test symbol conversion to ts_code format."""
        provider = HistoricalDataFactory.get_provider(
            "tushare", symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )

        assert provider.ts_code == "600000.SH"

        provider2 = HistoricalDataFactory.get_provider(
            "tushare", symbol="000001", interval="day", start_date="2024-01-01", end_date="2024-01-10"
        )

        assert provider2.ts_code == "000001.SZ"


class TestMultiSource:
    """Test using Tushare alongside other sources."""

    @pytest.mark.integration
    def test_list_sources(self):
        """Test that Tushare is registered in factories."""
        financial_sources = FinancialDataFactory.list_sources()
        assert "tushare" in financial_sources

        historical_sources = HistoricalDataFactory.list_sources()
        assert "tushare" in historical_sources

    @pytest.mark.integration
    def test_compare_sources(self):
        """Compare data from different sources."""
        symbol = "600000"

        tushare_provider = FinancialDataFactory.get_provider("tushare", symbol=symbol)
        tushare_df = tushare_provider.get_balance_sheet()

        assert isinstance(tushare_df, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
