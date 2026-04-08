"""
Additional tests for limitup module to increase coverage.
"""

from unittest.mock import patch
import pandas as pd
import pytest
from akshare_one.modules.limitup.eastmoney import EastmoneyLimitUpDownProvider


class TestLimitUpDownMissingBranches:
    """Test missing branches to increase coverage."""

    @pytest.fixture
    def provider(self):
        return EastmoneyLimitUpDownProvider()

    @patch("akshare.stock_zt_pool_em")
    def test_首次封板时间_column(self, mock_zt, provider):
        """Test handling 首次封板时间 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "首次封板时间": ["09:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["limit_up_time"].iloc[0] == "09:30:00"

    @patch("akshare.stock_zt_pool_em")
    def test_最后封板时间_column(self, mock_zt, provider):
        """Test handling 最后封板时间 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "最后封板时间": ["14:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["limit_up_time"].iloc[0] == "14:30:00"

    @patch("akshare.stock_zt_pool_em")
    def test_missing_limit_up_time(self, mock_zt, provider):
        """Test handling missing limit up time column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["limit_up_time"].iloc[0] == ""

    @patch("akshare.stock_zt_pool_em")
    def test_炸板次数_column(self, mock_zt, provider):
        """Test handling 炸板次数 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "炸板次数": [5],
                "封单金额": [50000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["open_count"].iloc[0] == 5

    @patch("akshare.stock_zt_pool_em")
    def test_封单额_column(self, mock_zt, provider):
        """Test handling 封单额 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单额": [60000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["seal_amount"].iloc[0] == 60000000.0

    @patch("akshare.stock_zt_pool_em")
    def test_封板资金_column(self, mock_zt, provider):
        """Test handling 封板资金 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封板资金": [70000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["seal_amount"].iloc[0] == 70000000.0

    @patch("akshare.stock_zt_pool_em")
    def test_封单资金_column(self, mock_zt, provider):
        """Test handling 封单资金 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单资金": [80000000.0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["seal_amount"].iloc[0] == 80000000.0

    @patch("akshare.stock_zt_pool_em")
    def test_missing_seal_amount(self, mock_zt, provider):
        """Test handling missing seal amount column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "连板数": [1],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert pd.isna(result["seal_amount"].iloc[0])

    @patch("akshare.stock_zt_pool_em")
    def test_连续涨停_column(self, mock_zt, provider):
        """Test handling 连续涨停 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连续涨停": [3],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["consecutive_days"].iloc[0] == 3

    @patch("akshare.stock_zt_pool_em")
    def test_所属行业_column(self, mock_zt, provider):
        """Test handling 所属行业 column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连板数": [1],
                "所属行业": ["银行"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["reason"].iloc[0] == "银行"

    @patch("akshare.stock_zt_pool_em")
    def test_missing_reason(self, mock_zt, provider):
        """Test handling missing reason column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "连板数": [1],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["reason"].iloc[0] == ""

    @patch("akshare.stock_zt_pool_em")
    def test_missing_consecutive_days(self, mock_zt, provider):
        """Test handling missing consecutive days column."""
        mock_data = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.50],
                "涨停时间": ["09:30:00"],
                "打开次数": [0],
                "封单金额": [50000000.0],
                "涨停原因": ["板块联动"],
                "换手率": [5.5],
            }
        )
        mock_zt.return_value = mock_data

        result = provider.get_limit_up_pool("2024-01-02")
        assert result["consecutive_days"].iloc[0] == 1
