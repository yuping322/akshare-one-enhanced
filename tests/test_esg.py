"""
Unit tests for ESG (ESG 评级) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.esg import (
    get_esg_rating,
    get_esg_rating_rank,
)
from akshare_one.modules.esg.eastmoney import EastmoneyESGProvider
from akshare_one.modules.esg import ESGFactory


class TestESGFactory:
    """Test ESGFactory class."""

    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = ESGFactory.get_provider("eastmoney")
        assert isinstance(provider, EastmoneyESGProvider)

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            ESGFactory.get_provider("invalid")

    def test_list_sources(self):
        """Test listing available sources."""
        sources = ESGFactory.list_sources()
        assert "eastmoney" in sources


class TestEastmoneyESGProvider:
    """Test EastmoneyESGProvider class."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyESGProvider()

    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == "esg"
        assert provider.get_source_name() == "eastmoney"
        assert provider.get_update_frequency() == "irregular"
        assert provider.get_delay_minutes() == 43200

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_all_stocks(self, mock_esg, provider):
        """Test getting ESG rating for all stocks."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "股票简称": ["浦发银行", "招商银行"],
                "评级日期": ["2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "symbol" in result.columns
        assert "rating_date" in result.columns
        assert "esg_score" in result.columns
        assert "e_score" in result.columns
        assert "s_score" in result.columns
        assert "g_score" in result.columns
        assert "rating_agency" in result.columns
        assert result["symbol"].iloc[0] == "600000"
        assert result["esg_score"].iloc[0] == 85.5
        assert result["e_score"].iloc[0] == 80.0

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_single_stock(self, mock_esg, provider):
        """Test getting ESG rating for a single stock."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "股票简称": ["浦发银行", "招商银行"],
                "评级日期": ["2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating("600000", "2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600000"
        assert result["esg_score"].iloc[0] == 85.5

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_empty(self, mock_esg, provider):
        """Test getting ESG rating with no data."""
        mock_esg.return_value = pd.DataFrame()

        result = provider.get_esg_rating("600000", "2024-01-01", "2024-12-31")

        assert result.empty
        assert "symbol" in result.columns
        assert "rating_date" in result.columns
        assert "esg_score" in result.columns

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_all_industries(self, mock_esg, provider):
        """Test getting ESG rating rankings for all industries."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)

        assert not result.empty
        assert len(result) == 4
        assert "rank" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "esg_score" in result.columns
        assert "industry" in result.columns
        assert "industry_rank" in result.columns

        # Check ranking order (descending by ESG score)
        assert result["rank"].iloc[0] == 1
        assert result["symbol"].iloc[0] == "600036"  # Highest score
        assert result["esg_score"].iloc[0] == 90.2

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_industry_filter(self, mock_esg, provider):
        """Test getting ESG rating rankings with industry filter."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", "银行", 100)

        assert not result.empty
        assert len(result) == 3
        assert all(result["industry"] == "银行")

        # Check ranking within banking industry
        assert result["rank"].iloc[0] == 1
        assert result["symbol"].iloc[0] == "600036"  # Highest score in banking

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_top_n(self, mock_esg, provider):
        """Test getting top N ESG ratings."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 2)

        assert not result.empty
        assert len(result) == 2
        assert result["rank"].iloc[0] == 1
        assert result["rank"].iloc[1] == 2

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_empty(self, mock_esg, provider):
        """Test getting ESG rating rankings with no data."""
        mock_esg.return_value = pd.DataFrame()

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)

        assert result.empty
        assert "rank" in result.columns
        assert "symbol" in result.columns

    def test_invalid_date_format(self, provider):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            provider.get_esg_rating_rank("2024/12/31", None, 100)

    def test_invalid_top_n(self, provider):
        """Test with invalid top_n value."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_esg_rating_rank("2024-12-31", None, 0)


class TestESGPublicAPI:
    """Test public API functions."""

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_api(self, mock_esg):
        """Test get_esg_rating public API."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["浦发银行"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = get_esg_rating("600000", start_date="2024-01-01", end_date="2024-12-31")
        assert not result.empty
        assert "symbol" in result.columns
        assert "esg_score" in result.columns

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_api(self, mock_esg):
        """Test get_esg_rating_rank public API."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "股票简称": ["浦发银行", "招商银行"],
                "ESG评分": [85.5, 90.2],
                "所属行业": ["银行", "银行"],
            }
        )
        mock_esg.return_value = mock_data

        result = get_esg_rating_rank("2024-12-31")
        assert not result.empty
        assert "rank" in result.columns
        assert "esg_score" in result.columns


