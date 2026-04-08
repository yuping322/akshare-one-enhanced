"""
Unit tests for Northbound module.

This test suite covers:
1. Unit tests for all 3 public functions
2. Parameter validation tests
3. JSON compatibility tests
4. Provider functionality tests
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.northbound import (
    NorthboundFactory,
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from akshare_one.modules.northbound.base import NorthboundProvider
from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider

# ============================================================================
# Unit Tests - Provider Basics
# ============================================================================


class TestProviderBasics:
    """Test basic provider functionality."""

    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyNorthboundProvider()
        assert provider is not None
        assert isinstance(provider, NorthboundProvider)

    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyNorthboundProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"
        assert "data_type" in metadata
        assert metadata["data_type"] == "northbound"
        assert "update_frequency" in metadata
        assert metadata["update_frequency"] == "daily"
        assert "delay_minutes" in metadata
        assert metadata["delay_minutes"] == 1440  # T+1


# ============================================================================
# Unit Tests - Parameter Validation
# ============================================================================


class TestParameterValidation:
    """Test parameter validation for all functions."""

    def test_valid_date_range(self):
        """Test with valid date range."""
        provider = EastmoneyNorthboundProvider()
        # Should not raise
        provider.validate_date_range("2024-01-01", "2024-01-31")

    def test_invalid_date_format(self):
        """Test with invalid date formats."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="Invalid.*format"):
            provider.validate_date_range("2024/01/01", "2024-01-31")

        with pytest.raises(ValueError, match="Invalid.*format"):
            provider.validate_date_range("2024-01-01", "invalid")

    def test_invalid_date_range_order(self):
        """Test with start_date > end_date."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="start_date.*must be.*end_date"):
            provider.validate_date_range("2024-01-31", "2024-01-01")

    def test_valid_symbol(self):
        """Test with valid 6-digit symbol."""
        provider = EastmoneyNorthboundProvider()
        # Should not raise
        provider.validate_symbol("600000")
        provider.validate_symbol("000001")

    def test_invalid_symbol_format(self):
        """Test with invalid symbol formats."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol("INVALID")

        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol("12345")

    def test_invalid_market_parameter(self):
        """Test with invalid market parameter."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="Invalid market"):
            provider.get_northbound_flow("2024-01-01", "2024-01-31", "invalid")

    def test_invalid_top_n_parameter(self):
        """Test with invalid top_n parameter."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_northbound_top_stocks("2024-01-01", "all", -1)

        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_northbound_top_stocks("2024-01-01", "all", 0)


# ============================================================================
# Unit Tests - Factory Pattern
# ============================================================================


