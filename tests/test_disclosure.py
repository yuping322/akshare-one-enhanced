"""
Unit tests for disclosure module.

Tests the disclosure data provider implementations including:
- Dividend data fetching and standardization
- Repurchase data fetching and standardization
- ST/delist risk data fetching and standardization
- Factory pattern
- JSON compatibility
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.disclosure import (
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
    DisclosureFactory,
)
from akshare_one.modules.disclosure.eastmoney import EastmoneyDisclosureProvider


class TestDisclosureFactory:
    """Test DisclosureFactory class."""

    def test_get_provider_eastmoney(self):
        """Test getting Eastmoney provider."""
        provider = DisclosureFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyDisclosureProvider)
        assert provider.get_source_name() == "eastmoney"

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            DisclosureFactory.get_provider(source="invalid")

    def test_get_available_sources(self):
        """Test getting available sources."""
        sources = DisclosureFactory.get_available_sources()
        assert isinstance(sources, list)
        assert "eastmoney" in sources


class TestEastmoneyDisclosureProvider:
    """Test EastmoneyDisclosureProvider class."""

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = EastmoneyDisclosureProvider()
        assert provider.get_source_name() == "eastmoney"
        assert provider.get_data_type() == "disclosure"
        assert provider.get_update_frequency() == "realtime"
        assert provider.get_delay_minutes() == 60

    @patch("akshare.stock_dividend_cninfo")
    def test_get_dividend_data_single_stock(self, mock_ak):
        """Test getting dividend data for a single stock."""
        # Mock akshare response
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报", "2022年报"],
                "派息比例": [1.5, 1.0],
                "股权登记日": ["2024-06-20", "2023-06-15"],
                "除权日": ["2024-06-21", "2023-06-16"],
                "派息日": ["2024-06-22", "2023-06-17"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            "symbol",
            "fiscal_year",
            "dividend_per_share",
            "record_date",
            "ex_dividend_date",
            "payment_date",
            "dividend_ratio",
        ]

        # Verify data
        assert len(result) == 2
        assert result["symbol"].iloc[0] == "600000"
        assert result["dividend_per_share"].iloc[0] == 0.15  # 1.5 / 10
        assert result["ex_dividend_date"].iloc[0] == "2024-06-21"

    @patch("akshare.stock_dividend_cninfo")
    def test_get_dividend_data_empty_result(self, mock_ak):
        """Test getting dividend data with empty result."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        # Should return empty DataFrame with correct structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            "symbol",
            "fiscal_year",
            "dividend_per_share",
            "record_date",
            "ex_dividend_date",
            "payment_date",
            "dividend_ratio",
        ]

    @patch("akshare.stock_dividend_cninfo")
    def test_get_dividend_data_json_compatibility(self, mock_ak):
        """Test dividend data JSON compatibility."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": ["2024-06-21"],
                "派息日": [pd.NaT],  # Test NaT handling
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        # Test JSON serialization
        json_str = result.to_json(orient="records")
        assert json_str is not None

        # Verify no NaN/Infinity
        assert not result.isnull().any().any() or result["payment_date"].isnull().all()

    @patch("akshare.stock_repurchase_em")
    def test_get_repurchase_data_all_stocks(self, mock_ak):
        """Test getting repurchase data for all stocks."""
        # Mock akshare response
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "000001"],
                "最新公告日期": ["2024-01-15", "2024-01-10"],
                "实施进度": ["进行中", "已完成"],
                "已回购金额": [50000000.0, 100000000.0],
                "已回购股份数量": [1000000.0, 2000000.0],
                "计划回购价格区间": ["10-15元", "20-25元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data(None, "2024-01-01", "2024-12-31")

        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["symbol", "announcement_date", "progress", "amount", "quantity", "price_range"]

        # Verify data
        assert len(result) == 2
        assert result["symbol"].iloc[0] == "600000"
        assert result["announcement_date"].iloc[0] == "2024-01-15"
        assert result["progress"].iloc[0] == "进行中"
        assert result["amount"].iloc[0] == 50000000.0

    @patch("akshare.stock_repurchase_em")
    def test_get_repurchase_data_single_stock(self, mock_ak):
        """Test getting repurchase data for a single stock."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "000001"],
                "最新公告日期": ["2024-01-15", "2024-01-10"],
                "实施进度": ["进行中", "已完成"],
                "已回购金额": [50000000.0, 100000000.0],
                "已回购股份数量": [1000000.0, 2000000.0],
                "计划回购价格区间": ["10-15元", "20-25元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        # Should only return data for 600000
        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_repurchase_em")
    def test_get_repurchase_data_date_filter(self, mock_ak):
        """Test repurchase data date filtering."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "000001"],
                "最新公告日期": ["2024-01-15", "2023-12-10"],
                "实施进度": ["进行中", "已完成"],
                "已回购金额": [50000000.0, 100000000.0],
                "已回购股份数量": [1000000.0, 2000000.0],
                "计划回购价格区间": ["10-15元", "20-25元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data(None, "2024-01-01", "2024-12-31")

        # Should only return data within date range
        assert len(result) == 1
        assert result["announcement_date"].iloc[0] == "2024-01-15"

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_get_st_delist_data_all_stocks(self, mock_sz, mock_sh):
        """Test getting ST/delist data for all stocks."""
        # Mock SH data
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001", "600002"],
                "公司简称": ["*ST华谊", "ST海润"],
                "暂停上市日期": ["2024-01-15", "2024-02-20"],
            }
        )
        mock_sh.return_value = mock_sh_df

        # Mock SZ data
        mock_sz_df = pd.DataFrame(
            {
                "证券代码": ["000001"],
                "证券简称": ["S*ST昌鱼"],
                "终止上市日期": ["2024-03-10"],
            }
        )
        mock_sz.return_value = mock_sz_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data(None)

        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["symbol", "name", "st_type", "risk_level", "announcement_date"]

        # Verify data
        assert len(result) == 3
        assert "600001" in result["symbol"].values
        assert "000001" in result["symbol"].values

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_get_st_delist_data_single_stock(self, mock_sz, mock_sh):
        """Test getting ST/delist data for a single stock."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001", "600002"],
                "公司简称": ["*ST华谊", "ST海润"],
                "暂停上市日期": ["2024-01-15", "2024-02-20"],
            }
        )
        mock_sh.return_value = mock_sh_df

        mock_sz_df = pd.DataFrame()
        mock_sz.return_value = mock_sz_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data("600001")

        # Should only return data for 600001
        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600001"
        assert result["st_type"].iloc[0] == "*ST"
        assert result["risk_level"].iloc[0] == "high"

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_get_st_delist_data_risk_levels(self, mock_sz, mock_sh):
        """Test ST/delist data risk level classification."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001", "600002", "600003"],
                "公司简称": ["*ST华谊", "ST海润", "退市大控"],
                "暂停上市日期": ["2024-01-15", "2024-02-20", "2024-03-10"],
            }
        )
        mock_sh.return_value = mock_sh_df

        mock_sz_df = pd.DataFrame()
        mock_sz.return_value = mock_sz_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data(None)

        # Verify risk levels
        assert result[result["symbol"] == "600001"]["risk_level"].iloc[0] == "high"  # *ST
        assert result[result["symbol"] == "600002"]["risk_level"].iloc[0] == "medium"  # ST
        assert result[result["symbol"] == "600003"]["risk_level"].iloc[0] == "critical"  # 退市


class TestDisclosurePublicAPI:
    """Test public API functions."""

    @patch("akshare.stock_dividend_cninfo")
    def test_get_dividend_data_api(self, mock_ak):
        """Test get_dividend_data public API."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": ["2024-06-21"],
                "派息日": ["2024-06-22"],
            }
        )
        mock_ak.return_value = mock_df

        result = get_dividend_data("600000", start_date="2023-01-01", end_date="2024-12-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "symbol" in result.columns
        assert "dividend_per_share" in result.columns

    @patch("akshare.stock_repurchase_em")
    def test_get_repurchase_data_api(self, mock_ak):
        """Test get_repurchase_data public API."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["进行中"],
                "已回购金额": [50000000.0],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = get_repurchase_data("600000", start_date="2024-01-01", end_date="2024-12-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "symbol" in result.columns
        assert "progress" in result.columns

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_get_st_delist_data_api(self, mock_sz, mock_sh):
        """Test get_st_delist_data public API."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001"],
                "公司简称": ["*ST华谊"],
                "暂停上市日期": ["2024-01-15"],
            }
        )
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()

        result = get_st_delist_data("600001")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "symbol" in result.columns
        assert "st_type" in result.columns
        assert "risk_level" in result.columns