class TestESGJSONCompatibility:
    """Test JSON compatibility of ESG data."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_json_compatibility(self, mock_esg, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "股票简称": ["浦发银行"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        # Test JSON serialization
        json_str = result.to_json(orient="records")
        assert json_str is not None

        # Check no NaN values
        assert not result.isnull().any().any()

        # Check symbol is string with leading zeros
        assert result["symbol"].dtype in ["object", "string"]
        assert result["symbol"].iloc[0] == "600000"

        # Check rating_date is string
        assert result["rating_date"].dtype in ["object", "string"]


class TestESGAdditionalCoverage:
    """Additional tests for coverage improvement."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyESGProvider()

    def test_fetch_data(self, provider):
        """Test fetch_data method returns empty DataFrame."""
        result = provider.fetch_data()
        assert result.empty

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_with_pagination(self, mock_esg, provider):
        """Test ESG rating with pagination parameters."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "评级日期": ["2024-09-30", "2024-09-30", "2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "E评分": [80.0, 88.0, 85.0, 70.0],
                "S评分": [85.0, 90.0, 88.0, 75.0],
                "G评分": [90.0, 92.0, 90.0, 80.0],
                "评级机构": ["华证ESG", "华证ESG", "华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=1, page_size=2)

        assert len(result) == 2
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_invalid_page(self, mock_esg, provider):
        """Test ESG rating with invalid page parameter."""
        with pytest.raises(ValueError, match="Page must be >= 1"):
            provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=0)

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_invalid_page_size(self, mock_esg, provider):
        """Test ESG rating with invalid page_size parameter."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page_size=0)

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_missing_columns(self, mock_esg, provider):
        """Test handling of missing columns in raw data."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        assert not result.empty
        assert result["esg_score"].iloc[0] == 0.0
        assert result["e_score"].iloc[0] == 0.0
        assert result["s_score"].iloc[0] == 0.0
        assert result["g_score"].iloc[0] == 0.0
        assert result["rating_agency"].iloc[0] == "Unknown"

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_alternative_columns(self, mock_esg, provider):
        """Test handling of alternative column names."""
        mock_data = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "日期": ["2024-09-30"],
                "ESG得分": [85.5],
                "环境评分": [80.0],
                "社会评分": [85.0],
                "治理评分": [90.0],
                "机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        assert not result.empty
        assert result["symbol"].iloc[0] == "600000"
        assert result["esg_score"].iloc[0] == 85.5
        assert result["e_score"].iloc[0] == 80.0

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_no_symbol_column(self, mock_esg, provider):
        """Test handling when symbol column is missing."""
        mock_data = pd.DataFrame(
            {
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        assert result.empty

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_missing_columns(self, mock_esg, provider):
        """Test handling of missing columns in ranking."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "ESG评分": [85.5],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 10)

        assert not result.empty
        assert result["name"].iloc[0] == ""
        assert result["industry"].iloc[0] == "未分类"

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_no_symbol_column(self, mock_esg, provider):
        """Test handling when symbol column is missing in ranking."""
        mock_data = pd.DataFrame(
            {
                "ESG评分": [85.5],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 10)

        assert result.empty

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_alternative_columns(self, mock_esg, provider):
        """Test handling of alternative column names in ranking."""
        mock_data = pd.DataFrame({"代码": ["600000"], "名称": ["浦发银行"], "ESG得分": [85.5], "行业": ["银行"]})
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 10)

        assert not result.empty
        assert result["symbol"].iloc[0] == "600000"
        assert result["name"].iloc[0] == "浦发银行"
        assert result["esg_score"].iloc[0] == 85.5

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_exception_handling(self, mock_esg, provider):
        """Test exception handling in get_esg_rating."""
        mock_esg.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch ESG rating data"):
            provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_exception_handling(self, mock_esg, provider):
        """Test exception handling in get_esg_rating_rank."""
        mock_esg.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch ESG rating rankings"):
            provider.get_esg_rating_rank("2024-12-31", None, 100)

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_with_score_alternatives(self, mock_esg, provider):
        """Test handling of alternative score column names."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "综合评分": [85.5],
                "评级日期": ["2024-09-30"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")

        assert not result.empty
        assert result["esg_score"].iloc[0] == 85.5

    @patch("akshare.stock_esg_rate_sina")
    def test_get_esg_rating_rank_multiple_industries(self, mock_esg, provider):
        """Test ranking with multiple industries."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)

        assert not result.empty
        assert result["industry_rank"].iloc[0] == 1
        assert result["industry_rank"].iloc[3] == 1

    def test_get_esg_rating_invalid_symbol(self, provider):
        """Test validation of invalid symbol."""
        with pytest.raises(ValueError):
            provider.get_esg_rating("invalid", "2024-01-01", "2024-12-31")

    def test_get_esg_rating_invalid_date_range(self, provider):
        """Test validation of invalid date range."""
        with pytest.raises(ValueError):
            provider.get_esg_rating(None, "2024-12-31", "2024-01-01")

    def test_provider_data_type(self, provider):
        """Test provider data type method."""
        assert provider.get_data_type() == "esg"

    def test_provider_update_frequency(self, provider):
        """Test provider update frequency."""
        assert provider.get_update_frequency() == "irregular"

    def test_provider_delay_minutes(self, provider):
        """Test provider delay minutes."""
        assert provider.get_delay_minutes() == 43200


