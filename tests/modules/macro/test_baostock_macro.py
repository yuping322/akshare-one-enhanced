"""
Unit tests for Baostock Macro Provider

This module tests the Baostock macro provider implementation
without requiring actual network connections to Baostock.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.akshare_one.modules.macro import MacroFactory
from src.akshare_one.modules.macro.baostock import BaostockMacroProvider


class TestBaostockMacroProvider(unittest.TestCase):
    """Test Baostock macro provider functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.mock_bs = MagicMock()
        cls.mock_bs.login.return_value.error_code = "0"
        cls.mock_bs.logout.return_value = None

    def test_provider_registration(self):
        """Test that Baostock provider is registered"""
        sources = MacroFactory.list_sources()
        self.assertIn("baostock", sources)

    def test_provider_creation(self):
        """Test that provider can be created"""
        with patch("baostock.login") as mock_login:
            mock_login.return_value.error_code = "0"
            provider = MacroFactory.get_provider("baostock")
            self.assertIsInstance(provider, BaostockMacroProvider)
            self.assertEqual(provider.get_source_name(), "baostock")

    def test_deposit_rate_data_structure(self):
        """Test deposit rate data structure"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = ["date", "rate", "rateType"]
        mock_result.next.return_value = True
        mock_result.get_row_data.return_value = ["2024-01-01", "2.5", "活期存款"]

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_deposit_rate_data.return_value = mock_result
            mock_result.next.side_effect = [True, False]  # One row, then stop

            df = provider.get_deposit_rate_data("2024-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn("date", df.columns)
            self.assertIn("deposit_rate", df.columns)
            self.assertIn("deposit_rate_type", df.columns)

    def test_loan_rate_data_structure(self):
        """Test loan rate data structure"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = ["date", "rate", "rateType"]
        mock_result.next.return_value = True
        mock_result.get_row_data.return_value = ["2024-01-01", "4.5", "短期贷款"]

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_loan_rate_data.return_value = mock_result
            mock_result.next.side_effect = [True, False]

            df = provider.get_loan_rate_data("2024-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn("date", df.columns)
            self.assertIn("loan_rate", df.columns)
            self.assertIn("loan_rate_type", df.columns)

    def test_reserve_ratio_data_structure(self):
        """Test reserve ratio data structure"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = ["date", "reserveRatio", "reserveType"]
        mock_result.next.return_value = True
        mock_result.get_row_data.return_value = ["2024-01-01", "12.5", "大型金融机构"]

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_required_reserve_ratio_data.return_value = mock_result
            mock_result.next.side_effect = [True, False]

            df = provider.get_required_reserve_ratio_data("2024-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn("date", df.columns)
            self.assertIn("reserve_ratio", df.columns)
            self.assertIn("reserve_ratio_type", df.columns)

    def test_money_supply_month_structure(self):
        """Test monthly money supply data structure"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = [
            "date",
            "m0",
            "m1",
            "m2",
            "m0YoY",
            "m1YoY",
            "m2YoY",
            "m0MonthYoY",
            "m1MonthYoY",
            "m2MonthYoY",
        ]
        mock_result.next.return_value = True
        mock_result.get_row_data.return_value = [
            "2024-01-01",
            "100000",
            "200000",
            "300000",
            "5.0",
            "6.0",
            "7.0",
            "1.0",
            "1.5",
            "2.0",
        ]

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_money_supply_data_month.return_value = mock_result
            mock_result.next.side_effect = [True, False]

            df = provider.get_money_supply_data_month("2024-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn("date", df.columns)
            self.assertIn("m0", df.columns)
            self.assertIn("m1", df.columns)
            self.assertIn("m2", df.columns)
            self.assertIn("m0_yoy", df.columns)
            self.assertIn("m1_yoy", df.columns)
            self.assertIn("m2_yoy", df.columns)

    def test_money_supply_year_structure(self):
        """Test yearly money supply data structure"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = ["year", "m0", "m1", "m2", "m0YoY", "m1YoY", "m2YoY"]
        mock_result.next.return_value = True
        mock_result.get_row_data.return_value = ["2024", "100000", "200000", "300000", "5.0", "6.0", "7.0"]

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_money_supply_data_year.return_value = mock_result
            mock_result.next.side_effect = [True, False]

            df = provider.get_money_supply_data_year("2020-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn("date", df.columns)
            self.assertIn("m0", df.columns)
            self.assertIn("m1", df.columns)
            self.assertIn("m2", df.columns)

    def test_empty_result(self):
        """Test handling of empty results"""
        mock_result = MagicMock()
        mock_result.error_code = "0"
        mock_result.error_msg = ""
        mock_result.fields = ["date", "rate", "rateType"]
        mock_result.next.return_value = False

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_deposit_rate_data.return_value = mock_result

            df = provider.get_deposit_rate_data("2024-01-01", "2024-12-31")

            self.assertIsInstance(df, pd.DataFrame)
            self.assertTrue(df.empty)

    def test_error_handling(self):
        """Test handling of API errors"""
        mock_result = MagicMock()
        mock_result.error_code = "1"
        mock_result.error_msg = "Query failed"

        provider = BaostockMacroProvider.__new__(BaostockMacroProvider)
        provider.logger = MagicMock()

        with patch.object(provider, "_bs_instance") as mock_bs:
            mock_bs.query_deposit_rate_data.return_value = mock_result

            with self.assertRaises(RuntimeError):
                provider.get_deposit_rate_data("2024-01-01", "2024-12-31")


if __name__ == "__main__":
    unittest.main()