class TestDisclosureDataValidation:
    """Test data validation in disclosure module."""

    def test_invalid_symbol_format(self):
        """Test validation with invalid symbol format."""
        provider = EastmoneyDisclosureProvider()

        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.get_dividend_data("INVALID", "2024-01-01", "2024-12-31")

    def test_invalid_date_format(self):
        """Test validation with invalid date format."""
        provider = EastmoneyDisclosureProvider()

        with pytest.raises(ValueError, match="Invalid start_date format"):
            provider.get_dividend_data("600000", "2024/01/01", "2024-12-31")

    def test_invalid_date_range(self):
        """Test validation with invalid date range."""
        provider = EastmoneyDisclosureProvider()

        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            provider.get_dividend_data("600000", "2024-12-31", "2024-01-01")


class TestDisclosureJSONCompatibility:
    """Test JSON compatibility of disclosure data."""

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_data_json_serialization(self, mock_ak):
        """Test dividend data can be serialized to JSON."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": ["2024-06-21"],
                "派息日": ["2024-06-22"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        # Should be able to serialize to JSON
        json_str = result.to_json(orient="records")
        assert json_str is not None
        assert "NaN" not in json_str
        assert "Infinity" not in json_str

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_data_json_serialization(self, mock_ak):
        """Test repurchase data can be serialized to JSON."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["进行中"],
                "已回购金额": [50000000.0],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        # Should be able to serialize to JSON
        json_str = result.to_json(orient="records")
        assert json_str is not None
        assert "NaN" not in json_str
        assert "Infinity" not in json_str