class TestESGNumericalValidation:
    """Test numerical range validation for ESG data."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_esg_score_in_valid_range(self, mock_esg, provider):
        """ESG评分应在有效范围内(0-100)。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001"],
                "股票简称": ["浦发银行", "招商银行", "平安银行"],
                "评级日期": ["2024-09-30", "2024-09-30", "2024-09-30"],
                "ESG评分": [35.5, 90.2, 100.0],
                "E评分": [30.0, 88.0, 95.0],
                "S评分": [35.0, 90.0, 98.0],
                "G评分": [40.0, 92.0, 100.0],
                "评级机构": ["华证ESG", "华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert not result.empty
        assert result["esg_score"].min() >= 0
        assert result["esg_score"].max() <= 100

    @patch("akshare.stock_esg_rate_sina")
    def test_e_score_in_valid_range(self, mock_esg, provider):
        """E评分应在有效范围内。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [75.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["e_score"].iloc[0] >= 0
        assert result["e_score"].iloc[0] <= 100

    @patch("akshare.stock_esg_rate_sina")
    def test_s_score_in_valid_range(self, mock_esg, provider):
        """S评分应在有效范围内。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["s_score"].iloc[0] >= 0
        assert result["s_score"].iloc[0] <= 100

    @patch("akshare.stock_esg_rate_sina")
    def test_g_score_in_valid_range(self, mock_esg, provider):
        """G评分应在有效范围内。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["g_score"].iloc[0] >= 0
        assert result["g_score"].iloc[0] <= 100

    @patch("akshare.stock_esg_rate_sina")
    def test_ranking_sorted_by_esg_score_descending(self, mock_esg, provider):
        """排名应按ESG评分降序排列。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)
        scores = result["esg_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    @patch("akshare.stock_esg_rate_sina")
    def test_ranking_sequence_correct(self, mock_esg, provider):
        """排名序号应正确连续。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [90.0, 80.0, 70.0, 60.0],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)
        assert list(result["rank"]) == [1, 2, 3, 4]


class TestESGDateFiltering:
    """Test date filtering logic for ESG."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_date_range_filter_includes_records(self, mock_esg, provider):
        """日期范围内记录应被包含。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "评级日期": ["2024-06-15", "2024-08-20"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-06-01", "2024-09-01")
        assert len(result) == 2

    @patch("akshare.stock_esg_rate_sina")
    def test_date_range_filter_excludes_outside(self, mock_esg, provider):
        """日期范围外记录应被排除。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001"],
                "评级日期": ["2024-05-01", "2024-07-15", "2024-10-01"],
                "ESG评分": [85.5, 90.2, 88.0],
                "E评分": [80.0, 88.0, 85.0],
                "S评分": [85.0, 90.0, 88.0],
                "G评分": [90.0, 92.0, 90.0],
                "评级机构": ["华证ESG", "华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-06-01", "2024-09-01")
        assert len(result) == 1
        assert result["rating_date"].iloc[0] == "2024-07-15"

    @patch("akshare.stock_esg_rate_sina")
    def test_no_date_column_uses_end_date(self, mock_esg, provider):
        """无日期列时使用end_date作为默认值。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert not result.empty
        assert result["rating_date"].iloc[0] == "2024-12-31"


class TestESGPagination:
    """Test pagination logic for ESG rating."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_pagination_page1(self, mock_esg, provider):
        """第一页数据正确。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": [f"60000{i}" for i in range(10)],
                "评级日期": ["2024-09-30"] * 10,
                "ESG评分": [90 - i for i in range(10)],
                "E评分": [80 - i for i in range(10)],
                "S评分": [85 - i for i in range(10)],
                "G评分": [90 - i for i in range(10)],
                "评级机构": ["华证ESG"] * 10,
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=1, page_size=5)
        assert len(result) == 5
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_esg_rate_sina")
    def test_pagination_page2(self, mock_esg, provider):
        """第二页数据正确。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": [f"60000{i}" for i in range(10)],
                "评级日期": ["2024-09-30"] * 10,
                "ESG评分": [90 - i for i in range(10)],
                "E评分": [80 - i for i in range(10)],
                "S评分": [85 - i for i in range(10)],
                "G评分": [90 - i for i in range(10)],
                "评级机构": ["华证ESG"] * 10,
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=2, page_size=5)
        assert len(result) == 5
        assert result["symbol"].iloc[0] == "600005"

    @patch("akshare.stock_esg_rate_sina")
    def test_pagination_no_overlap(self, mock_esg, provider):
        """分页数据不应重叠。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": [f"60000{i}" for i in range(10)],
                "评级日期": ["2024-09-30"] * 10,
                "ESG评分": [90 - i for i in range(10)],
                "E评分": [80 - i for i in range(10)],
                "S评分": [85 - i for i in range(10)],
                "G评分": [90 - i for i in range(10)],
                "评级机构": ["华证ESG"] * 10,
            }
        )
        mock_esg.return_value = mock_data

        page1 = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=1, page_size=5)
        page2 = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=2, page_size=5)

        symbols1 = set(page1["symbol"])
        symbols2 = set(page2["symbol"])
        assert symbols1.isdisjoint(symbols2)

    @patch("akshare.stock_esg_rate_sina")
    def test_pagination_exceeds_total(self, mock_esg, provider):
        """分页超出总数据量时返回空。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31", page=10, page_size=5)
        assert result.empty


