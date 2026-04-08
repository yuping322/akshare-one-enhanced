"""
Unit tests for macro economic data module.
"""

import json
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate,
    get_social_financing,
)
from akshare_one.modules.macro import MacroFactory
from akshare_one.modules.macro.official import OfficialMacroProvider


class TestMacroFactory:
    """Test MacroFactory class."""

    def test_get_provider_official(self):
        """Test getting official provider."""
        provider = MacroFactory.get_provider("official")
        assert isinstance(provider, OfficialMacroProvider)

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            MacroFactory.get_provider("invalid")

    def test_list_sources(self):
        """Test listing available sources."""
        sources = MacroFactory.list_sources()
        assert "official" in sources


class TestOfficialMacroProvider:
    """Test OfficialMacroProvider class."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return OfficialMacroProvider()

    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == "macro"
        assert provider.get_source_name() == "official"
        assert provider.get_update_frequency() == "monthly"
        assert provider.get_delay_minutes() == 0

    @patch("akshare.macro_china_lpr")
    def test_get_lpr_rate(self, mock_lpr, provider):
        """Test getting LPR rate data."""
        mock_data = pd.DataFrame(
            {"TRADE_DATE": ["2024-01-20", "2024-02-20"], "LPR1Y": [3.45, 3.45], "LPR5Y": [4.20, 4.20]}
        )
        mock_lpr.return_value = mock_data

        result = provider.get_lpr_rate("2024-01-01", "2024-12-31")

        assert not result.empty
        assert "date" in result.columns
        assert "lpr_1y" in result.columns
        assert "lpr_5y" in result.columns
        assert result["date"].dtype in ["object", "string"]

    @patch("akshare.macro_china_pmi")
    def test_get_pmi_manufacturing(self, mock_pmi, provider):
        """Test getting manufacturing PMI data."""
        mock_data = pd.DataFrame({"日期": ["2024-01-01", "2024-02-01"], "制造业-指数": [50.2, 50.5]})
        mock_pmi.return_value = mock_data

        result = provider.get_pmi_index("2024-01-01", "2024-12-31", "manufacturing")

        assert not result.empty
        assert "date" in result.columns
        assert "pmi_value" in result.columns

    @patch("akshare.macro_china_cpi")
    def test_get_cpi_data(self, mock_cpi, provider):
        """Test getting CPI data."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024-01-01", "2024-02-01"],
                "当月": [100.0, 100.5],
                "同比增长": [2.1, 2.2],
                "环比增长": [0.1, 0.2],
                "累计": [100.0, 100.5],
            }
        )
        mock_cpi.return_value = mock_data

        result = provider.get_cpi_data("2024-01-01", "2024-12-31")

        assert not result.empty
        assert "date" in result.columns
        assert "current" in result.columns
        assert "yoy" in result.columns
        assert "mom" in result.columns

    @patch("akshare.macro_china_m2_yearly")
    def test_get_m2_supply(self, mock_m2, provider):
        """Test getting M2 supply data."""
        mock_data = pd.DataFrame(
            {"月份": ["2024-01-01", "2024-02-01"], "M2数量(亿元)": [2500000, 2510000], "M2同比增长": [8.5, 8.6]}
        )
        mock_m2.return_value = mock_data

        result = provider.get_m2_supply("2024-01-01", "2024-12-31")

        assert not result.empty
        assert "date" in result.columns
        assert "m2_balance" in result.columns
        assert "yoy_growth_rate" in result.columns

    @patch("akshare.macro_china_shibor_all")
    def test_get_shibor_rate(self, mock_shibor, provider):
        """Test getting Shibor rate data."""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "隔夜": [1.5, 1.6],
                "1周": [1.8, 1.9],
                "2周": [2.0, 2.1],
                "1月": [2.2, 2.3],
                "3月": [2.5, 2.6],
                "6月": [2.8, 2.9],
                "9月": [3.0, 3.1],
                "1年": [3.2, 3.3],
            }
        )
        mock_shibor.return_value = mock_data

        result = provider.get_shibor_rate("2024-01-01", "2024-12-31")

        assert not result.empty
        assert "date" in result.columns
        assert "overnight" in result.columns
        assert "year_1" in result.columns

    def test_invalid_pmi_type(self, provider):
        """Test invalid PMI type."""
        with pytest.raises(ValueError, match="Invalid pmi_type"):
            provider.get_pmi_index("2024-01-01", "2024-12-31", "invalid")

    @patch("akshare.macro_china_lpr")
    def test_get_lpr_rate_basic(self, mock_lpr, provider):
        """Test LPR rate basic functionality."""
        mock_data = pd.DataFrame(
            {
                "TRADE_DATE": ["2024-01-20", "2024-02-20", "2024-03-20"],
                "LPR1Y": [3.45, 3.45, 3.45],
                "LPR5Y": [4.20, 4.20, 3.95],
            }
        )
        mock_lpr.return_value = mock_data

        result = provider.get_lpr_rate("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 3
        assert "date" in result.columns
        assert "lpr_1y" in result.columns
        assert "lpr_5y" in result.columns
        assert result["lpr_1y"].dtype in ["float64", "float32"]
        assert result["lpr_5y"].dtype in ["float64", "float32"]
        assert all(result["lpr_1y"] == 3.45)
        assert result["lpr_5y"].iloc[0] == 4.20
        assert result["lpr_5y"].iloc[2] == 3.95

    @patch("akshare.macro_china_lpr")
    def test_get_lpr_rate_with_date_range(self, mock_lpr, provider):
        """Test LPR rate with date range filtering."""
        mock_data = pd.DataFrame(
            {
                "TRADE_DATE": ["2024-01-20", "2024-02-20", "2024-03-20", "2024-04-20"],
                "LPR1Y": [3.45, 3.45, 3.45, 3.45],
                "LPR5Y": [4.20, 4.20, 3.95, 3.95],
            }
        )
        mock_lpr.return_value = mock_data

        result = provider.get_lpr_rate("2024-02-01", "2024-03-31")

        assert not result.empty
        assert len(result) == 2
        assert result["date"].iloc[0] == "2024-02-20"
        assert result["date"].iloc[1] == "2024-03-20"

    @patch("akshare.macro_china_pmi")
    def test_get_pmi_index_manufacturing(self, mock_pmi, provider):
        """Test PMI manufacturing data."""
        mock_data = pd.DataFrame(
            {"月份": ["2024年01月份", "2024年02月份"], "制造业-指数": [49.2, 49.1], "制造业-同比增长": [0.5, 0.3]}
        )
        mock_pmi.return_value = mock_data

        result = provider.get_pmi_index("2024-01-01", "2024-12-31", "manufacturing")

        assert not result.empty
        assert "date" in result.columns
        assert "pmi_value" in result.columns
        assert "yoy" in result.columns
        assert result["pmi_value"].iloc[0] == 49.2
        assert result["date"].iloc[0] == "2024-01-01"

    @patch("akshare.macro_china_non_man_pmi")
    def test_get_pmi_index_non_manufacturing(self, mock_pmi, provider):
        """Test PMI non-manufacturing data."""
        mock_data = pd.DataFrame(
            {"月份": ["2024年01月份", "2024年02月份"], "非制造业-指数": [50.3, 51.0], "非制造业-同比增长": [1.2, 1.5]}
        )
        mock_pmi.return_value = mock_data

        result = provider.get_pmi_index("2024-01-01", "2024-12-31", "non_manufacturing")

        assert not result.empty
        assert "pmi_value" in result.columns
        assert result["pmi_value"].iloc[0] == 50.3
        assert result["date"].iloc[0] == "2024-01-01"

    def test_get_pmi_index_caixin(self, provider):
        """Test Caixin PMI data."""
        pytest.skip("akshare does not have macro_china_cx_pmi function")

    @patch("akshare.macro_china_cpi")
    def test_get_cpi_data_basic(self, mock_cpi, provider):
        """Test CPI data basic functionality."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024年01月份", "2024年02月份"],
                "当月": [100.5, 100.8],
                "同比增长": [2.1, 2.3],
                "环比增长": [0.3, 0.5],
                "累计": [100.5, 100.8],
            }
        )
        mock_cpi.return_value = mock_data

        result = provider.get_cpi_data("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "current" in result.columns
        assert "yoy" in result.columns
        assert "mom" in result.columns
        assert "cumulative" in result.columns
        assert result["current"].iloc[0] == 100.5
        assert result["yoy"].iloc[0] == 2.1

    @patch("akshare.macro_china_cpi")
    def test_get_cpi_data_field_validation(self, mock_cpi, provider):
        """Test CPI data field validation."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024年01月份", "2024年02月份"],
                "当月": [100.5, 100.8],
                "同比增长": [2.1, 2.3],
                "环比增长": [0.3, 0.5],
                "累计": [100.5, 100.8],
            }
        )
        mock_cpi.return_value = mock_data

        result = provider.get_cpi_data("2024-01-01", "2024-12-31")

        assert list(result.columns) == ["date", "current", "yoy", "mom", "cumulative"]
        assert result["date"].dtype in ["object", "string"] or str(result["date"].dtype).startswith("StringDtype")
        assert result["current"].dtype in ["float64", "float32", "int64", "int32"]
        assert result["yoy"].dtype in ["float64", "float32", "int64", "int32"]

    @patch("akshare.macro_china_ppi")
    def test_get_ppi_data_basic(self, mock_ppi, provider):
        """Test PPI data basic functionality."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024年01月份", "2024年02月份"],
                "当月": [98.5, 98.3],
                "同比增长": [-2.5, -2.7],
                "环比增长": [-0.2, -0.1],
                "累计": [98.5, 98.3],
            }
        )
        mock_ppi.return_value = mock_data

        result = provider.get_ppi_data("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "current" in result.columns
        assert "yoy" in result.columns
        assert "mom" in result.columns
        assert "cumulative" in result.columns
        assert result["current"].iloc[0] == 98.5
        assert result["yoy"].iloc[0] == -2.5

    @patch("akshare.macro_china_m2_yearly")
    def test_get_m2_supply_basic(self, mock_m2, provider):
        """Test M2 supply basic functionality."""
        mock_data = pd.DataFrame(
            {
                "商品": ["M2", "M2"],
                "日期": ["2024-01-01", "2024-02-01"],
                "今值": [8.7, 8.8],
                "预测值": [8.6, 8.7],
                "前值": [8.5, 8.7],
            }
        )
        mock_m2.return_value = mock_data

        result = provider.get_m2_supply("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "m2_balance" in result.columns
        assert "yoy_growth_rate" in result.columns
        assert result["yoy_growth_rate"].iloc[0] == 8.7
        assert result["m2_balance"].iloc[0] is None

    @patch("akshare.macro_china_shibor_all")
    def test_get_shibor_rate_basic(self, mock_shibor, provider):
        """Test Shibor rate basic functionality."""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-02", "2024-01-03"],
                "O/N-定价": [1.5230, 1.5340],
                "1W-定价": [1.7890, 1.7950],
                "2W-定价": [1.8760, 1.8820],
                "1M-定价": [2.1050, 2.1120],
                "3M-定价": [2.3450, 2.3520],
                "6M-定价": [2.4560, 2.4630],
                "9M-定价": [2.5670, 2.5740],
                "1Y-定价": [2.6780, 2.6850],
            }
        )
        mock_shibor.return_value = mock_data

        result = provider.get_shibor_rate("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "overnight" in result.columns
        assert "week_1" in result.columns
        assert "week_2" in result.columns
        assert "month_1" in result.columns
        assert "month_3" in result.columns
        assert "month_6" in result.columns
        assert "month_9" in result.columns
        assert "year_1" in result.columns
        assert result["overnight"].iloc[0] == 1.5230
        assert result["year_1"].iloc[0] == 2.6780

    @patch("akshare.macro_china_shibor_all")
    def test_get_shibor_rate_old_format(self, mock_shibor, provider):
        """Test Shibor rate with old format columns."""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-02", "2024-01-03"],
                "隔夜": [1.5230, 1.5340],
                "1周": [1.7890, 1.7950],
                "2周": [1.8760, 1.8820],
                "1月": [2.1050, 2.1120],
                "3月": [2.3450, 2.3520],
                "6月": [2.4560, 2.4630],
                "9月": [2.5670, 2.5740],
                "1年": [2.6780, 2.6850],
            }
        )
        mock_shibor.return_value = mock_data

        result = provider.get_shibor_rate("2024-01-01", "2024-12-31")

        assert not result.empty
        assert "overnight" in result.columns
        assert "year_1" in result.columns
        assert result["overnight"].iloc[0] == 1.5230

    @patch("akshare.macro_china_shrzgm")
    def test_get_social_financing_basic(self, mock_sf, provider):
        """Test social financing basic functionality."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024-01-01", "2024-02-01"],
                "社会融资规模增量(亿元)": [65000.0, 15200.0],
                "新增人民币贷款(亿元)": [49000.0, 14500.0],
            }
        )
        mock_sf.return_value = mock_data

        result = provider.get_social_financing("2024-01-01", "2024-12-31")

        assert not result.empty
        assert len(result) == 2
        assert "date" in result.columns
        assert "total_scale" in result.columns
        assert "yoy" in result.columns
        assert "mom" in result.columns
        assert "new_rmb_loans" in result.columns
        assert result["total_scale"].iloc[0] == 65000.0
        assert result["new_rmb_loans"].iloc[0] == 49000.0
        assert result["yoy"].iloc[0] is None
        assert result["mom"].iloc[0] is None

    @patch("akshare.macro_china_lpr")
    def test_macro_data_json_compatibility(self, mock_lpr, provider):
        """Test that macro data is JSON serializable."""
        mock_data = pd.DataFrame(
            {"TRADE_DATE": ["2024-01-20", "2024-02-20"], "LPR1Y": [3.45, 3.45], "LPR5Y": [4.20, 3.95]}
        )
        mock_lpr.return_value = mock_data

        result = provider.get_lpr_rate("2024-01-01", "2024-12-31")

        try:
            json_str = result.to_json(orient="records")
            json_data = json.loads(json_str)
            assert isinstance(json_data, list)
            assert len(json_data) == 2
            assert "date" in json_data[0]
            assert "lpr_1y" in json_data[0]
            assert "lpr_5y" in json_data[0]
        except Exception as e:
            pytest.fail(f"Data is not JSON compatible: {e}")

    @patch("akshare.macro_china_pmi")
    def test_macro_data_field_standardization(self, mock_pmi, provider):
        """Test that data fields are standardized."""
        mock_data = pd.DataFrame({"月份": ["2024年01月份"], "制造业-指数": [50.5], "制造业-同比增长": [0.8]})
        mock_pmi.return_value = mock_data

        result = provider.get_pmi_index("2024-01-01", "2024-12-31", "manufacturing")

        assert "date" in result.columns
        assert "pmi_value" in result.columns
        assert "yoy" in result.columns
        assert "mom" in result.columns
        assert result["date"].iloc[0] == "2024-01-01"

    @patch("akshare.macro_china_lpr")
    def test_empty_dataframe_handling(self, mock_lpr, provider):
        """Test handling of empty dataframes."""
        mock_lpr.return_value = pd.DataFrame()

        result = provider.get_lpr_rate("2024-01-01", "2024-12-31")

        assert result.empty
        assert "date" in result.columns
        assert "lpr_1y" in result.columns
        assert "lpr_5y" in result.columns

    @patch("akshare.macro_china_cpi")
    def test_numeric_conversion(self, mock_cpi, provider):
        """Test that numeric values are properly converted."""
        mock_data = pd.DataFrame(
            {"月份": ["2024年01月份"], "当月": ["100.5"], "同比增长": ["2.1"], "环比增长": ["0.3"], "累计": ["100.5"]}
        )
        mock_cpi.return_value = mock_data

        result = provider.get_cpi_data("2024-01-01", "2024-12-31")

        assert not result.empty
        assert result["current"].dtype in ["float64", "float32"]
        assert result["yoy"].dtype in ["float64", "float32"]

    @patch("akshare.macro_china_lpr")
    def test_error_handling(self, mock_lpr, provider):
        """Test error handling when API fails."""
        mock_lpr.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch LPR rate data"):
            provider.get_lpr_rate("2024-01-01", "2024-12-31")