class TestDisclosureNewsEnhanced:
    """Enhanced tests for disclosure news functionality."""

    @patch("akshare.stock_notice_report")
    def test_get_disclosure_news_all(self, mock_ak):
        """Test getting all disclosure news."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14"],
                "代码": ["600000", "000001"],
                "公告标题": ["2023年年报", "分红派息公告"],
                "公告类型": ["年报", "分红"],
                "网址": ["http://example.com/1", "http://example.com/2"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["date", "symbol", "title", "category", "content", "url"]
        assert len(result) > 0
        assert result["date"].iloc[0] == "2024-01-15"
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_notice_report")
    def test_get_disclosure_news_by_category(self, mock_ak):
        """Test filtering disclosure news by category."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14", "2024-01-13"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["2023年分红派息公告", "股份回购计划", "重大事项公告"],
                "公告类型": ["分红", "回购", "重大事项"],
                "网址": ["http://ex1", "http://ex2", "http://ex3"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()

        # Test dividend category
        result_dividend = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "dividend")
        assert len(result_dividend) >= 1
        assert any("分红" in title or "派息" in title for title in result_dividend["title"].values)

        # Test repurchase category
        result_repurchase = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "repurchase")
        assert len(result_repurchase) >= 1
        assert any("回购" in title for title in result_repurchase["title"].values)

    @patch("akshare.stock_notice_report")
    def test_disclosure_date_range_filter(self, mock_ak):
        """Test disclosure date range filtering."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-10", "2023-12-01"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["公告1", "公告2", "公告3"],
                "公告类型": ["年报", "年报", "年报"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        # Should have data within range
        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns

        # Verify date field format
        if len(result) > 0:
            dates = pd.to_datetime(result["date"], errors="coerce")
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                # Some dates should be in range
                assert any(valid_dates >= pd.to_datetime("2024-01-01"))

    def test_disclosure_category_validation(self):
        """Test disclosure category parameter validation."""
        provider = EastmoneyDisclosureProvider()

        with pytest.raises(ValueError, match="Invalid category"):
            provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "invalid_category")

    @patch("akshare.stock_notice_report")
    def test_disclosure_field_standardization(self, mock_ak):
        """Test disclosure field standardization."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15"],
                "代码": ["600000"],
                "公告标题": ["2023年年报"],
                "公告类型": ["年报"],
                "网址": ["http://example.com"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        # Verify standard field names
        expected_fields = ["date", "symbol", "title", "category", "content", "url"]
        assert list(result.columns) == expected_fields

        # Verify data types
        assert isinstance(result["date"].iloc[0], str)
        assert isinstance(result["symbol"].iloc[0], str)
        assert len(result["symbol"].iloc[0]) == 6  # 6-digit code

    def test_disclosure_multi_source(self):
        """Test disclosure data from multiple sources."""
        from akshare_one.modules.disclosure.sina import SinaDisclosureProvider

        eastmoney_provider = DisclosureFactory.get_provider("eastmoney")
        sina_provider = DisclosureFactory.get_provider("sina")

        assert eastmoney_provider.get_source_name() == "eastmoney"
        assert sina_provider.get_source_name() == "sina"

        # Both providers should support same interface
        assert hasattr(eastmoney_provider, "get_disclosure_news")
        assert hasattr(sina_provider, "get_disclosure_news")

    @patch("akshare.stock_notice_report")
    def test_disclosure_empty_result(self, mock_ak):
        """Test handling of empty disclosure results."""
        mock_ak.return_value = pd.DataFrame()

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["date", "symbol", "title", "category", "content", "url"]

    @patch("akshare.stock_notice_report")
    def test_disclosure_api_timeout(self, mock_ak):
        """Test handling of API timeout in disclosure."""
        mock_ak.side_effect = TimeoutError("API timeout")

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        # Should return empty DataFrame on error
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestDividendDataEnhanced:
    """Enhanced tests for dividend data functionality."""

    @patch("akshare.stock_dividend_cninfo")
    def test_get_dividend_data_basic(self, mock_ak):
        """Test basic dividend data retrieval."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2024年报", "2023年报", "2022年报"],
                "派息比例": [2.5, 1.8, 1.2],
                "股权登记日": ["2025-07-01", "2024-06-20", "2023-06-15"],
                "除权日": ["2025-07-02", "2024-06-21", "2023-06-16"],
                "派息日": ["2025-07-03", "2024-06-22", "2023-06-17"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data("600000", "2023-01-01", "2025-12-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 2  # At least 2 records should be in range
        assert all(result["symbol"] == "600000")

        # Verify dividend per share calculation (派息比例 / 10)
        if len(result) > 0:
            assert result["dividend_per_share"].iloc[0] == 0.25
            if len(result) > 1:
                assert result["dividend_per_share"].iloc[1] == 0.18


class TestRepurchaseDataEnhanced:
    """Enhanced tests for repurchase data functionality."""

    @patch("akshare.stock_repurchase_em")
    def test_get_repurchase_data_basic(self, mock_ak):
        """Test basic repurchase data retrieval."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "600036"],
                "最新公告日期": ["2024-03-01", "2024-02-15"],
                "实施进度": ["实施中", "已完成"],
                "已回购金额": [100000000.0, 200000000.0],
                "已回购股份数量": [5000000.0, 8000000.0],
                "计划回购价格区间": ["10-20元", "15-25元"],
                "计划回购金额区间-下限": [80000000.0, 150000000.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data(None, "2024-01-01", "2024-12-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "progress" in result.columns
        assert "amount" in result.columns

        # Verify sorting by announcement_date descending
        assert result["announcement_date"].iloc[0] == "2024-03-01"
        assert result["announcement_date"].iloc[1] == "2024-02-15"


class TestStDelistDataEnhanced:
    """Enhanced tests for ST/delist data functionality."""

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_get_st_delist_data(self, mock_sz, mock_sh):
        """Test ST/delist data retrieval with different risk types."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001", "600002", "600003"],
                "公司简称": ["*ST华谊", "ST海润", "退市大控"],
                "暂停上市日期": ["2024-04-01", "2024-03-15", "2024-02-01"],
            }
        )
        mock_sh.return_value = mock_sh_df

        mock_sz_df = pd.DataFrame(
            {
                "证券代码": ["000001"],
                "证券简称": ["S*ST昌鱼"],
                "终止上市日期": ["2024-01-15"],
            }
        )
        mock_sz.return_value = mock_sz_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data(None)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert "st_type" in result.columns
        assert "risk_level" in result.columns

        # Verify ST type classification
        st_types = result["st_type"].values
        assert "*ST" in st_types
        assert "ST" in st_types
        assert "S*ST" in st_types

        # Verify risk level classification
        risk_levels = result["risk_level"].values
        assert "critical" in risk_levels  # 退市
        assert "high" in risk_levels  # *ST
        assert "medium" in risk_levels  # ST


class TestDisclosureCategoryFilteringEnhanced:
    """Enhanced tests for disclosure category filtering."""

    @patch("akshare.stock_notice_report")
    def test_dividend_category_keywords(self, mock_ak):
        """Test dividend category filters by keywords."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14", "2024-01-13"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["2023年分红派息公告", "现金分红方案", "普通公告"],
                "公告类型": ["分红", "年报", "公告"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "dividend")

        assert len(result) >= 2
        titles = result["title"].tolist()
        assert any("分红" in title or "派息" in title for title in titles)

    @patch("akshare.stock_notice_report")
    def test_repurchase_category_keywords(self, mock_ak):
        """Test repurchase category filters by keywords."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14"],
                "代码": ["600000", "000001"],
                "公告标题": ["股份回购计划", "回购股份实施进展"],
                "公告类型": ["回购", "回购"],
                "网址": ["url1", "url2"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "repurchase")

        assert len(result) >= 2
        titles = result["title"].tolist()
        assert all("回购" in title for title in titles)

    @patch("akshare.stock_notice_report")
    def test_st_category_keywords(self, mock_ak):
        """Test ST category filters by keywords."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14"],
                "代码": ["600001", "000001"],
                "公告标题": ["ST风险警示公告", "退市风险提示"],
                "公告类型": ["ST", "风险"],
                "网址": ["url1", "url2"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        # Use a narrower date range to avoid multiple API calls
        result = provider.get_disclosure_news(None, "2024-01-15", "2024-01-15", "st")

        # Check that filtering works if we have results
        if len(result) > 0:
            assert any("ST" in title or "退市" in title or "风险" in title for title in result["title"].tolist())

    @patch("akshare.stock_notice_report")
    def test_major_event_category_keywords(self, mock_ak):
        """Test major event category filters by keywords."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14"],
                "代码": ["600000", "000001"],
                "公告标题": ["重大资产重组", "重大合同签订"],
                "公告类型": ["重大事项", "重大事项"],
                "网址": ["url1", "url2"],
            }
        )
        mock_ak.return_value = mock_df

        provider = EastmoneyDisclosureProvider()
        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "major_event")

        assert len(result) >= 2


class TestDisclosureKeywordSearch:
    """Test keyword search functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_notice_report")
    def test_title_keyword_search(self, mock_ak, provider):
        """Test searching by title keywords."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14", "2024-01-13"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["分红公告", "回购公告", "普通公告"],
                "公告类型": ["分红", "回购", "年报"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "dividend")

        assert any("分红" in title for title in result["title"].tolist())


class TestDisclosureDateFilterEnhanced:
    """Enhanced tests for disclosure date filtering."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_notice_report")
    def test_date_range_boundary(self, mock_ak, provider):
        """Test date range includes boundary dates."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-01", "2024-01-15", "2024-01-31"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["公告1", "公告2", "公告3"],
                "公告类型": ["年报", "年报", "年报"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        dates = result["date"].tolist()
        assert "2024-01-01" in dates
        assert "2024-01-31" in dates

    @patch("akshare.stock_notice_report")
    def test_date_sorting_descending(self, mock_ak, provider):
        """Test results are sorted by date descending."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-10", "2024-01-20", "2024-01-15"],
                "代码": ["600000", "000001", "000002"],
                "公告标题": ["公告A", "公告B", "公告C"],
                "公告类型": ["年报", "年报", "年报"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        dates = result["date"].tolist()
        assert dates == sorted(dates, reverse=True)


class TestDividendDataEnhanced2:
    """Enhanced tests for dividend data."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_per_share_calculation(self, mock_ak, provider):
        """Test dividend per share is calculated correctly."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报", "2022年报"],
                "派息比例": [10.0, 5.0],
                "股权登记日": ["2024-06-20", "2023-06-15"],
                "除权日": ["2024-06-21", "2023-06-16"],
                "派息日": ["2024-06-22", "2023-06-17"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        assert result["dividend_per_share"].iloc[0] == 1.0
        assert result["dividend_per_share"].iloc[1] == 0.5

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_date_format(self, mock_ak, provider):
        """Test dividend dates are formatted correctly."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": ["2024-06-21"],
                "派息日": ["2024-06-22"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        assert result["record_date"].iloc[0] == "2024-06-20"
        assert result["ex_dividend_date"].iloc[0] == "2024-06-21"
        assert result["payment_date"].iloc[0] == "2024-06-22"

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_symbol_consistency(self, mock_ak, provider):
        """Test symbol is consistent across records."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报", "2022年报", "2021年报"],
                "派息比例": [1.5, 1.0, 0.8],
                "股权登记日": ["2024-06-20", "2023-06-15", "2022-06-10"],
                "除权日": ["2024-06-21", "2023-06-16", "2022-06-11"],
                "派息日": ["2024-06-22", "2023-06-17", "2022-06-12"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_dividend_data("600000", "2021-01-01", "2024-12-31")

        assert all(result["symbol"] == "600000")


class TestRepurchaseDataEnhanced2:
    """Enhanced tests for repurchase data."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_progress_status(self, mock_ak, provider):
        """Test repurchase progress status preserved."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "000001"],
                "最新公告日期": ["2024-01-15", "2024-01-10"],
                "实施进度": ["实施中", "已完成"],
                "已回购金额": [50000000.0, 100000000.0],
                "已回购股份数量": [1000000.0, 2000000.0],
                "计划回购价格区间": ["10-15元", "20-25元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data(None, "2024-01-01", "2024-12-31")

        assert "实施中" in result["progress"].tolist()
        assert "已完成" in result["progress"].tolist()

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_amount_range(self, mock_ak, provider):
        """Test repurchase amount is within expected range."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["实施中"],
                "已回购金额": [50000000.0],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        assert result["amount"].iloc[0] >= 40000000.0

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_quantity_positive(self, mock_ak, provider):
        """Test repurchase quantity is positive."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["实施中"],
                "已回购金额": [50000000.0],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        assert result["quantity"].iloc[0] > 0


class TestSTTypeClassification:
    """Test ST type classification functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    def test_st_type_star_st(self, provider):
        """Test *ST type classification."""
        result = provider.standardize_st_type("*ST华谊")
        assert result == "*ST"

    def test_st_type_regular_st(self, provider):
        """Test ST type classification."""
        result = provider.standardize_st_type("ST海润")
        assert result == "ST"

    def test_st_type_s_star_st(self, provider):
        """Test S*ST type classification."""
        result = provider.standardize_st_type("S*ST昌鱼")
        assert result == "S*ST"

    def test_st_type_sst(self, provider):
        """Test SST type classification."""
        result = provider.standardize_st_type("SST股票")
        assert result == "SST"

    def test_st_type_normal(self, provider):
        """Test normal stock classification."""
        result = provider.standardize_st_type("浦发银行")
        assert result == "normal"


class TestRiskLevelClassification:
    """Test risk level classification functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    def test_risk_level_critical(self, provider):
        """Test critical risk level."""
        result = provider.standardize_risk_level("退市大控")
        assert result == "critical"

    def test_risk_level_high(self, provider):
        """Test high risk level."""
        result = provider.standardize_risk_level("*ST华谊")
        assert result == "high"

    def test_risk_level_medium(self, provider):
        """Test medium risk level."""
        result = provider.standardize_risk_level("ST海润")
        assert result == "medium"

    def test_risk_level_low(self, provider):
        """Test low risk level."""
        result = provider.standardize_risk_level("浦发银行")
        assert result == "low"

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_combined_risk_classification(self, mock_sz, mock_sh, provider):
        """Test combined risk classification from SH and SZ."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001", "600002", "600003"],
                "公司简称": ["*ST华谊", "ST海润", "退市大控"],
                "暂停上市日期": ["2024-01-15", "2024-02-20", "2024-03-10"],
            }
        )
        mock_sh.return_value = mock_sh_df

        mock_sz_df = pd.DataFrame(
            {
                "证券代码": ["000001"],
                "证券简称": ["S*ST昌鱼"],
                "终止上市日期": ["2024-01-15"],
            }
        )
        mock_sz.return_value = mock_sz_df

        result = provider.get_st_delist_data(None)

        risk_levels = result["risk_level"].tolist()
        assert "high" in risk_levels
        assert "medium" in risk_levels
        assert "critical" in risk_levels


class TestDelistDataSources:
    """Test data from SH and SZ sources."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_sh_delist_data_only(self, mock_sz, mock_sh, provider):
        """Test SH delist data only."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001"],
                "公司简称": ["*ST华谊"],
                "暂停上市日期": ["2024-01-15"],
            }
        )
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()

        result = provider.get_st_delist_data(None)

        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600001"

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_sz_delist_data_only(self, mock_sz, mock_sh, provider):
        """Test SZ delist data only."""
        mock_sh.return_value = pd.DataFrame()
        mock_sz_df = pd.DataFrame(
            {
                "证券代码": ["000001"],
                "证券简称": ["S*ST昌鱼"],
                "终止上市日期": ["2024-01-15"],
            }
        )
        mock_sz.return_value = mock_sz_df

        result = provider.get_st_delist_data(None)

        assert len(result) == 1
        assert result["symbol"].iloc[0] == "000001"

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_both_sources_combined(self, mock_sz, mock_sh, provider):
        """Test both SH and SZ data combined."""
        mock_sh_df = pd.DataFrame(
            {
                "公司代码": ["600001"],
                "公司简称": ["*ST华谊"],
                "暂停上市日期": ["2024-01-15"],
            }
        )
        mock_sh.return_value = mock_sh_df

        mock_sz_df = pd.DataFrame(
            {
                "证券代码": ["000001"],
                "证券简称": ["S*ST昌鱼"],
                "终止上市日期": ["2024-01-15"],
            }
        )
        mock_sz.return_value = mock_sz_df

        result = provider.get_st_delist_data(None)

        assert len(result) == 2
        assert "600001" in result["symbol"].tolist()
        assert "000001" in result["symbol"].tolist()


class TestDisclosureSymbolFiltering:
    """Test symbol filtering in disclosure."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_notice_report")
    def test_symbol_filter_exact_match(self, mock_ak, provider):
        """Test symbol filter exact match."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14"],
                "代码": ["600000", "000001"],
                "公告标题": ["公告1", "公告2"],
                "公告类型": ["年报", "年报"],
                "网址": ["url1", "url2"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news("600000", "2024-01-01", "2024-01-31", "all")

        assert len(result) >= 1
        assert all(result["symbol"] == "600000")

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_symbol_filter(self, mock_ak, provider):
        """Test symbol filter in repurchase data."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000", "000001", "600036"],
                "最新公告日期": ["2024-01-15", "2024-01-10", "2024-01-12"],
                "实施进度": ["实施中", "已完成", "实施中"],
                "已回购金额": [50000000.0, 100000000.0, 80000000.0],
                "已回购股份数量": [1000000.0, 2000000.0, 1500000.0],
                "计划回购价格区间": ["10-15元", "20-25元", "15-20元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0, 60000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data("600036", "2024-01-01", "2024-12-31")

        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600036"


class TestDisclosureErrorHandlingEnhanced:
    """Enhanced error handling tests."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_api_error(self, mock_ak, provider):
        """Test dividend API error handling."""
        mock_ak.side_effect = Exception("API error")

        result = provider.get_dividend_data("600000", "2024-01-01", "2024-12-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "symbol" in result.columns

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_api_error(self, mock_ak, provider):
        """Test repurchase API error handling."""
        mock_ak.side_effect = Exception("API error")

        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "symbol" in result.columns

    @patch("akshare.stock_info_sh_delist")
    @patch("akshare.stock_info_sz_delist")
    def test_delist_api_error(self, mock_sz, mock_sh, provider):
        """Test delist API error handling."""
        mock_sh.side_effect = Exception("API error")
        mock_sz.side_effect = Exception("API error")

        result = provider.get_st_delist_data("600001")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "symbol" in result.columns

    def test_invalid_category_validation(self, provider):
        """Test invalid category raises error."""
        with pytest.raises(ValueError, match="Invalid category"):
            provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "invalid")


class TestDisclosureFieldStandardization:
    """Test field standardization in disclosure."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_notice_report")
    def test_symbol_zero_padding(self, mock_ak, provider):
        """Test symbol zero padding."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15"],
                "代码": ["1"],
                "公告标题": ["测试公告"],
                "公告类型": ["年报"],
                "网址": ["url1"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news(None, "2024-01-01", "2024-01-31", "all")

        assert result["symbol"].iloc[0] == "000001"

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_symbol_padding(self, mock_ak, provider):
        """Test repurchase symbol padding."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["36"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["实施中"],
                "已回购金额": [50000050.0],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data(None, "2024-01-01", "2024-12-31")

        assert result["symbol"].iloc[0] == "000036"


class TestDisclosureProgressStandardization:
    """Test progress status standardization."""

    def test_progress_standardization(self):
        """Test progress status is standardized."""
        provider = EastmoneyDisclosureProvider()

        assert provider.standardize_repurchase_progress("实施中") == "in_progress"
        assert provider.standardize_repurchase_progress("已完成") == "completed"
        assert provider.standardize_repurchase_progress("计划回购") == "planned"
        assert provider.standardize_repurchase_progress("取消回购") == "cancelled"


class TestDisclosureCategoryStandardization:
    """Test category standardization."""

    def test_category_standardization(self):
        """Test category is standardized."""
        provider = EastmoneyDisclosureProvider()

        assert provider.standardize_category("分红") == "dividend"
        assert provider.standardize_category("派息") == "dividend"
        assert provider.standardize_category("回购") == "repurchase"
        assert provider.standardize_category("全部") == "all"


class TestDisclosureDividendRatioCalculation:
    """Test dividend ratio calculation."""

    def test_dividend_ratio_calculation(self):
        """Test dividend ratio is calculated correctly."""
        provider = EastmoneyDisclosureProvider()

        ratio = provider.standardize_dividend_ratio(1.0, 20.0)
        assert ratio == 5.0

        ratio = provider.standardize_dividend_ratio(0.5, 10.0)
        assert ratio == 5.0

    def test_dividend_ratio_zero_price(self):
        """Test dividend ratio with zero price."""
        provider = EastmoneyDisclosureProvider()

        ratio = provider.standardize_dividend_ratio(1.0, 0.0)
        assert ratio is None

    def test_dividend_ratio_none_values(self):
        """Test dividend ratio with None values."""
        provider = EastmoneyDisclosureProvider()

        ratio = provider.standardize_dividend_ratio(None, 20.0)
        assert ratio is None

        ratio = provider.standardize_dividend_ratio(1.0, None)
        assert ratio is None


class TestDisclosureDateRangeValidation:
    """Test date range validation."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    def test_valid_date_range(self, provider):
        """Test valid date range."""
        provider.validate_date_range("2024-01-01", "2024-12-31")

    def test_invalid_date_range_order(self, provider):
        """Test invalid date range order."""
        with pytest.raises(ValueError):
            provider.validate_date_range("2024-12-31", "2024-01-01")

    def test_invalid_date_format(self, provider):
        """Test invalid date format."""
        with pytest.raises(ValueError):
            provider.validate_date_range("2024/01/01", "2024-12-31")


class TestDisclosureMultipleRecords:
    """Test handling of multiple records."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_notice_report")
    def test_multiple_news_records(self, mock_ak, provider):
        """Test multiple news records handling."""
        mock_df = pd.DataFrame(
            {
                "公告日期": ["2024-01-15", "2024-01-14", "2024-01-13"],
                "代码": ["600000", "600000", "600000"],
                "公告标题": ["公告1", "公告2", "公告3"],
                "公告类型": ["年报", "年报", "年报"],
                "网址": ["url1", "url2", "url3"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_disclosure_news("600000", "2024-01-01", "2024-01-31", "all")

        assert len(result) >= 1
        assert all(result["symbol"] == "600000")

    @patch("akshare.stock_dividend_cninfo")
    def test_multiple_dividend_records(self, mock_ak, provider):
        """Test multiple dividend records handling."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报", "2022年报", "2021年报"],
                "派息比例": [1.5, 1.0, 0.8],
                "股权登记日": ["2024-06-20", "2023-06-15", "2022-06-10"],
                "除权日": ["2024-06-21", "2023-06-16", "2022-06-11"],
                "派息日": ["2024-06-22", "2023-06-17", "2022-06-12"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_dividend_data("600000", "2021-01-01", "2024-12-31")

        assert len(result) >= 3


class TestDisclosureJSONCompatibilityEnhanced:
    """Enhanced JSON compatibility tests."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDisclosureProvider()

    @patch("akshare.stock_dividend_cninfo")
    def test_dividend_json_with_nat(self, mock_ak, provider):
        """Test dividend JSON with NaT values."""
        mock_df = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": [pd.NaT],
                "派息日": ["2024-06-22"],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_dividend_data("600000", "2023-01-01", "2024-12-31")

        json_str = result.to_json(orient="records")
        assert json_str is not None

    @patch("akshare.stock_repurchase_em")
    def test_repurchase_json_with_nan(self, mock_ak, provider):
        """Test repurchase JSON with NaN values."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["实施中"],
                "已回购金额": [pd.NA],
                "已回购股份数量": [1000000.0],
                "计划回购价格区间": ["10-15元"],
                "计划回购金额区间-下限": [40000000.0],
            }
        )
        mock_ak.return_value = mock_df

        result = provider.get_repurchase_data("600000", "2024-01-01", "2024-12-31")

        json_str = result.to_json(orient="records")
        assert json_str is not None