class TestFactory:
    """Test factory pattern implementation."""

    def test_factory_get_provider(self):
        """Test factory can create provider."""
        provider = NorthboundFactory.get_provider("eastmoney")
        assert isinstance(provider, EastmoneyNorthboundProvider)

    def test_factory_unsupported_source(self):
        """Test factory raises error for unsupported source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            NorthboundFactory.get_provider("unsupported")

    def test_factory_list_sources(self):
        """Test factory can list available sources."""
        sources = NorthboundFactory.list_sources()
        assert isinstance(sources, list)
        assert "eastmoney" in sources

    def test_factory_register_provider(self):
        """Test factory can register new provider."""

        class CustomProvider(NorthboundProvider):
            def get_source_name(self):
                return "custom"

            def get_data_type(self):
                return "northbound"

            def fetch_data(self):
                return pd.DataFrame()

            def get_northbound_flow(self, start_date, end_date, market):
                return pd.DataFrame()

            def get_northbound_holdings(self, symbol, start_date, end_date):
                return pd.DataFrame()

            def get_northbound_top_stocks(self, date, market, top_n):
                return pd.DataFrame()

        NorthboundFactory.register_provider("custom", CustomProvider)
        assert "custom" in NorthboundFactory.list_sources()

        provider = NorthboundFactory.get_provider("custom")
        assert isinstance(provider, CustomProvider)

    def test_factory_register_invalid_provider(self):
        """Test factory rejects invalid provider class."""

        class InvalidProvider:
            pass

        with pytest.raises(TypeError, match="must inherit from NorthboundProvider"):
            NorthboundFactory.register_provider("invalid", InvalidProvider)


# ============================================================================
# Unit Tests - JSON Compatibility
# ============================================================================


class TestJSONCompatibility:
    """Test JSON compatibility of returned data."""

    def test_ensure_json_compatible_handles_nan(self):
        """Test that NaN values are replaced with None."""
        provider = EastmoneyNorthboundProvider()

        df = pd.DataFrame({"date": ["2024-01-01"], "value": [np.nan]})

        result = provider.ensure_json_compatible(df)
        assert result["value"][0] is None

    def test_ensure_json_compatible_handles_infinity(self):
        """Test that Infinity values are replaced with None."""
        provider = EastmoneyNorthboundProvider()

        df = pd.DataFrame({"date": ["2024-01-01"], "value": [np.inf]})

        result = provider.ensure_json_compatible(df)
        assert result["value"][0] is None

    def test_ensure_json_compatible_handles_datetime(self):
        """Test that datetime columns are converted to strings."""
        provider = EastmoneyNorthboundProvider()

        df = pd.DataFrame({"date": [pd.Timestamp("2024-01-01")]})

        result = provider.ensure_json_compatible(df)
        assert result["date"][0] == "2024-01-01"
        assert isinstance(result["date"][0], str)

    def test_ensure_json_compatible_handles_symbol(self):
        """Test that symbol columns preserve leading zeros."""
        provider = EastmoneyNorthboundProvider()

        df = pd.DataFrame({"symbol": ["600000", "000001"]})

        result = provider.ensure_json_compatible(df)
        assert result["symbol"][0] == "600000"
        assert result["symbol"][1] == "000001"
        assert isinstance(result["symbol"][0], str)


# ============================================================================
# Unit Tests - Empty Results
# ============================================================================


class TestEmptyResults:
    """Test handling of empty results."""

    def test_create_empty_dataframe(self):
        """Test creating empty DataFrame with correct columns."""
        provider = EastmoneyNorthboundProvider()

        columns = ["date", "market", "net_buy"]
        df = provider.create_empty_dataframe(columns)

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == columns

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow_empty_result(self, mock_ak):
        """Test get_northbound_flow returns empty DataFrame with correct structure."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-01", "2024-01-31", "all")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        expected_columns = [
            "date",
            "market",
            "northbound_net_buy",
            "northbound_buy_amount",
            "northbound_sell_amount",
            "balance",
        ]
        assert list(result.columns) == expected_columns


# ============================================================================
# Unit Tests - Northbound Flow (Eastmoney Provider)
# ============================================================================


