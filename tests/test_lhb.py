"""
Unit tests for dragon tiger list (龙虎榜) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.lhb import (
    get_dragon_tiger_broker_stats,
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
)
from akshare_one.modules.lhb.eastmoney import EastmoneyDragonTigerProvider
from akshare_one.modules.lhb import DragonTigerFactory


class TestDragonTigerFactory:
    """Test DragonTigerFactory class."""

    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = DragonTigerFactory.get_provider("eastmoney")
        assert isinstance(provider, EastmoneyDragonTigerProvider)

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            DragonTigerFactory.get_provider("invalid")

    def test_list_sources(self):
        """Test listing available sources."""
        sources = DragonTigerFactory.list_sources()
        assert "eastmoney" in sources


class TestEastmoneyDragonTigerProvider:
    """Test EastmoneyDragonTigerProvider class."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == "lhb"
        assert provider.get_source_name() == "eastmoney"
        assert provider.get_update_frequency() == "daily"
        assert provider.get_delay_minutes() == 1440

    @patch("akshare.stock_lhb_detail_em")
    def test_get_dragon_tiger_list_all_stocks(self, mock_lhb, provider):
        """Test getting dragon tiger list data for all stocks."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "代码": ["600000", "600036"],
                "名称": ["浦发银行", "招商银行"],
                "上榜日": ["2024-01-02", "2024-01-02"],
                "收盘价": [10.50, 35.20],
                "涨跌幅": [5.0, 3.5],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%"],
                "龙虎榜买入额": [50000000.0, 80000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0],
                "换手率": [5.5, 8.2],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "reason" in result.columns
        assert "buy_amount" in result.columns
        assert "sell_amount" in result.columns
        assert "net_amount" in result.columns
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_lhb_detail_em")
    def test_get_dragon_tiger_list_single_stock(self, mock_lhb, provider):
        """Test getting dragon tiger list data for single stock."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02", "600000")

        assert not result.empty
        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600000"

    @patch("akshare.stock_lhb_detail_em")
    def test_get_dragon_tiger_list_empty(self, mock_lhb, provider):
        """Test getting dragon tiger list with no data."""
        mock_lhb.return_value = pd.DataFrame()

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert result.empty
        assert "date" in result.columns
        assert "symbol" in result.columns

    @patch("akshare.stock_lhb_stock_statistic_em")
    def test_get_dragon_tiger_summary_by_stock(self, mock_stat, provider):
        """Test getting dragon tiger summary grouped by stock."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "代码": ["600000", "600036"],
                "名称": ["浦发银行", "招商银行"],
                "上榜次数": [5, 3],
                "龙虎榜净买额": [100000000.0, 50000000.0],
                "龙虎榜买入额": [200000000.0, 100000000.0],
                "龙虎榜卖出额": [100000000.0, 50000000.0],
                "龙虎榜总成交额": [300000000.0, 150000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "stock")

        assert not result.empty
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "list_count" in result.columns
        assert "net_buy_amount" in result.columns
        assert result["list_count"].iloc[0] == 5

    @patch("akshare.stock_lhb_traderstatistic_em")
    def test_get_dragon_tiger_summary_by_broker(self, mock_stat, provider):
        """Test getting dragon tiger summary grouped by broker."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "营业部名称": ["深股通专用", "机构专用"],
                "上榜次数": [100, 80],
                "买入额": [5000000000.0, 3000000000.0],
                "买入次数": [95, 75],
                "卖出额": [4000000000.0, 2500000000.0],
                "卖出次数": [90, 70],
                "龙虎榜成交金额": [9000000000.0, 5500000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "broker")

        assert not result.empty
        assert "broker_name" in result.columns
        assert "list_count" in result.columns
        assert "buy_amount" in result.columns
        assert "sell_amount" in result.columns
        assert result["list_count"].iloc[0] == 100

    @patch("akshare.stock_lhb_detail_em")
    def test_get_dragon_tiger_summary_by_reason(self, mock_detail, provider):
        """Test getting dragon tiger summary grouped by reason."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "代码": ["600000", "600036", "600000"],
                "上榜原因": ["涨幅偏离值达7%", "涨幅偏离值达7%", "换手率达20%"],
                "龙虎榜净买额": [20000000.0, 30000000.0, 10000000.0],
                "龙虎榜买入额": [50000000.0, 70000000.0, 30000000.0],
                "龙虎榜卖出额": [30000000.0, 40000000.0, 20000000.0],
                "龙虎榜成交额": [80000000.0, 110000000.0, 50000000.0],
            }
        )
        mock_detail.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "reason")

        assert not result.empty
        assert "reason" in result.columns
        assert "list_count" in result.columns
        assert "net_buy_amount" in result.columns

    def test_get_dragon_tiger_summary_invalid_group_by(self, provider):
        """Test invalid group_by parameter."""
        with pytest.raises(ValueError, match="Invalid group_by"):
            provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "invalid")

    @patch("akshare.stock_lhb_traderstatistic_em")
    def test_get_dragon_tiger_broker_stats(self, mock_stat, provider):
        """Test getting broker statistics."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "营业部名称": ["深股通专用", "机构专用", "某营业部"],
                "上榜次数": [100, 80, 60],
                "买入额": [5000000000.0, 3000000000.0, 2000000000.0],
                "买入次数": [95, 75, 55],
                "卖出额": [4000000000.0, 2500000000.0, 1800000000.0],
                "卖出次数": [90, 70, 50],
                "龙虎榜成交金额": [9000000000.0, 5500000000.0, 3800000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", 2)

        assert not result.empty
        assert len(result) == 2
        assert "rank" in result.columns
        assert "broker_name" in result.columns
        assert "list_count" in result.columns
        assert "buy_amount" in result.columns
        assert "sell_amount" in result.columns
        assert "net_amount" in result.columns
        assert result["rank"].iloc[0] == 1

    def test_get_dragon_tiger_broker_stats_invalid_top_n(self, provider):
        """Test invalid top_n parameter."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", 0)


class TestDragonTigerPublicAPI:
    """Test public API functions."""

    @patch("akshare.stock_lhb_detail_em")
    def test_get_dragon_tiger_list_api(self, mock_lhb):
        """Test get_dragon_tiger_list public API."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = get_dragon_tiger_list("2024-01-02")
        assert not result.empty
        assert "symbol" in result.columns

    @patch("akshare.stock_lhb_stock_statistic_em")
    def test_get_dragon_tiger_summary_api(self, mock_stat):
        """Test get_dragon_tiger_summary public API."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜次数": [5],
                "龙虎榜净买额": [100000000.0],
                "龙虎榜买入额": [200000000.0],
                "龙虎榜卖出额": [100000000.0],
                "龙虎榜总成交额": [300000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = get_dragon_tiger_summary("2024-01-01", "2024-01-31", "stock")
        assert not result.empty
        assert "symbol" in result.columns

    @patch("akshare.stock_lhb_traderstatistic_em")
    def test_get_dragon_tiger_broker_stats_api(self, mock_stat):
        """Test get_dragon_tiger_broker_stats public API."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "营业部名称": ["深股通专用"],
                "上榜次数": [100],
                "买入额": [5000000000.0],
                "买入次数": [95],
                "卖出额": [4000000000.0],
                "卖出次数": [90],
                "龙虎榜成交金额": [9000000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", 10)
        assert not result.empty
        assert "broker_name" in result.columns


class TestDragonTigerJSONCompatibility:
    """Test JSON compatibility of dragon tiger data."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_json_compatibility(self, mock_lhb, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        # Test JSON serialization
        json_str = result.to_json(orient="records")
        assert json_str is not None

        # Check no NaN values
        assert not result.isnull().any().any()

        # Check date is string
        assert result["date"].dtype in ["object", "string"]

        # Check symbol is string with leading zeros
        assert result["symbol"].dtype in ["object", "string"]
        assert result["symbol"].iloc[0] == "600000"


class TestLHBNetBuyCalculation:
    """Test net buy calculation logic."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_net_buy_calculation_accuracy(self, mock_lhb, provider):
        """Test net buy amount equals buy minus sell."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "代码": ["600000", "600036", "000001"],
                "名称": ["浦发银行", "招商银行", "平安银行"],
                "上榜日": ["2024-01-02", "2024-01-02", "2024-01-02"],
                "收盘价": [10.50, 35.20, 12.80],
                "涨跌幅": [5.0, 3.5, 2.8],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%", "涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0, 80000000.0, 30000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0, 25000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0, 5000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0, 55000000.0],
                "换手率": [5.5, 8.2, 4.3],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        # Verify net buy calculation
        for i in range(len(result)):
            calculated_net = result["buy_amount"].iloc[i] - result["sell_amount"].iloc[i]
            actual_net = result["net_amount"].iloc[i]
            assert abs(calculated_net - actual_net) < 100

    @patch("akshare.stock_lhb_detail_em")
    def test_net_buy_negative_values(self, mock_lhb, provider):
        """Test handling of negative net buy amounts."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [-5.0],
                "上榜原因": ["跌幅偏离值达7%"],
                "龙虎榜买入额": [20000000.0],
                "龙虎榜卖出额": [50000000.0],
                "龙虎榜净买额": [-30000000.0],
                "龙虎榜成交额": [70000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert result["net_amount"].iloc[0] < 0
        assert result["sell_amount"].iloc[0] > result["buy_amount"].iloc[0]


class TestLHBDateFiltering:
    """Test date filtering functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_single_date_query(self, mock_lhb, provider):
        """Test querying for a single date."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "代码": ["600000", "600036"],
                "名称": ["浦发银行", "招商银行"],
                "上榜日": ["2024-01-15", "2024-01-15"],
                "收盘价": [10.50, 35.20],
                "涨跌幅": [5.0, 3.5],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%"],
                "龙虎榜买入额": [50000000.0, 80000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0],
                "换手率": [5.5, 8.2],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-15")

        assert all(result["date"] == "2024-01-15")
        assert len(result) == 2

    def test_invalid_date_format(self, provider):
        """Test invalid date format raises error."""
        with pytest.raises(ValueError):
            provider.get_dragon_tiger_list("2024/01/02")

        with pytest.raises(ValueError):
            provider.get_dragon_tiger_list("invalid-date")


class TestLHBReasonAnalysis:
    """Test dragon tiger list reason analysis."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_reason_field_preserved(self, mock_lhb, provider):
        """Test reason field is preserved in output."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert "reason" in result.columns
        assert result["reason"].iloc[0] == "涨幅偏离值达7%"

    @patch("akshare.stock_lhb_detail_em")
    def test_multiple_reasons(self, mock_lhb, provider):
        """Test handling of different listing reasons."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3, 4],
                "代码": ["600000", "600036", "000001", "300750"],
                "名称": ["浦发银行", "招商银行", "平安银行", "宁德时代"],
                "上榜日": ["2024-01-02"] * 4,
                "收盘价": [10.50, 35.20, 12.80, 180.50],
                "涨跌幅": [5.0, 3.5, 2.8, 10.0],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%", "跌幅偏离值达7%", "连续三个交易日涨幅偏离值累计达20%"],
                "龙虎榜买入额": [50000000.0, 80000000.0, 30000000.0, 120000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0, 25000000.0, 90000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0, 5000000.0, 30000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0, 55000000.0, 210000000.0],
                "换手率": [5.5, 8.2, 4.3, 15.6],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        reasons = result["reason"].tolist()
        assert "涨幅偏离值达7%" in reasons
        assert "换手率达20%" in reasons
        assert "跌幅偏离值达7%" in reasons


class TestLHBBrokerRanking:
    """Test broker ranking functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_traderstatistic_em")
    def test_broker_ranking_order(self, mock_stat, provider):
        """Test brokers are ranked by total amount."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3, 4],
                "营业部名称": ["深股通专用", "机构专用", "华泰证券南京", "中信证券北京"],
                "上榜次数": [100, 80, 60, 40],
                "买入额": [5000000000.0, 3000000000.0, 2000000000.0, 1500000000.0],
                "买入次数": [95, 75, 55, 35],
                "卖出额": [4000000000.0, 2500000000.0, 1800000000.0, 1200000000.0],
                "卖出次数": [90, 70, 50, 30],
                "龙虎榜成交金额": [9000000000.0, 5500000000.0, 3800000000.0, 2700000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", 4)

        # Verify ranking by total amount (descending)
        total_amounts = result["total_amount"].tolist()
        assert total_amounts == sorted(total_amounts, reverse=True)

    @patch("akshare.stock_lhb_traderstatistic_em")
    def test_broker_net_amount_calculation(self, mock_stat, provider):
        """Test broker net amount equals buy minus sell."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "营业部名称": ["深股通专用"],
                "上榜次数": [100],
                "买入额": [5000000000.0],
                "买入次数": [95],
                "卖出额": [4000000000.0],
                "卖出次数": [90],
                "龙虎榜成交金额": [9000000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", 10)

        expected_net = result["buy_amount"].iloc[0] - result["sell_amount"].iloc[0]
        assert result["net_amount"].iloc[0] == expected_net


class TestLHBStockStatistics:
    """Test stock statistics functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_stock_statistic_em")
    def test_stock_list_count(self, mock_stat, provider):
        """Test stock list count field."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "代码": ["600000", "600036", "000001"],
                "名称": ["浦发银行", "招商银行", "平安银行"],
                "上榜次数": [10, 5, 3],
                "龙虎榜净买额": [100000000.0, 50000000.0, 30000000.0],
                "龙虎榜买入额": [200000000.0, 100000000.0, 60000000.0],
                "龙虎榜卖出额": [100000000.0, 50000000.0, 30000000.0],
                "龙虎榜总成交额": [300000000.0, 150000000.0, 90000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "stock")

        assert "list_count" in result.columns
        assert result["list_count"].iloc[0] == 10

    @patch("akshare.stock_lhb_stock_statistic_em")
    def test_stock_net_buy_aggregation(self, mock_stat, provider):
        """Test stock net buy aggregation."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜次数": [5],
                "龙虎榜净买额": [150000000.0],
                "龙虎榜买入额": [250000000.0],
                "龙虎榜卖出额": [100000000.0],
                "龙虎榜总成交额": [350000000.0],
            }
        )
        mock_stat.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "stock")

        # Net buy should be consistent
        calculated_net = result["buy_amount"].iloc[0] - result["sell_amount"].iloc[0]
        assert abs(result["net_buy_amount"].iloc[0] - calculated_net) < 100


class TestLHBDataConsistency:
    """Test data consistency checks."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_total_amount_equals_buy_plus_sell(self, mock_lhb, provider):
        """Test total amount equals buy amount plus sell amount."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        # Total amount should be close to buy + sell
        expected_total = result["buy_amount"].iloc[0] + result["sell_amount"].iloc[0]
        assert abs(result["total_amount"].iloc[0] - expected_total) < 100

    @patch("akshare.stock_lhb_detail_em")
    def test_turnover_rate_range(self, mock_lhb, provider):
        """Test turnover rate is within reasonable range."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "代码": ["600000", "300750"],
                "名称": ["浦发银行", "宁德时代"],
                "上榜日": ["2024-01-02", "2024-01-02"],
                "收盘价": [10.50, 180.50],
                "涨跌幅": [5.0, 10.0],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%"],
                "龙虎榜买入额": [50000000.0, 120000000.0],
                "龙虎榜卖出额": [30000000.0, 90000000.0],
                "龙虎榜净买额": [20000000.0, 30000000.0],
                "龙虎榜成交额": [80000000.0, 210000000.0],
                "换手率": [5.5, 25.8],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        # Turnover rate should be positive
        assert all(result["turnover_rate"] > 0)
        # Turnover rate should be less than 100% (reasonable range)
        assert all(result["turnover_rate"] < 100)


class TestLHBErrorHandling:
    """Test error handling scenarios."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_api_exception_handling(self, mock_lhb, provider):
        """Test handling of API exceptions."""
        mock_lhb.side_effect = Exception("API error")

        with pytest.raises(RuntimeError, match="Failed to fetch dragon tiger list data"):
            provider.get_dragon_tiger_list("2024-01-02")

    @patch("akshare.stock_lhb_stock_statistic_em")
    def test_summary_api_exception_handling(self, mock_stat, provider):
        """Test handling of summary API exceptions."""
        mock_stat.side_effect = Exception("API error")

        with pytest.raises(RuntimeError, match="Failed to fetch dragon tiger summary"):
            provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "stock")

    def test_invalid_symbol_in_filter(self, provider):
        """Test invalid symbol format raises error."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.get_dragon_tiger_list("2024-01-02", symbol="INVALID")

    def test_invalid_top_n_value(self, provider):
        """Test invalid top_n value raises error."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", top_n=0)

        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", top_n=-5)


class TestLHBFieldStandardization:
    """Test field standardization."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_symbol_zero_padding(self, mock_lhb, provider):
        """Test symbol zero padding."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2],
                "代码": ["1", "36"],
                "名称": ["测试股票A", "测试股票B"],
                "上榜日": ["2024-01-02", "2024-01-02"],
                "收盘价": [10.50, 35.20],
                "涨跌幅": [5.0, 3.5],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%"],
                "龙虎榜买入额": [50000000.0, 80000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0],
                "换手率": [5.5, 8.2],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert result["symbol"].iloc[0] == "000001"
        assert result["symbol"].iloc[1] == "000036"

    @patch("akshare.stock_lhb_detail_em")
    def test_date_format_conversion(self, mock_lhb, provider):
        """Test date format is standardized to YYYY-MM-DD."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert result["date"].iloc[0] == "2024-01-02"
        assert isinstance(result["date"].iloc[0], str)


class TestLHBSymbolFiltering:
    """Test symbol filtering functionality."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_symbol_filter_exact_match(self, mock_lhb, provider):
        """Test symbol filter returns exact match."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "代码": ["600000", "600036", "000001"],
                "名称": ["浦发银行", "招商银行", "平安银行"],
                "上榜日": ["2024-01-02", "2024-01-02", "2024-01-02"],
                "收盘价": [10.50, 35.20, 12.80],
                "涨跌幅": [5.0, 3.5, 2.8],
                "上榜原因": ["涨幅偏离值达7%", "换手率达20%", "涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0, 80000000.0, 30000000.0],
                "龙虎榜卖出额": [30000000.0, 60000000.0, 25000000.0],
                "龙虎榜净买额": [20000000.0, 20000000.0, 5000000.0],
                "龙虎榜成交额": [80000000.0, 140000000.0, 55000000.0],
                "换手率": [5.5, 8.2, 4.3],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02", symbol="600036")

        assert len(result) == 1
        assert result["symbol"].iloc[0] == "600036"
        assert result["name"].iloc[0] == "招商银行"

    @patch("akshare.stock_lhb_detail_em")
    def test_symbol_filter_no_match(self, mock_lhb, provider):
        """Test symbol filter returns empty when no match."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [50000000.0],
                "龙虎榜卖出额": [30000000.0],
                "龙虎榜净买额": [20000000.0],
                "龙虎榜成交额": [80000000.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02", symbol="999999")

        assert result.empty
        assert "symbol" in result.columns


class TestLHBReasonGrouping:
    """Test reason grouping in summary."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_reason_grouping_aggregation(self, mock_detail, provider):
        """Test reason grouping aggregates correctly."""
        mock_data = pd.DataFrame(
            {
                "序号": [1, 2, 3, 4, 5],
                "代码": ["600000", "600036", "000001", "600000", "600036"],
                "上榜原因": ["涨幅偏离值达7%", "涨幅偏离值达7%", "跌幅偏离值达7%", "换手率达20%", "换手率达20%"],
                "龙虎榜净买额": [20000000.0, 30000000.0, -5000000.0, 10000000.0, 15000000.0],
                "龙虎榜买入额": [50000000.0, 70000000.0, 30000000.0, 30000000.0, 40000000.0],
                "龙虎榜卖出额": [30000000.0, 40000000.0, 35000000.0, 20000000.0, 25000000.0],
                "龙虎榜成交额": [80000000.0, 110000000.0, 65000000.0, 50000000.0, 65000000.0],
            }
        )
        mock_detail.return_value = mock_data

        result = provider.get_dragon_tiger_summary("2024-01-01", "2024-01-31", "reason")

        assert "reason" in result.columns
        assert "list_count" in result.columns

        # Check aggregation by reason
        reason_counts = result.groupby("reason")["list_count"].sum()
        assert reason_counts.get("涨幅偏离值达7%", 0) == 2
        assert reason_counts.get("换手率达20%", 0) == 2


class TestLHBMultipleDataTypes:
    """Test handling of different data types."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()

    @patch("akshare.stock_lhb_detail_em")
    def test_numeric_type_conversion(self, mock_lhb, provider):
        """Test numeric fields are converted to float."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": ["10.50"],
                "涨跌幅": ["5.0"],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": ["50000000"],
                "龙虎榜卖出额": ["30000000"],
                "龙虎榜净买额": ["20000000"],
                "龙虎榜成交额": ["80000000"],
                "换手率": ["5.5"],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert isinstance(result["close_price"].iloc[0], float)
        assert isinstance(result["buy_amount"].iloc[0], float)

    @patch("akshare.stock_lhb_detail_em")
    def test_large_amount_values(self, mock_lhb, provider):
        """Test handling of large amount values."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "上榜日": ["2024-01-02"],
                "收盘价": [10.50],
                "涨跌幅": [5.0],
                "上榜原因": ["涨幅偏离值达7%"],
                "龙虎榜买入额": [999999999999.0],
                "龙虎榜卖出额": [888888888888.0],
                "龙虎榜净买额": [111111111111.0],
                "龙虎榜成交额": [1888888888887.0],
                "换手率": [5.5],
            }
        )
        mock_lhb.return_value = mock_data

        result = provider.get_dragon_tiger_list("2024-01-02")

        assert result["buy_amount"].iloc[0] == 999999999999.0
        assert result["net_amount"].iloc[0] == 111111111111.0
