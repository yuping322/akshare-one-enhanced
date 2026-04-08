"""
Unit tests for equity pledge (股权质押) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.pledge import (
    get_equity_pledge,
    get_equity_pledge_ratio_rank,
)
from akshare_one.modules.pledge.eastmoney import EastmoneyEquityPledgeProvider
from akshare_one.modules.pledge import EquityPledgeFactory


class TestEquityPledgeFactory:
    """Test EquityPledgeFactory class."""

    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = EquityPledgeFactory.get_provider("eastmoney")
        assert isinstance(provider, EastmoneyEquityPledgeProvider)

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            EquityPledgeFactory.get_provider("invalid")

    def test_list_sources(self):
        """Test listing available sources."""
        sources = EquityPledgeFactory.list_sources()
        assert "eastmoney" in sources


class TestEastmoneyEquityPledgeProvider:
    """Test EastmoneyEquityPledgeProvider class."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyEquityPledgeProvider()

    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == "pledge"
        assert provider.get_source_name() == "eastmoney"
        assert provider.get_update_frequency() == "irregular"
        assert provider.get_delay_minutes() == 0

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_single_stock(self, mock_pledge, provider):
        """Test getting equity pledge data for a single stock."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A", "股东B"],
                "质押股数": [10000000.0, 20000000.0],
                "占所持股份比例": [50.0, 60.0],
                "质权人": ["银行A", "银行B"],
                "公告日期": ["2024-01-02", "2024-01-03"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

        assert not result.empty
        assert len(result) == 2
        assert "symbol" in result.columns
        assert "shareholder_name" in result.columns
        assert "pledge_shares" in result.columns
        assert "pledge_ratio" in result.columns
        assert "pledgee" in result.columns
        assert "pledge_date" in result.columns
        assert result["symbol"].iloc[0] == "600000"
        assert result["shareholder_name"].iloc[0] == "股东A"
        assert result["pledge_shares"].iloc[0] == 10000000.0
        assert result["pledge_ratio"].iloc[0] == 50.0
        assert result["pledgee"].iloc[0] == "银行A"
        assert result["pledge_date"].iloc[0] == "2024-01-02"

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_empty(self, mock_pledge, provider):
        """Test getting equity pledge data with no data."""
        mock_pledge.return_value = pd.DataFrame()

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

        assert result.empty
        assert "symbol" in result.columns
        assert "shareholder_name" in result.columns

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_all_stocks(self, mock_pledge, provider):
        """Test getting equity pledge data for all stocks."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "股东名称": ["股东A", "股东B"],
                "质押股数": [10000000.0, 20000000.0],
                "占所持股份比例": [50.0, 60.0],
                "质权人": ["银行A", "银行B"],
                "公告日期": ["2024-01-02", "2024-01-03"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")

        assert not result.empty
        assert len(result) == 2
        assert "symbol" in result.columns
        assert "shareholder_name" in result.columns
        assert result["symbol"].iloc[0] == "600000"
        assert result["symbol"].iloc[1] == "600036"

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank(self, mock_ratio, provider):
        """Test getting equity pledge ratio ranking."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001"],
                "股票简称": ["浦发银行", "招商银行", "平安银行"],
                "质押比例": [80.5, 75.3, 70.2],
                "质押市值": [5000000000.0, 4500000000.0, 4000000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)

        assert not result.empty
        assert len(result) == 3
        assert "rank" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "pledge_ratio" in result.columns
        assert "pledge_value" in result.columns
        assert result["rank"].iloc[0] == 1
        assert result["symbol"].iloc[0] == "600000"
        assert result["name"].iloc[0] == "浦发银行"
        assert result["pledge_ratio"].iloc[0] == 80.5
        assert result["pledge_value"].iloc[0] == 5000000000.0
        # Check ranking is correct (sorted by pledge_ratio descending)
        assert result["pledge_ratio"].iloc[0] >= result["pledge_ratio"].iloc[1]
        assert result["pledge_ratio"].iloc[1] >= result["pledge_ratio"].iloc[2]

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_top_n(self, mock_ratio, provider):
        """Test getting top N equity pledge ratio ranking."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002", "000003"],
                "股票简称": ["股票A", "股票B", "股票C", "股票D", "股票E"],
                "质押比例": [80.5, 75.3, 70.2, 65.1, 60.0],
                "质押市值": [5000000000.0, 4500000000.0, 4000000000.0, 3500000000.0, 3000000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 3)

        assert not result.empty
        assert len(result) == 3  # Should only return top 3
        assert result["rank"].iloc[0] == 1
        assert result["rank"].iloc[2] == 3

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_empty(self, mock_ratio, provider):
        """Test getting equity pledge ratio ranking with no data."""
        mock_ratio.return_value = pd.DataFrame()

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)

        assert result.empty
        assert "rank" in result.columns
        assert "symbol" in result.columns

    def test_get_equity_pledge_ratio_rank_invalid_date(self, provider):
        """Test getting equity pledge ratio ranking with invalid date."""
        with pytest.raises(ValueError, match="Invalid date format"):
            provider.get_equity_pledge_ratio_rank("2024/01/31", 100)

    def test_get_equity_pledge_ratio_rank_invalid_top_n(self, provider):
        """Test getting equity pledge ratio ranking with invalid top_n."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_equity_pledge_ratio_rank("2024-01-31", 0)


class TestEquityPledgePublicAPI:
    """Test public API functions."""

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_api(self, mock_pledge):
        """Test get_equity_pledge public API."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = get_equity_pledge("600000", start_date="2024-01-01", end_date="2024-01-31")
        assert not result.empty
        assert "symbol" in result.columns

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_api(self, mock_ratio):
        """Test get_equity_pledge_ratio_rank public API."""
        mock_data = pd.DataFrame(
            {"股票代码": ["600000"], "股票简称": ["浦发银行"], "质押比例": [80.5], "质押市值": [5000000000.0]}
        )
        mock_ratio.return_value = mock_data

        result = get_equity_pledge_ratio_rank("2024-01-31")
        assert not result.empty
        assert "rank" in result.columns