class TestNorthboundFlowEastmoney:
    """Test get_northbound_flow for eastmoney provider with comprehensive coverage."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow_all_market(self, mock_ak):
        """Test fetching northbound flow for all markets."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "当日成交净买额": [50.25, -30.18, 42.56],
                "买入成交额": [150.50, 120.30, 145.60],
                "卖出成交额": [100.25, 150.48, 103.04],
                "当日余额": [1550.25, 1520.07, 1562.63],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-17", "all")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "date" in result.columns
        assert "market" in result.columns
        assert "northbound_net_buy" in result.columns
        assert "northbound_buy_amount" in result.columns
        assert "northbound_sell_amount" in result.columns
        assert "balance" in result.columns

        assert all(result["market"] == "all")
        assert len(result) == 3

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow_sh_market(self, mock_ak):
        """Test fetching northbound flow for Shanghai market."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "当日成交净买额": [30.50, 25.30],
                "买入成交额": [100.50, 95.30],
                "卖出成交额": [70.00, 70.00],
                "当日余额": [1200.50, 1225.80],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-16", "sh")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(result["market"] == "sh")

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow_sz_market(self, mock_ak):
        """Test fetching northbound flow for Shenzhen market."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "当日成交净买额": [20.50, 15.30],
                "买入成交额": [80.50, 75.30],
                "卖出成交额": [60.00, 60.00],
                "当日余额": [800.50, 815.80],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-16", "sz")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(result["market"] == "sz")

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow_with_date_range(self, mock_ak):
        """Test date range filtering in northbound flow."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-10", "2024-01-15", "2024-01-20", "2024-01-25"],
                "当日成交净买额": [10.0, 20.0, 30.0, 40.0],
                "买入成交额": [100.0, 150.0, 200.0, 250.0],
                "卖出成交额": [90.0, 130.0, 170.0, 210.0],
                "当日余额": [1000.0, 1020.0, 1050.0, 1090.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-12", "2024-01-22", "all")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert all(result["date"] >= "2024-01-12")
        assert all(result["date"] <= "2024-01-22")

    @patch("akshare.stock_hsgt_hist_em")
    def test_northbound_data_value_range(self, mock_ak):
        """Test numerical value ranges in northbound flow data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        assert not result.empty
        expected_net_buy = 50.25 * 100000000
        assert abs(result["northbound_net_buy"].iloc[0] - expected_net_buy) < 1

        expected_buy_amount = 150.50 * 100000000
        assert abs(result["northbound_buy_amount"].iloc[0] - expected_buy_amount) < 1

    @patch("akshare.stock_hsgt_hist_em")
    def test_northbound_empty_data_handling(self, mock_ak):
        """Test handling of empty DataFrame from API."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-01", "2024-01-31", "all")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "date" in result.columns
        assert "market" in result.columns


# ============================================================================
# Unit Tests - Northbound Holdings (Eastmoney Provider)
# ============================================================================


class TestNorthboundHoldingsEastmoney:
    """Test get_northbound_holdings for eastmoney provider."""

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_get_northbound_holdings_basic(self, mock_ak):
        """Test fetching northbound holdings for all stocks."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "000001"],
                "名称": ["浦发银行", "平安银行"],
                "持股日期": ["2024-01-15", "2024-01-15"],
                "持股数量(股)": [15000000, 12000000],
                "持股市值(元)": [225000000, 180000000],
                "持股占比(%)": [3.5, 4.2],
                "持股数量增减": [500000, 450000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings(None, "2024-01-01", "2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "holdings_shares" in result.columns
        assert "holdings_value" in result.columns
        assert "holdings_ratio" in result.columns

    @patch("akshare.stock_hsgt_individual_em")
    def test_get_northbound_holdings_with_symbol(self, mock_ak):
        """Test fetching northbound holdings for specific stock."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "持股数量": [15000000, 15500000],
                "持股市值": [225000000, 232500000],
                "持股占比": [3.5, 3.6],
                "持股变化": [500000, 500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("600000", "2024-01-15", "2024-01-16")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(result["symbol"] == "600000")
        assert "holdings_shares" in result.columns

    @patch("akshare.stock_hsgt_individual_em")
    def test_northbound_holdings_empty_data_handling(self, mock_ak):
        """Test handling empty holdings data."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("600000", "2024-01-01", "2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "symbol" in result.columns
        assert "holdings_shares" in result.columns


# ============================================================================
# Unit Tests - Northbound Top Stocks (Eastmoney Provider)
# ============================================================================


class TestNorthboundTopStocksEastmoney:
    """Test get_northbound_top_stocks for eastmoney provider."""

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_get_northbound_top_stocks_basic(self, mock_ak):
        """Test fetching top northbound stocks."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 5)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "rank" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "northbound_net_buy" in result.columns
        assert "holdings_shares" in result.columns
        assert "holdings_ratio" in result.columns
        assert len(result) <= 5
        assert result["rank"].iloc[0] == 1

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_get_northbound_top_stocks_with_market_filter(self, mock_ak):
        """Test filtering top stocks by market."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()

        result_sh = provider.get_northbound_top_stocks("2024-01-15", "sh", 10)
        if not result_sh.empty:
            assert all(str(s).startswith("6") for s in result_sh["symbol"])

        result_sz = provider.get_northbound_top_stocks("2024-01-15", "sz", 10)
        if not result_sz.empty:
            assert all(str(s).startswith(("0", "3")) for s in result_sz["symbol"])

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_northbound_top_stocks_empty_data_handling(self, mock_ak):
        """Test handling empty top stocks data."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 10)

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "rank" in result.columns
        assert "symbol" in result.columns


# ============================================================================
# Unit Tests - Data Field Validation
# ============================================================================


class TestNorthboundFieldValidation:
    """Test data field validation and standardization."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_northbound_data_field_validation(self, mock_ak):
        """Test that output fields are correctly standardized."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        assert "date" in result.columns
        assert "market" in result.columns
        assert "northbound_net_buy" in result.columns
        assert "northbound_buy_amount" in result.columns
        assert "northbound_sell_amount" in result.columns
        assert "balance" in result.columns

        assert pd.api.types.is_string_dtype(result["date"])
        assert pd.api.types.is_string_dtype(result["market"])

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_holdings_field_validation(self, mock_ak):
        """Test holdings data field validation."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "持股日期": ["2024-01-15"],
                "持股数量(股)": [15000000],
                "持股市值(元)": [225000000],
                "持股占比(%)": [3.5],
                "持股数量增减": [500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings(None, "2024-01-01", "2024-01-31")

        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "holdings_shares" in result.columns
        assert "holdings_value" in result.columns
        assert "holdings_ratio" in result.columns

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_stocks_field_validation(self, mock_ak):
        """Test top stocks data field validation."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "今日持股-股数": [150000000],
                "今日持股-市值": [2250000000],
                "今日持股-占流通股比": [5.5],
                "5日增持估计-市值": [112500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 10)

        assert "rank" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "holdings_shares" in result.columns
        assert "holdings_ratio" in result.columns


# ============================================================================
# Unit Tests - JSON Compatibility
# ============================================================================


class TestNorthboundJSONCompatibility:
    """Test JSON compatibility of returned data."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_northbound_json_compatibility(self, mock_ak):
        """Test that northbound flow data can be serialized to JSON."""
        import json

        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        json_str = result.to_json(orient="records")
        assert json_str is not None
        assert len(json_str) > 0

        records = json.loads(json_str)
        assert isinstance(records, list)
        assert len(records) == len(result)

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_holdings_json_compatibility(self, mock_ak):
        """Test that holdings data can be serialized to JSON."""
        import json

        mock_df = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "持股日期": ["2024-01-15"],
                "持股数量(股)": [15000000],
                "持股市值(元)": [225000000],
                "持股占比(%)": [3.5],
                "持股数量增减": [500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings(None, "2024-01-01", "2024-01-31")

        json_str = result.to_json(orient="records")
        assert json_str is not None

        records = json.loads(json_str)
        assert isinstance(records, list)

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_stocks_json_compatibility(self, mock_ak):
        """Test that top stocks data can be serialized to JSON."""
        import json

        mock_df = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "今日持股-股数": [150000000],
                "今日持股-市值": [2250000000],
                "今日持股-占流通股比": [5.5],
                "5日增持估计-市值": [112500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 10)

        json_str = result.to_json(orient="records")
        assert json_str is not None

        records = json.loads(json_str)
        assert isinstance(records, list)


# ============================================================================
# Unit Tests - Public Functions
# ============================================================================


class TestPublicFunctions:
    """Test public API functions."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_get_northbound_flow(self, mock_ak):
        """Test get_northbound_flow function."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "当日成交净买额": [15.7, 29.0],
                "买入成交额": [100.0, 150.0],
                "卖出成交额": [84.3, 121.0],
                "当日余额": [1000.0, 1029.0],
            }
        )
        mock_ak.return_value = mock_df

        result = get_northbound_flow(start_date="2024-01-01", end_date="2024-01-31", market="all")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "date" in result.columns
        assert "market" in result.columns
        assert "northbound_net_buy" in result.columns

    @patch("akshare.stock_hsgt_individual_em")
    def test_get_northbound_holdings_with_symbol(self, mock_ak):
        """Test get_northbound_holdings with specific symbol."""
        # Mock akshare response
        mock_df = pd.DataFrame(
            {"日期": ["2024-01-01"], "持股数量": [1000000], "持股市值": [50000000], "持股占比": [2.5]}
        )
        mock_ak.return_value = mock_df

        result = get_northbound_holdings(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "holdings_shares" in result.columns

    @patch("akshare.stock_hsgt_board_rank_em")
    def test_get_northbound_top_stocks(self, mock_ak):
        """Test get_northbound_top_stocks function."""
        # Mock akshare response
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "000001"],
                "名称": ["浦发银行", "平安银行"],
                "今日持股": [1000000, 800000],
                "持股数量": [50000000, 40000000],
                "持股占比": [2.5, 2.0],
            }
        )
        mock_ak.return_value = mock_df

        result = get_northbound_top_stocks(date="2024-01-01", market="all", top_n=10)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "rank" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert len(result) <= 10


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Additional Tests - Market Distribution and Flow Consistency
# ============================================================================