class TestMacroDataValidation:
    """Test data validation and edge cases."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return OfficialMacroProvider()

    def test_date_validation(self, provider):
        """Test date validation."""
        with pytest.raises(ValueError):
            provider.get_lpr_rate("2024-12-31", "2024-01-01")

    @patch("akshare.macro_china_lpr")
    def test_date_range_filtering(self, mock_lpr, provider):
        """Test that date range filtering works correctly."""
        mock_data = pd.DataFrame(
            {
                "TRADE_DATE": ["2024-01-20", "2024-02-20", "2024-03-20", "2024-04-20"],
                "LPR1Y": [3.45, 3.45, 3.45, 3.45],
                "LPR5Y": [4.20, 4.20, 3.95, 3.95],
            }
        )
        mock_lpr.return_value = mock_data

        result = provider.get_lpr_rate("2024-02-01", "2024-03-31")

        assert len(result) == 2
        assert "2024-01-20" not in result["date"].values
        assert "2024-04-20" not in result["date"].values

    @patch("akshare.macro_china_cpi")
    def test_chinese_date_parsing(self, mock_cpi, provider):
        """Test Chinese date format parsing."""
        mock_data = pd.DataFrame(
            {
                "月份": ["2024年01月份", "2024年02月份", "2024年03月份"],
                "当月": [100.5, 100.8, 101.0],
                "同比增长": [2.1, 2.3, 2.5],
                "环比增长": [0.3, 0.5, 0.4],
                "累计": [100.5, 100.8, 101.0],
            }
        )
        mock_cpi.return_value = mock_data

        result = provider.get_cpi_data("2024-01-01", "2024-12-31")

        assert result["date"].iloc[0] == "2024-01-01"
        assert result["date"].iloc[1] == "2024-02-01"
        assert result["date"].iloc[2] == "2024-03-01"

    @patch("akshare.macro_china_pmi")
    def test_missing_columns_handling(self, mock_pmi, provider):
        """Test handling of missing optional columns."""
        mock_data = pd.DataFrame({"月份": ["2024年01月份", "2024年02月份"], "制造业-指数": [50.2, 50.5]})
        mock_pmi.return_value = mock_data

        result = provider.get_pmi_index("2024-01-01", "2024-12-31", "manufacturing")

        assert "yoy" in result.columns
        assert result["yoy"].iloc[0] is None or pd.isna(result["yoy"].iloc[0])


class TestMacroPublicAPI:
    """Test public API functions."""

    @patch("akshare.macro_china_lpr")
    def test_get_lpr_rate_api(self, mock_lpr):
        """Test get_lpr_rate public API."""
        mock_data = pd.DataFrame({"TRADE_DATE": ["2024-01-20"], "LPR1Y": [3.45], "LPR5Y": [4.20]})
        mock_lpr.return_value = mock_data

        result = get_lpr_rate(start_date="2024-01-01")
        assert not result.empty

    @patch("akshare.macro_china_pmi")
    def test_get_pmi_index_api(self, mock_pmi):
        """Test get_pmi_index public API."""
        mock_data = pd.DataFrame({"日期": ["2024-01-01"], "制造业-指数": [50.2]})
        mock_pmi.return_value = mock_data

        result = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
        assert not result.empty

    @patch("akshare.macro_china_cpi")
    def test_get_cpi_data_api(self, mock_cpi):
        """Test get_cpi_data public API."""
        mock_data = pd.DataFrame(
            {"月份": ["2024年01月份"], "当月": [100.5], "同比增长": [2.1], "环比增长": [0.3], "累计": [100.5]}
        )
        mock_cpi.return_value = mock_data

        result = get_cpi_data(start_date="2024-01-01")
        assert not result.empty
        assert "date" in result.columns
        assert "current" in result.columns

    @patch("akshare.macro_china_ppi")
    def test_get_ppi_data_api(self, mock_ppi):
        """Test get_ppi_data public API."""
        mock_data = pd.DataFrame(
            {"月份": ["2024年01月份"], "当月": [98.5], "同比增长": [-2.5], "环比增长": [-0.2], "累计": [98.5]}
        )
        mock_ppi.return_value = mock_data

        result = get_ppi_data(start_date="2024-01-01")
        assert not result.empty
        assert "date" in result.columns
        assert "current" in result.columns

    @patch("akshare.macro_china_m2_yearly")
    def test_get_m2_supply_api(self, mock_m2):
        """Test get_m2_supply public API."""
        mock_data = pd.DataFrame(
            {"商品": ["M2"], "日期": ["2024-01-01"], "今值": [8.7], "预测值": [8.6], "前值": [8.5]}
        )
        mock_m2.return_value = mock_data

        result = get_m2_supply(start_date="2024-01-01")
        assert not result.empty
        assert "date" in result.columns
        assert "yoy_growth_rate" in result.columns

    @patch("akshare.macro_china_shibor_all")
    def test_get_shibor_rate_api(self, mock_shibor):
        """Test get_shibor_rate public API."""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-02"],
                "O/N-定价": [1.5230],
                "1W-定价": [1.7890],
                "2W-定价": [1.8760],
                "1M-定价": [2.1050],
                "3M-定价": [2.3450],
                "6M-定价": [2.4560],
                "9M-定价": [2.5670],
                "1Y-定价": [2.6780],
            }
        )
        mock_shibor.return_value = mock_data

        result = get_shibor_rate(start_date="2024-01-01")
        assert not result.empty
        assert "date" in result.columns
        assert "overnight" in result.columns

    @patch("akshare.macro_china_shrzgm")
    def test_get_social_financing_api(self, mock_sf):
        """Test get_social_financing public API."""
        mock_data = pd.DataFrame(
            {"月份": ["2024-01-01"], "社会融资规模增量(亿元)": [65000.0], "新增人民币贷款(亿元)": [49000.0]}
        )
        mock_sf.return_value = mock_data

        result = get_social_financing(start_date="2024-01-01")
        assert not result.empty
        assert "date" in result.columns
        assert "total_scale" in result.columns