class TestEquityPledgeJSONCompatibility:
    """Test JSON compatibility of equity pledge data."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_json_compatibility_pledge_data(self, mock_pledge, provider):
        """Test that equity pledge data output is JSON compatible."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

        # Test JSON serialization
        json_str = result.to_json(orient="records")
        assert json_str is not None

        # Check no NaN values
        assert not result.isnull().any().any()

        # Check symbol is string with leading zeros
        assert result["symbol"].dtype in ["object", "string"]
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_json_compatibility_ratio_rank(self, mock_ratio, provider):
        """Test that equity pledge ratio ranking output is JSON compatible."""
        mock_data = pd.DataFrame(
            {"股票代码": ["600000"], "股票简称": ["浦发银行"], "质押比例": [80.5], "质押市值": [5000000000.0]}
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)

        # Test JSON serialization
        json_str = result.to_json(orient="records")
        assert json_str is not None

        # Check no NaN values
        assert not result.isnull().any().any()

        # Check symbol is string with leading zeros
        assert result["symbol"].dtype in ["object", "string"]
        assert result["symbol"].iloc[0] == "600000"


class TestEquityPledgeAdditionalCoverage:
    """Additional tests for coverage improvement."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyEquityPledgeProvider()

    def test_fetch_data(self, provider):
        """Test fetch_data method returns empty DataFrame."""
        result = provider.fetch_data()
        assert result.empty

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_missing_columns(self, mock_pledge, provider):
        """Test handling of missing columns in raw data."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

        assert not result.empty
        assert result["pledge_ratio"].iloc[0] == 0.0
        assert result["pledgee"].iloc[0] == ""
        assert result["pledge_date"].iloc[0] == ""

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_all_stocks_missing_columns(self, mock_pledge, provider):
        """Test handling of missing columns in all stocks data."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股东名称": ["股东A"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")

        assert not result.empty
        assert result["pledge_shares"].iloc[0] == 0.0
        assert result["pledge_ratio"].iloc[0] == 0.0
        assert result["pledgee"].iloc[0] == ""
        assert result["pledge_date"].iloc[0] == ""

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_missing_columns(self, mock_ratio, provider):
        """Test handling of missing columns in ratio ranking."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 10)

        assert not result.empty
        assert result["name"].iloc[0] == ""
        assert result["pledge_ratio"].iloc[0] == 0.0
        assert result["pledge_value"].iloc[0] == 0.0

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_with_alternative_columns(self, mock_pledge, provider):
        """Test handling of alternative column names."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "质押比例": [50.0],
                "质权人": ["银行A"],
                "质押日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

        assert not result.empty
        assert result["pledge_ratio"].iloc[0] == 50.0
        assert result["pledge_date"].iloc[0] == "2024-01-02"

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_all_with_alternative_columns(self, mock_pledge, provider):
        """Test handling of alternative column names for all stocks."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "质押比例": [50.0],
                "质权人": ["银行A"],
                "质押日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")

        assert not result.empty
        assert result["pledge_ratio"].iloc[0] == 50.0
        assert result["pledge_date"].iloc[0] == "2024-01-02"

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_with_alternative_columns(self, mock_ratio, provider):
        """Test handling of alternative column names in ranking."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["浦发银行"],
                "质押率": [80.5],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 10)

        assert not result.empty
        assert result["pledge_ratio"].iloc[0] == 80.5

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_exception_handling(self, mock_pledge, provider):
        """Test exception handling in get_equity_pledge."""
        mock_pledge.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch equity pledge data"):
            provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_get_equity_pledge_ratio_rank_exception_handling(self, mock_ratio, provider):
        """Test exception handling in get_equity_pledge_ratio_rank."""
        mock_ratio.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch equity pledge ratio ranking"):
            provider.get_equity_pledge_ratio_rank("2024-01-31", 100)

    def test_get_equity_pledge_invalid_symbol(self, provider):
        """Test validation of invalid symbol."""
        with pytest.raises(ValueError):
            provider.get_equity_pledge("invalid", "2024-01-01", "2024-01-31")

    def test_get_equity_pledge_invalid_date_range(self, provider):
        """Test validation of invalid date range."""
        with pytest.raises(ValueError):
            provider.get_equity_pledge("600000", "2024-12-31", "2024-01-01")

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_get_equity_pledge_with_akshare_compat_errors(self, mock_pledge, provider):
        """Test compatibility with different akshare versions."""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )

        mock_pledge.side_effect = [TypeError("Invalid parameter"), TypeError("Invalid parameter"), mock_data]

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty

    def test_provider_data_type(self, provider):
        """Test provider data type method."""
        assert provider.get_data_type() == "pledge"

    def test_provider_update_frequency(self, provider):
        """Test provider update frequency."""
        assert provider.get_update_frequency() == "irregular"

    def test_provider_delay_minutes(self, provider):
        """Test provider delay minutes."""
        assert provider.get_delay_minutes() == 0


class TestPledgeNumericalValidation:
    """Test numerical range validation for pledge data."""

    @pytest.fixture
    def provider(self):
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_pledge_ratio_not_exceed_100(self, mock_pledge, provider):
        """质押比例不应超过100%。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A", "股东B", "股东C"],
                "质押股数": [10000000.0, 20000000.0, 30000000.0],
                "占所持股份比例": [45.0, 85.0, 99.9],
                "质权人": ["银行A", "银行B", "银行C"],
                "公告日期": ["2024-01-02", "2024-01-03", "2024-01-04"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty
        assert result["pledge_ratio"].max() <= 100

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_pledge_shares_positive(self, mock_pledge, provider):
        """质押股数应为正值。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty
        assert all(result["pledge_shares"] >= 0)

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_pledge_ratio_rank_sorted_descending(self, mock_ratio, provider):
        """质押比例排名应按降序排列。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["股票A", "股票B", "股票C", "股票D"],
                "质押比例": [80.5, 75.3, 70.2, 65.1],
                "质押市值": [5000000000.0, 4500000000.0, 4000000000.0, 3500000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)
        assert not result.empty
        ratios = result["pledge_ratio"].tolist()
        assert ratios == sorted(ratios, reverse=True)

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_pledge_ratio_rank_correct_ranking(self, mock_ratio, provider):
        """排名序号应正确连续。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002", "000003"],
                "股票简称": ["股票A", "股票B", "股票C", "股票D", "股票E"],
                "质押比例": [90.0, 80.0, 70.0, 60.0, 50.0],
                "质押市值": [5000000000.0, 4000000000.0, 3000000000.0, 2000000000.0, 1000000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 5)
        assert list(result["rank"]) == [1, 2, 3, 4, 5]

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_pledge_value_positive(self, mock_ratio, provider):
        """质押市值应为正值。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["股票A"],
                "质押比例": [80.5],
                "质押市值": [5000000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)
        assert not result.empty
        assert all(result["pledge_value"] >= 0)


class TestPledgeDateFiltering:
    """Test date filtering logic."""

    @pytest.fixture
    def provider(self):
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_date_range_filter_includes_records(self, mock_pledge, provider):
        """日期范围内记录应被包含。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A", "股东B"],
                "质押股数": [10000000.0, 20000000.0],
                "占所持股份比例": [50.0, 60.0],
                "质权人": ["银行A", "银行B"],
                "公告日期": ["2024-01-15", "2024-01-20"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-10", "2024-01-25")
        assert len(result) == 2

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_date_range_filter_excludes_outside(self, mock_pledge, provider):
        """日期范围外记录应被排除。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A", "股东B", "股东C"],
                "质押股数": [10000000.0, 20000000.0, 30000000.0],
                "占所持股份比例": [50.0, 60.0, 70.0],
                "质权人": ["银行A", "银行B", "银行C"],
                "公告日期": ["2024-01-05", "2024-01-15", "2024-02-01"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-10", "2024-01-20")
        assert len(result) == 1
        assert result["pledge_date"].iloc[0] == "2024-01-15"

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_empty_date_field_handling(self, mock_pledge, provider):
        """空日期字段应被正确处理。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty
        assert result["pledge_date"].iloc[0] == ""

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_all_stocks_date_filtering(self, mock_pledge, provider):
        """全市场数据日期过滤。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "股东名称": ["股东A", "股东B"],
                "质押股数": [10000000.0, 20000000.0],
                "占所持股份比例": [50.0, 60.0],
                "质权人": ["银行A", "银行B"],
                "公告日期": ["2024-01-15", "2024-02-01"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")
        assert len(result) == 1


class TestPledgeSymbolHandling:
    """Test symbol handling and validation."""

    @pytest.fixture
    def provider(self):
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_symbol_zfill_6_digits_from_raw_data(self, mock_pledge, provider):
        """原始数据中的股票代码应补齐6位。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["1", "36", "600000"],
                "股东名称": ["股东A", "股东B", "股东C"],
                "质押股数": [10000000.0, 20000000.0, 30000000.0],
                "占所持股份比例": [50.0, 60.0, 70.0],
                "质权人": ["银行A", "银行B", "银行C"],
                "公告日期": ["2024-01-02", "2024-01-03", "2024-01-04"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")
        assert "000001" in result["symbol"].values
        assert "000036" in result["symbol"].values

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_all_stocks_symbol_zfill(self, mock_pledge, provider):
        """全市场数据股票代码补齐。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["1", "36", "600000"],
                "股东名称": ["股东A", "股东B", "股东C"],
                "质押股数": [10000000.0, 20000000.0, 30000000.0],
                "占所持股份比例": [50.0, 60.0, 70.0],
                "质权人": ["银行A", "银行B", "银行C"],
                "公告日期": ["2024-01-02", "2024-01-03", "2024-01-04"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge(None, "2024-01-01", "2024-01-31")
        assert "000001" in result["symbol"].values
        assert "000036" in result["symbol"].values
        assert "600000" in result["symbol"].values

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_ratio_rank_symbol_zfill(self, mock_ratio, provider):
        """排名数据股票代码补齐。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["1", "36"],
                "股票简称": ["股票A", "股票B"],
                "质押比例": [80.5, 75.3],
                "质押市值": [5000000000.0, 4500000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)
        assert result["symbol"].iloc[0] == "000001"
        assert result["symbol"].iloc[1] == "000036"


class TestPledgeAkshareCompatibility:
    """Test akshare API compatibility and error handling."""

    @pytest.fixture
    def provider(self):
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_fallback_to_stock_parameter(self, mock_pledge, provider):
        """测试symbol参数失败后使用stock参数。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.side_effect = [TypeError("symbol not found"), mock_data]

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_fallback_to_positional_argument(self, mock_pledge, provider):
        """测试参数失败后使用位置参数。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.side_effect = [TypeError("symbol not found"), TypeError("stock not found"), mock_data]

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert not result.empty

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_all_fallbacks_fail_returns_empty(self, mock_pledge, provider):
        """所有兼容性尝试失败后返回空数据。"""
        mock_pledge.side_effect = [
            TypeError("error1"),
            TypeError("error2"),
            TypeError("error3"),
            TypeError("error4"),
        ]

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert result.empty
        assert "symbol" in result.columns


class TestPledgeEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def provider(self):
        return EastmoneyEquityPledgeProvider()

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_single_record(self, mock_pledge, provider):
        """单条记录处理。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [50.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert len(result) == 1

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_large_volume_data(self, mock_pledge, provider):
        """大数据量处理。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": [f"股东{i}" for i in range(100)],
                "质押股数": [10000000.0 * i for i in range(100)],
                "占所持股份比例": [50.0 + i * 0.5 for i in range(100)],
                "质权人": [f"银行{i}" for i in range(100)],
                "公告日期": [f"2024-01-{(i % 28) + 1:02d}" for i in range(100)],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert len(result) == 100

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_ratio_rank_top_n_boundary(self, mock_ratio, provider):
        """top_n边界值测试。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["股票A"],
                "质押比例": [80.5],
                "质押市值": [5000000000.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 1)
        assert len(result) == 1

    def test_standardize_and_filter_with_source(self, provider):
        """standardize_and_filter方法测试。"""
        result = provider.standardize_and_filter(pd.DataFrame(), source=pd.DataFrame())
        assert isinstance(result, pd.DataFrame)

    @patch("akshare.stock_gpzy_pledge_ratio_detail_em")
    def test_pledge_ratio_zero_value(self, mock_pledge, provider):
        """质押比例为0的处理。"""
        mock_data = pd.DataFrame(
            {
                "股东名称": ["股东A"],
                "质押股数": [10000000.0],
                "占所持股份比例": [0.0],
                "质权人": ["银行A"],
                "公告日期": ["2024-01-02"],
            }
        )
        mock_pledge.return_value = mock_data

        result = provider.get_equity_pledge("600000", "2024-01-01", "2024-01-31")
        assert result["pledge_ratio"].iloc[0] == 0.0

    @patch("akshare.stock_gpzy_pledge_ratio_em")
    def test_ratio_rank_zero_pledge_value(self, mock_ratio, provider):
        """质押市值为0的处理。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["股票A"],
                "质押比例": [80.5],
                "质押市值": [0.0],
            }
        )
        mock_ratio.return_value = mock_data

        result = provider.get_equity_pledge_ratio_rank("2024-01-31", 100)
        assert result["pledge_value"].iloc[0] == 0.0