class TestNorthboundMarketDistribution:
    """Test market distribution and market split functionality."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_market_parameter_all(self, mock_ak):
        """Test market parameter 'all' includes all data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "当日成交净买额": [50.25, 30.18],
                "买入成交额": [150.50, 120.30],
                "卖出成交额": [100.25, 90.12],
                "当日余额": [1550.25, 1520.07],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-16", "all")

        assert all(result["market"] == "all")
        assert len(result) > 0

    @patch("akshare.stock_hsgt_hist_em")
    def test_market_parameter_sh(self, mock_ak):
        """Test market parameter 'sh' filters Shanghai market."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "当日成交净买额": [30.50, 25.30],
                "买入成交额": [100.50, 95.30],
                "卖出成交额": [70.00, 70.00],
                "当日余额": [1200.50, 1225.80],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-16", "sh")

        assert all(result["market"] == "sh")

    @patch("akshare.stock_hsgt_hist_em")
    def test_market_parameter_sz(self, mock_ak):
        """Test market parameter 'sz' filters Shenzhen market."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "当日成交净买额": [20.50, 15.30],
                "买入成交额": [80.50, 75.30],
                "卖出成交额": [60.00, 60.00],
                "当日余额": [800.50, 815.80],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-16", "sz")

        assert all(result["market"] == "sz")