class TestESGIndustryRanking:
    """Test industry ranking logic."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_industry_rank_correct(self, mock_esg, provider):
        """行业内排名应正确计算。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "银行", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)
        banking_stocks = result[result["industry"] == "银行"]
        assert banking_stocks["industry_rank"].iloc[0] == 1
        assert banking_stocks["industry_rank"].iloc[1] == 2
        assert banking_stocks["industry_rank"].iloc[2] == 3

    @patch("akshare.stock_esg_rate_sina")
    def test_industry_rank_independent_per_industry(self, mock_esg, provider):
        """每个行业的排名应独立计算。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036", "000001", "000002"],
                "股票简称": ["浦发银行", "招商银行", "平安银行", "万科A"],
                "ESG评分": [85.5, 90.2, 88.0, 75.5],
                "所属行业": ["银行", "银行", "证券", "房地产"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)
        assert result[result["industry"] == "银行"]["industry_rank"].iloc[0] == 1
        assert result[result["industry"] == "证券"]["industry_rank"].iloc[0] == 1
        assert result[result["industry"] == "房地产"]["industry_rank"].iloc[0] == 1


class TestESGRatingAgency:
    """Test rating agency handling."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_rating_agency_standardization(self, mock_esg, provider):
        """评级机构应被正确提取。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "评级日期": ["2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "MSCI"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["rating_agency"].iloc[0] == "华证ESG"
        assert result["rating_agency"].iloc[1] == "MSCI"

    @patch("akshare.stock_esg_rate_sina")
    def test_rating_agency_alternative_column(self, mock_esg, provider):
        """评级机构使用'机构'列名的处理。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["rating_agency"].iloc[0] == "华证ESG"

    @patch("akshare.stock_esg_rate_sina")
    def test_no_rating_agency_column(self, mock_esg, provider):
        """无评级机构列时使用默认值。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["rating_agency"].iloc[0] == "Unknown"


class TestESGSymbolHandling:
    """Test symbol handling and validation."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_symbol_zfill_6_digits(self, mock_esg, provider):
        """股票代码应补齐6位。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["1", "36"],
                "评级日期": ["2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert "000001" in result["symbol"].values
        assert "000036" in result["symbol"].values

    @patch("akshare.stock_esg_rate_sina")
    def test_symbol_filter_exact_match(self, mock_esg, provider):
        """股票代码筛选应精确匹配。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "评级日期": ["2024-09-30", "2024-09-30"],
                "ESG评分": [85.5, 90.2],
                "E评分": [80.0, 88.0],
                "S评分": [85.0, 90.0],
                "G评分": [90.0, 92.0],
                "评级机构": ["华证ESG", "华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating("600000", "2024-01-01", "2024-12-31")
        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_esg_rate_sina")
    def test_ranking_symbol_zfill(self, mock_esg, provider):
        """排名数据股票代码补齐。"""
        mock_data = pd.DataFrame(
            {
                "代码": ["1", "36"],
                "名称": ["股票A", "股票B"],
                "ESG评分": [90.2, 85.5],
                "行业": ["银行", "证券"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 100)
        assert result["symbol"].iloc[0] == "000001"
        assert result["symbol"].iloc[1] == "000036"


class TestESGScoreComponents:
    """Test ESG score components handling."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_esg_score_comprehensive_alternative(self, mock_esg, provider):
        """使用综合评分替代ESG评分。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "综合评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["esg_score"].iloc[0] == 85.5

    @patch("akshare.stock_esg_rate_sina")
    def test_e_score_environmental_alternative(self, mock_esg, provider):
        """使用环境评分替代E评分。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "环境评分": [80.0],
                "S评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["e_score"].iloc[0] == 80.0

    @patch("akshare.stock_esg_rate_sina")
    def test_s_score_social_alternative(self, mock_esg, provider):
        """使用社会评分替代S评分。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "社会评分": [85.0],
                "G评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["s_score"].iloc[0] == 85.0

    @patch("akshare.stock_esg_rate_sina")
    def test_g_score_governance_alternative(self, mock_esg, provider):
        """使用治理评分替代G评分。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [85.5],
                "E评分": [80.0],
                "S评分": [85.0],
                "治理评分": [90.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["g_score"].iloc[0] == 90.0


class TestESGEdgeCases:
    """Test edge cases for ESG data."""

    @pytest.fixture
    def provider(self):
        return EastmoneyESGProvider()

    @patch("akshare.stock_esg_rate_sina")
    def test_zero_esg_score(self, mock_esg, provider):
        """ESG评分为零的处理。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "评级日期": ["2024-09-30"],
                "ESG评分": [0.0],
                "E评分": [0.0],
                "S评分": [0.0],
                "G评分": [0.0],
                "评级机构": ["华证ESG"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert result["esg_score"].iloc[0] == 0.0

    @patch("akshare.stock_esg_rate_sina")
    def test_large_data_volume(self, mock_esg, provider):
        """大数据量处理。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": [f"600{i:03d}" for i in range(100)],
                "评级日期": ["2024-09-30"] * 100,
                "ESG评分": [90 - i * 0.5 for i in range(100)],
                "E评分": [80 - i * 0.3 for i in range(100)],
                "S评分": [85 - i * 0.4 for i in range(100)],
                "G评分": [90 - i * 0.5 for i in range(100)],
                "评级机构": ["华证ESG"] * 100,
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating(None, "2024-01-01", "2024-12-31")
        assert len(result) == 100

    def test_standardize_and_filter_with_source(self, provider):
        """standardize_and_filter方法测试。"""
        result = provider.standardize_and_filter(pd.DataFrame(), source=pd.DataFrame())
        assert isinstance(result, pd.DataFrame)

    @patch("akshare.stock_esg_rate_sina")
    def test_ranking_top_n_boundary(self, mock_esg, provider):
        """top_n边界值测试。"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "ESG评分": [90.0, 85.0],
                "所属行业": ["银行", "银行"],
            }
        )
        mock_esg.return_value = mock_data

        result = provider.get_esg_rating_rank("2024-12-31", None, 1)
        assert len(result) == 1
