"""
Integration tests for macro economic data module.

These tests make real API calls to verify the module works end-to-end.
"""

import pandas as pd
import pytest

from akshare_one.modules.macro import (
    get_cpi_data,
    get_lpr_rate,
    get_m2_supply,
    get_pmi_index,
    get_ppi_data,
    get_shibor_rate,
    get_social_financing,
)


@pytest.mark.integration
class TestMacroIntegration:
    """Integration tests for macro data module."""

    def test_get_lpr_rate_integration(self):
        """Test getting real LPR rate data."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "lpr_1y" in df.columns
        assert "lpr_5y" in df.columns

        # Verify data types
        if not df.empty:
            assert df["date"].dtype in ["object", "string"]
            assert df["lpr_1y"].dtype in ["float64", "float32"]

    def test_get_pmi_index_integration(self):
        """Test getting real PMI index data."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "pmi_value" in df.columns

    def test_get_cpi_data_integration(self):
        """Test getting real CPI data."""
        df = get_cpi_data(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "current" in df.columns
        assert "yoy" in df.columns

    def test_get_m2_supply_integration(self):
        """Test getting real M2 supply data."""
        df = get_m2_supply(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "m2_balance" in df.columns
        assert "yoy_growth_rate" in df.columns

    def test_get_shibor_rate_integration(self):
        """Test getting real Shibor rate data."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-12-31")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "overnight" in df.columns
        assert "year_1" in df.columns

    def test_get_ppi_data_integration(self):
        """Test getting real PPI data."""
        df = get_ppi_data(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "current" in df.columns
        assert "yoy" in df.columns
        assert "mom" in df.columns
        assert "cumulative" in df.columns

        if not df.empty:
            assert df["date"].dtype in ["object", "string"]

    def test_get_social_financing_integration(self):
        """Test getting real social financing data."""
        df = get_social_financing(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "total_scale" in df.columns
        assert "yoy" in df.columns
        assert "mom" in df.columns
        assert "new_rmb_loans" in df.columns

    def test_get_pmi_non_manufacturing_integration(self):
        """Test getting real non-manufacturing PMI data."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="non_manufacturing")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "pmi_value" in df.columns

    def test_get_pmi_caixin_integration(self):
        """Test getting real Caixin PMI data."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="caixin")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "pmi_value" in df.columns


@pytest.mark.integration
class TestMacroDataQuality:
    """Test data quality and format consistency."""

    def test_lpr_rate_value_range(self):
        """Test that LPR rates are within reasonable range."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            assert all(df["lpr_1y"] > 0)
            assert all(df["lpr_1y"] < 10)
            assert all(df["lpr_5y"] > 0)
            assert all(df["lpr_5y"] < 10)
            assert all(df["lpr_5y"] >= df["lpr_1y"])

    def test_pmi_value_range(self):
        """Test that PMI values are within reasonable range."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")

        if not df.empty:
            assert all(df["pmi_value"] > 0)
            assert all(df["pmi_value"] < 100)

    def test_cpi_yoy_range(self):
        """Test that CPI YoY values are within reasonable range."""
        df = get_cpi_data(start_date="2024-01-01")

        if not df.empty and df["yoy"].notna().any():
            assert all(abs(df["yoy"].dropna()) < 20)

    def test_shibor_rate_positive(self):
        """Test that Shibor rates are positive."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            assert all(df["overnight"] > 0)
            assert all(df["week_1"] > 0)
            assert all(df["year_1"] > 0)

    def test_date_format_consistency(self):
        """Test that all dates are in YYYY-MM-DD format."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            import re

            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            assert all(date_pattern.match(str(date)) for date in df["date"])

    def test_no_duplicate_dates(self):
        """Test that there are no duplicate dates."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            assert len(df["date"]) == len(df["date"].unique())


@pytest.mark.integration
class TestMacroDateFiltering:
    """Test date filtering functionality."""

    def test_lpr_date_range_filter(self):
        """Test that LPR data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_lpr_rate(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_shibor_date_range_filter(self):
        """Test that Shibor data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_shibor_rate(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)