class TestNorthboundHoldingsChanges:
    """Test holdings change tracking."""

    @patch("akshare.stock_hsgt_individual_em")
    def test_holdings_change_positive(self, mock_ak):
        """Test positive holdings change."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "持股数量": [15000000, 15500000],
                "持股市值": [225000000, 232500000],
                "持股占比": [3.5, 3.6],
                "持股变化": [500000, 500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("600000", "2024-01-15", "2024-01-16")

        assert all(result["holdings_change"] >= 0)

    @patch("akshare.stock_hsgt_individual_em")
    def test_holdings_change_negative(self, mock_ak):
        """Test negative holdings change."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16"],
                "持股数量": [15000000, 14500000],
                "持股市值": [225000000, 217500000],
                "持股占比": [3.5, 3.4],
                "持股变化": [-500000, -500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("600000", "2024-01-15", "2024-01-16")

        assert all(result["holdings_change"] <= 0)

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_holdings_change_tracking(self, mock_ak):
        """Test holdings change is tracked over time."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600000"],
                "名称": ["浦发银行", "浦发银行"],
                "持股日期": ["2024-01-15", "2024-01-16"],
                "持股数量(股)": [15000000, 16000000],
                "持股市值(元)": [225000000, 240000000],
                "持股占比(%)": [3.5, 3.7],
                "持股数量增减": [500000, 1000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings(None, "2024-01-01", "2024-01-31")

        assert "holdings_change" in result.columns


class TestNorthboundIndustryFlow:
    """Test industry-level flow analysis."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_flow_data_structure(self, mock_ak):
        """Test flow data has correct structure for analysis."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "当日成交净买额": [50.25, -30.18, 42.56],
                "买入成交额": [150.50, 120.30, 145.60],
                "卖出成交额": [100.25, 150.48, 103.04],
                "当日余额": [1550.25, 1520.07, 1562.63],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-17", "all")

        assert "date" in result.columns
        assert "northbound_net_buy" in result.columns
        assert "northbound_buy_amount" in result.columns
        assert "northbound_sell_amount" in result.columns

    @patch("akshare.stock_hsgt_hist_em")
    def test_flow_trend_analysis(self, mock_ak):
        """Test flow trend can be calculated."""
        mock_df = pd.DataFrame(
            {
                "日期": [
                    "2024-01-10",
                    "2024-01-11",
                    "2024-01-12",
                    "2024-01-13",
                    "2024-01-14",
                ],
                "当日成交净买额": [10.0, 15.0, -5.0, 20.0, 30.0],
                "买入成交额": [100.0, 115.0, 95.0, 120.0, 130.0],
                "卖出成交额": [90.0, 100.0, 100.0, 100.0, 100.0],
                "当日余额": [1000.0, 1015.0, 995.0, 1020.0, 1030.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-10", "2024-01-14", "all")

        assert len(result) > 0
        assert result["northbound_net_buy"].dtype in [float, "float64"]


class TestNorthboundTopStocksRanking:
    """Test top stocks ranking functionality."""

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_stocks_by_holdings_value(self, mock_ak):
        """Test top stocks sorted by holdings value."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 5)

        assert "rank" in result.columns
        assert result["rank"].iloc[0] == 1
        assert result["rank"].iloc[1] == 2

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_n_limit_enforced(self, mock_ak):
        """Test top_n parameter limits results."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036", "000002", "600887"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行", "万科A", "伊利股份"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000, 70000000, 80000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000, 1050000000, 1200000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1, 5.0, 5.3],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000, 52500000, 60000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 3)

        assert len(result) <= 3

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_stocks_market_filter_sh(self, mock_ak):
        """Test top stocks filtered by Shanghai market."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "sh", 10)

        if not result.empty:
            assert all(str(s).startswith("6") for s in result["symbol"])

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_top_stocks_market_filter_sz(self, mock_ak):
        """Test top stocks filtered by Shenzhen market."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "sz", 10)

        if not result.empty:
            assert all(str(s).startswith(("0", "3")) for s in result["symbol"])


class TestNorthboundTrendAnalysis:
    """Test trend analysis functionality."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_trend_direction_detection(self, mock_ak):
        """Test detecting trend direction."""
        mock_df = pd.DataFrame(
            {
                "日期": [
                    "2024-01-10",
                    "2024-01-11",
                    "2024-01-12",
                    "2024-01-13",
                    "2024-01-14",
                ],
                "当日成交净买额": [10.0, 15.0, 20.0, 25.0, 30.0],
                "买入成交额": [100.0, 115.0, 120.0, 125.0, 130.0],
                "卖出成交额": [90.0, 100.0, 100.0, 100.0, 100.0],
                "当日余额": [1000.0, 1015.0, 1020.0, 1025.0, 1030.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-10", "2024-01-14", "all")

        # Check trend (positive flow increasing)
        net_flows = result["northbound_net_buy"].tolist()
        assert net_flows[0] < net_flows[-1]

    @patch("akshare.stock_hsgt_hist_em")
    def test_flow_volatility(self, mock_ak):
        """Test flow volatility can be measured."""
        mock_df = pd.DataFrame(
            {
                "日期": [
                    "2024-01-10",
                    "2024-01-11",
                    "2024-01-12",
                    "2024-01-13",
                    "2024-01-14",
                ],
                "当日成交净买额": [10.0, -50.0, 30.0, -20.0, 40.0],
                "买入成交额": [100.0, 50.0, 130.0, 80.0, 140.0],
                "卖出成交额": [90.0, 100.0, 100.0, 100.0, 100.0],
                "当日余额": [1000.0, 950.0, 1030.0, 980.0, 1040.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-10", "2024-01-14", "all")

        assert len(result) > 0
        # High volatility should be reflected in net buy values
        net_flows = result["northbound_net_buy"]
        assert net_flows.max() > net_flows.min()


class TestNorthboundFlowConsistency:
    """Test flow data consistency."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_net_buy_equals_buy_minus_sell(self, mock_ak):
        """Test net buy equals buy amount minus sell amount."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        expected_net = result["northbound_buy_amount"].iloc[0] - result["northbound_sell_amount"].iloc[0]
        actual_net = result["northbound_net_buy"].iloc[0]
        assert abs(expected_net - actual_net) < 100

    @patch("akshare.stock_hsgt_hist_em")
    def test_balance_consistency(self, mock_ak):
        """Test balance field consistency."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        assert "balance" in result.columns
        assert result["balance"].iloc[0] > 0


class TestNorthboundHoldingsFlowConsistency:
    """Test consistency between holdings and flow data."""

    @patch("akshare.stock_hsgt_hold_stock_em")
    @patch("akshare.stock_hsgt_hist_em")
    def test_holdings_flow_direction_alignment(self, mock_flow, mock_holdings):
        """Test holdings change aligns with flow direction."""
        mock_holdings_df = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "持股日期": ["2024-01-15"],
                "持股数量(股)": [15000000],
                "持股市值(元)": [225000000],
                "持股占比(%)": [3.5],
                "持股数量增减": [500000],
            }
        )
        mock_holdings.return_value = mock_holdings_df

        mock_flow_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_flow.return_value = mock_flow_df

        provider = EastmoneyNorthboundProvider()
        holdings = provider.get_northbound_holdings(None, "2024-01-15", "2024-01-15")
        flow = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        # Positive holdings change should align with positive net flow
        if not holdings.empty and "holdings_change" in holdings.columns:
            holdings_change = holdings["holdings_change"].iloc[0]
            if holdings_change > 0:
                assert flow["northbound_net_buy"].iloc[0] > 0


class TestNorthboundErrorHandling:
    """Test error handling scenarios."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_api_error_handling(self, mock_ak):
        """Test API error returns empty DataFrame."""
        mock_ak.side_effect = Exception("API error")

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-01", "2024-01-31", "all")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "date" in result.columns

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_holdings_api_error_handling(self, mock_ak):
        """Test holdings API error returns empty DataFrame."""
        mock_ak.side_effect = Exception("API error")

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("600000", "2024-01-01", "2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert "symbol" in result.columns

    def test_invalid_market_parameter(self):
        """Test invalid market parameter raises error."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="Invalid market"):
            provider.get_northbound_flow("2024-01-01", "2024-01-31", "invalid")

    def test_invalid_top_n_parameter(self):
        """Test invalid top_n parameter raises error."""
        provider = EastmoneyNorthboundProvider()

        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_northbound_top_stocks("2024-01-01", "all", 0)


class TestNorthboundValueConversion:
    """Test value conversion logic."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_yuan_to_yuan_conversion(self, mock_ak):
        """Test conversion from 亿元 to 元."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [50.25],
                "买入成交额": [150.50],
                "卖出成交额": [100.25],
                "当日余额": [1550.25],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        expected_net_buy = 50.25 * 100000000
        assert abs(result["northbound_net_buy"].iloc[0] - expected_net_buy) < 1

    @patch("akshare.stock_hsgt_hist_em")
    def test_negative_value_conversion(self, mock_ak):
        """Test conversion handles negative values."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "当日成交净买额": [-30.18],
                "买入成交额": [120.30],
                "卖出成交额": [150.48],
                "当日余额": [1520.07],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-15", "2024-01-15", "all")

        assert result["northbound_net_buy"].iloc[0] < 0


class TestNorthboundDateRangeFiltering:
    """Test date range filtering."""

    @patch("akshare.stock_hsgt_hist_em")
    def test_date_range_inclusive(self, mock_ak):
        """Test date range includes both start and end dates."""
        mock_df = pd.DataFrame(
            {
                "日期": [
                    "2024-01-09",
                    "2024-01-10",
                    "2024-01-11",
                    "2024-01-12",
                    "2024-01-13",
                ],
                "当日成交净买额": [10.0, 15.0, 20.0, 25.0, 30.0],
                "买入成交额": [100.0, 115.0, 120.0, 125.0, 130.0],
                "卖出成交额": [90.0, 100.0, 100.0, 100.0, 100.0],
                "当日余额": [1000.0, 1015.0, 1020.0, 1025.0, 1030.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-10", "2024-01-12", "all")

        dates = result["date"].tolist()
        assert "2024-01-10" in dates
        assert "2024-01-12" in dates

    @patch("akshare.stock_hsgt_hist_em")
    def test_date_range_excludes_outside(self, mock_ak):
        """Test date range excludes dates outside range."""
        mock_df = pd.DataFrame(
            {
                "日期": [
                    "2024-01-09",
                    "2024-01-10",
                    "2024-01-11",
                    "2024-01-12",
                    "2024-01-13",
                ],
                "当日成交净买额": [10.0, 15.0, 20.0, 25.0, 30.0],
                "买入成交额": [100.0, 115.0, 120.0, 125.0, 130.0],
                "卖出成交额": [90.0, 100.0, 100.0, 100.0, 100.0],
                "当日余额": [1000.0, 1015.0, 1020.0, 1025.0, 1030.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow("2024-01-10", "2024-01-12", "all")

        dates = result["date"].tolist()
        assert "2024-01-09" not in dates
        assert "2024-01-13" not in dates


class TestNorthboundSymbolHandling:
    """Test symbol handling in holdings."""

    @patch("akshare.stock_hsgt_individual_em")
    def test_symbol_zero_padding(self, mock_ak):
        """Test symbol is zero-padded to 6 digits."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-15"],
                "持股数量": [15000000],
                "持股市值": [225000000],
                "持股占比": [3.5],
                "持股变化": [500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings("000001", "2024-01-01", "2024-01-31")

        assert result["symbol"].iloc[0] == "000001"

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_symbol_from_dataframe(self, mock_ak):
        """Test symbol extracted from DataFrame correctly."""
        mock_df = pd.DataFrame(
            {
                "代码": ["1", "36", "600000"],
                "名称": ["测试A", "测试B", "浦发银行"],
                "持股日期": ["2024-01-15"] * 3,
                "持股数量(股)": [10000000, 8000000, 15000000],
                "持股市值(元)": [150000000, 120000000, 225000000],
                "持股占比(%)": [2.5, 2.0, 3.5],
                "持股数量增减": [100000, 80000, 500000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_holdings(None, "2024-01-01", "2024-01-31")

        assert result["symbol"].iloc[0] == "000001"
        assert result["symbol"].iloc[1] == "000036"
        assert result["symbol"].iloc[2] == "600000"


class TestNorthboundMultipleMarkets:
    """Test handling of multiple market data."""

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_all_markets_combined(self, mock_ak):
        """Test all markets data combined correctly."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "000001", "300750"],
                "名称": ["浦发银行", "平安银行", "宁德时代"],
                "今日持股-股数": [150000000, 120000000, 65000000],
                "今日持股-市值": [2250000000, 1800000000, 975000000],
                "今日持股-占流通股比": [5.5, 7.2, 4.9],
                "5日增持估计-市值": [112500000, 90000000, 48750000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_top_stocks("2024-01-15", "all", 10)

        if not result.empty:
            symbols = result["symbol"].tolist()
            assert len(symbols) >= 3

    @patch("akshare.stock_hsgt_hold_stock_em")
    def test_market_specific_data(self, mock_ak):
        """Test market-specific data filtering."""
        mock_df = pd.DataFrame(
            {
                "代码": ["600000", "600519", "000001", "300750", "600036"],
                "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
                "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
                "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
                "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
                "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyNorthboundProvider()

        sh_result = provider.get_northbound_top_stocks("2024-01-15", "sh", 10)
        sz_result = provider.get_northbound_top_stocks("2024-01-15", "sz", 10)

        if not sh_result.empty:
            assert all(str(s).startswith("6") for s in sh_result["symbol"])

        if not sz_result.empty:
            assert all(str(s).startswith(("0", "3")) for s in sz_result["symbol"])
