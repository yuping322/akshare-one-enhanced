"""
Additional tests for restricted module to increase coverage.
"""

from unittest.mock import patch
import pandas as pd
import pytest
from akshare_one.modules.restricted.eastmoney import EastmoneyRestrictedReleaseProvider


class TestRestrictedMissingBranches:
    """Test missing branches to increase coverage."""

    @pytest.fixture
    def provider(self):
        return EastmoneyRestrictedReleaseProvider()

    @patch("akshare.stock_restricted_release_queue_em")
    def test_上市日期_column(self, mock_release, provider):
        """Test handling 上市日期 column."""
        mock_data = pd.DataFrame(
            {
                "上市日期": ["2024-01-15"],
                "解禁数量": [10000000.0],
                "解禁市值": [150000000.0],
                "股份类型": ["首发原股东限售股份"],
                "股东名称": ["股东A"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release("600000", "2024-01-01", "2024-12-31")
        assert result["release_date"].iloc[0] == "2024-01-15"

    @patch("akshare.stock_restricted_release_queue_em")
    def test_实际解禁数量_column(self, mock_release, provider):
        """Test handling 实际解禁数量 column."""
        mock_data = pd.DataFrame(
            {
                "解禁时间": ["2024-01-15"],
                "实际解禁数量": [10000000.0],
                "解禁市值": [150000000.0],
                "股份类型": ["首发原股东限售股份"],
                "股东名称": ["股东A"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release("600000", "2024-01-01", "2024-12-31")
        assert result["release_shares"].iloc[0] == 10000000.0

    @patch("akshare.stock_restricted_release_queue_em")
    def test_实际解禁市值_column(self, mock_release, provider):
        """Test handling 实际解禁市值 column."""
        mock_data = pd.DataFrame(
            {
                "解禁时间": ["2024-01-15"],
                "解禁数量": [10000000.0],
                "实际解禁市值": [150000000.0],
                "股份类型": ["首发原股东限售股份"],
                "股东名称": ["股东A"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release("600000", "2024-01-01", "2024-12-31")
        assert result["release_value"].iloc[0] == 150000000.0

    @patch("akshare.stock_restricted_release_queue_em")
    def test_限售股类型_column(self, mock_release, provider):
        """Test handling 限售股类型 column."""
        mock_data = pd.DataFrame(
            {
                "解禁时间": ["2024-01-15"],
                "解禁数量": [10000000.0],
                "解禁市值": [150000000.0],
                "限售股类型": ["定向增发机构配售股份"],
                "股东名称": ["股东A"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release("600000", "2024-01-01", "2024-12-31")
        assert result["release_type"].iloc[0] == "定向增发机构配售股份"

    @patch("akshare.stock_restricted_release_queue_em")
    def test_missing_股东名称(self, mock_release, provider):
        """Test handling missing 股东名称 column."""
        mock_data = pd.DataFrame(
            {
                "解禁时间": ["2024-01-15"],
                "解禁数量": [10000000.0],
                "解禁市值": [150000000.0],
                "股份类型": ["首发原股东限售股份"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release("600000", "2024-01-01", "2024-12-31")
        assert result["shareholder_name"].iloc[0] == ""

    @patch("akshare.stock_restricted_release_detail_em")
    def test_all_stocks_上市日期(self, mock_release, provider):
        """Test handling 上市日期 column for all stocks."""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "上市日期": ["2024-01-15"],
                "实际解禁数量": [10000000.0],
                "实际解禁市值": [150000000.0],
                "限售股类型": ["首发原股东限售股份"],
            }
        )
        mock_release.return_value = mock_data

        result = provider.get_restricted_release(None, "2024-01-01", "2024-12-31")
        assert result["release_date"].iloc[0] == "2024-01-15"
        assert result["release_shares"].iloc[0] == 10000000.0
        assert result["release_value"].iloc[0] == 150000000.0

    @patch("akshare.stock_restricted_release_detail_em")
    def test_all_stocks_missing_columns(self, mock_release, provider):
        """Test handling missing columns for all stocks."""
        mock_data = pd.DataFrame({"股票代码": ["600000"]})
        mock_release.return_value = mock_data

        result = provider.get_restricted_release(None, "2024-01-01", "2024-12-31")
        assert result["release_date"].iloc[0] == ""
        assert result["release_shares"].iloc[0] == 0.0
        assert result["release_value"].iloc[0] == 0.0

    @patch("akshare.stock_restricted_release_detail_em")
    def test_calendar_上市日期(self, mock_release, provider):
        """Test handling 上市日期 column in calendar."""
        mock_data = pd.DataFrame({"股票代码": ["600000"], "上市日期": ["2024-01-15"], "实际解禁市值": [150000000.0]})
        mock_release.return_value = mock_data

        result = provider.get_restricted_release_calendar("2024-01-01", "2024-12-31")
        assert result["date"].iloc[0] == "2024-01-15"
        assert result["total_release_value"].iloc[0] == 150000000.0
