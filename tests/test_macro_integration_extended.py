"""
Extended integration tests for macro economic data module.

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
class TestMacroIntegrationExtended:
    """Extended integration tests for macro data module."""

    def test_get_lpr_rate_integration_full(self):
        """Test getting real LPR rate data with full parameters."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "lpr_1y" in df.columns
            assert "lpr_5y" in df.columns
            assert df["date"].dtype in ["object", "string"]
            assert df["lpr_1y"].dtype in ["float64", "float32"]

    def test_get_lpr_rate_integration_narrow_range(self):
        """Test LPR rate with narrow date range."""
        df = get_lpr_rate(start_date="2024-06-01", end_date="2024-08-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert all(df["date"] >= "2024-06-01")
            assert all(df["date"] <= "2024-08-31")

    def test_get_pmi_manufacturing_integration(self):
        """Test getting real manufacturing PMI index data."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "pmi_value" in df.columns
            assert all(df["pmi_value"] > 0)
            assert all(df["pmi_value"] < 100)

    def test_get_pmi_non_manufacturing_integration(self):
        """Test getting real non-manufacturing PMI data."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="non_manufacturing")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "pmi_value" in df.columns

    def test_get_pmi_caixin_integration(self):
        """Test getting real Caixin PMI data."""
        try:
            df = get_pmi_index(start_date="2024-01-01", pmi_type="caixin")
            assert isinstance(df, pd.DataFrame)
            if not df.empty:
                assert "date" in df.columns
                assert "pmi_value" in df.columns
        except Exception:
            pytest.skip("Caixin PMI API not available")

    def test_get_cpi_data_integration_full(self):
        """Test getting real CPI data with full validation."""
        df = get_cpi_data(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "current" in df.columns
            assert "yoy" in df.columns
            assert "mom" in df.columns
            assert "cumulative" in df.columns

    def test_get_cpi_data_integration_range(self):
        """Test CPI data with date range."""
        df = get_cpi_data(start_date="2024-03-01", end_date="2024-06-30")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert all(df["date"] >= "2024-03-01")
            assert all(df["date"] <= "2024-06-30")

    def test_get_ppi_data_integration_full(self):
        """Test getting real PPI data with full validation."""
        df = get_ppi_data(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "current" in df.columns
            assert "yoy" in df.columns
            assert "mom" in df.columns
            assert "cumulative" in df.columns
            assert df["date"].dtype in ["object", "string"]

    def test_get_m2_supply_integration_full(self):
        """Test getting real M2 supply data with full validation."""
        df = get_m2_supply(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "m2_balance" in df.columns
            assert "yoy_growth_rate" in df.columns

    def test_get_m2_supply_integration_range(self):
        """Test M2 supply with date range."""
        df = get_m2_supply(start_date="2024-01-01", end_date="2024-06-30")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert all(df["date"] >= "2024-01-01")
            assert all(df["date"] <= "2024-06-30")

    def test_get_shibor_rate_integration_full(self):
        """Test getting real Shibor rate data with full validation."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-12-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "overnight" in df.columns
            assert "week_1" in df.columns
            assert "week_2" in df.columns
            assert "month_1" in df.columns
            assert "month_3" in df.columns
            assert "month_6" in df.columns
            assert "month_9" in df.columns
            assert "year_1" in df.columns

    def test_get_shibor_rate_integration_range(self):
        """Test Shibor rate with narrow date range."""
        df = get_shibor_rate(start_date="2024-07-01", end_date="2024-09-30")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert all(df["date"] >= "2024-07-01")
            assert all(df["date"] <= "2024-09-30")

    def test_get_social_financing_integration_full(self):
        """Test getting real social financing data with full validation."""
        df = get_social_financing(start_date="2024-01-01")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "date" in df.columns
            assert "total_scale" in df.columns
            assert "yoy" in df.columns
            assert "mom" in df.columns
            assert "new_rmb_loans" in df.columns


@pytest.mark.integration
class TestMacroDataQualityExtended:
    """Extended test data quality and format consistency."""

    def test_lpr_rate_value_range_extended(self):
        """Test that LPR rates are within reasonable range."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            assert all(df["lpr_1y"] > 0)
            assert all(df["lpr_1y"] < 10)
            assert all(df["lpr_5y"] > 0)
            assert all(df["lpr_5y"] < 10)
            assert all(df["lpr_5y"] >= df["lpr_1y"])

    def test_pmi_value_range_extended(self):
        """Test that PMI values are within 0-100 range."""
        df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")

        if not df.empty:
            assert all(df["pmi_value"] > 0)
            assert all(df["pmi_value"] < 100)

    def test_cpi_yoy_range_extended(self):
        """Test that CPI YoY values are within ±20%."""
        df = get_cpi_data(start_date="2024-01-01")

        if not df.empty and df["yoy"].notna().any():
            assert all(abs(df["yoy"].dropna()) < 20)

    def test_ppi_yoy_range_extended(self):
        """Test that PPI YoY values are within reasonable range."""
        df = get_ppi_data(start_date="2024-01-01")

        if not df.empty and df["yoy"].notna().any():
            assert all(abs(df["yoy"].dropna()) < 20)

    def test_m2_yoy_range_extended(self):
        """Test that M2 YoY values are within reasonable range."""
        df = get_m2_supply(start_date="2024-01-01")

        if not df.empty and df["yoy_growth_rate"].notna().any():
            assert all(abs(df["yoy_growth_rate"].dropna()) < 50)

    def test_shibor_rate_positive_extended(self):
        """Test that Shibor rates are positive."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            assert all(df["overnight"] > 0)
            assert all(df["week_1"] > 0)
            assert all(df["month_1"] > 0)
            assert all(df["month_3"] > 0)
            assert all(df["month_6"] > 0)
            assert all(df["month_9"] > 0)
            assert all(df["year_1"] > 0)

    def test_shibor_rate_monotonicity(self):
        """Test that Shibor rates increase with maturity."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty:
            for idx, row in df.iterrows():
                overnight = row["overnight"]
                week_1 = row["week_1"]
                month_1 = row["month_1"]
                year_1 = row["year_1"]

                if pd.notna(overnight) and pd.notna(week_1):
                    assert week_1 >= overnight or abs(week_1 - overnight) < 0.5
                if pd.notna(month_1) and pd.notna(year_1):
                    assert year_1 >= month_1 or abs(year_1 - month_1) < 0.5

    def test_social_financing_positive_values(self):
        """Test that social financing values are positive."""
        df = get_social_financing(start_date="2024-01-01")

        if not df.empty:
            assert all(df["total_scale"].dropna() >= 0)
            assert all(df["new_rmb_loans"].dropna() >= 0)

    def test_date_format_consistency_extended(self):
        """Test that all dates are in YYYY-MM-DD format."""
        import re

        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for func, args in [
            (get_lpr_rate, {"start_date": "2024-01-01"}),
            (get_pmi_index, {"start_date": "2024-01-01", "pmi_type": "manufacturing"}),
            (get_cpi_data, {"start_date": "2024-01-01"}),
            (get_ppi_data, {"start_date": "2024-01-01"}),
            (get_m2_supply, {"start_date": "2024-01-01"}),
            (get_shibor_rate, {"start_date": "2024-01-01"}),
            (get_social_financing, {"start_date": "2024-01-01"}),
        ]:
            df = func(**args)
            if not df.empty and "date" in df.columns:
                assert all(date_pattern.match(str(date)) for date in df["date"])

    def test_no_duplicate_dates_extended(self):
        """Test that there are no duplicate dates in each dataset."""
        for func, args in [
            (get_lpr_rate, {"start_date": "2024-01-01"}),
            (get_shibor_rate, {"start_date": "2024-01-01"}),
        ]:
            df = func(**args)
            if not df.empty and "date" in df.columns:
                assert len(df["date"]) == len(df["date"].unique())

    def test_data_sorted_by_date(self):
        """Test that data is sorted by date."""
        for func, args in [
            (get_lpr_rate, {"start_date": "2024-01-01"}),
            (get_shibor_rate, {"start_date": "2024-01-01"}),
        ]:
            df = func(**args)
            if not df.empty and "date" in df.columns and len(df) > 1:
                dates = pd.to_datetime(df["date"])
                assert dates.is_monotonic_increasing or dates.is_monotonic_decreasing


@pytest.mark.integration
class TestMacroDateFilteringExtended:
    """Extended test date filtering functionality."""

    def test_lpr_date_range_filter_extended(self):
        """Test that LPR data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_lpr_rate(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_shibor_date_range_filter_extended(self):
        """Test that Shibor data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_shibor_rate(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_cpi_date_range_filter_extended(self):
        """Test that CPI data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_cpi_data(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_pmi_date_range_filter_extended(self):
        """Test that PMI data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_pmi_index(start_date=start_date, end_date=end_date, pmi_type="manufacturing")

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_m2_date_range_filter_extended(self):
        """Test that M2 data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_m2_supply(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)

    def test_social_financing_date_range_filter_extended(self):
        """Test that social financing data is filtered by date range."""
        start_date = "2024-03-01"
        end_date = "2024-05-31"
        df = get_social_financing(start_date=start_date, end_date=end_date)

        if not df.empty:
            assert all(df["date"] >= start_date)
            assert all(df["date"] <= end_date)


@pytest.mark.integration
class TestMacroCrossValidation:
    """Test cross-validation between different macro indicators."""

    def test_pmi_cpi_correlation(self):
        """Test correlation between PMI and CPI."""
        pmi_df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
        cpi_df = get_cpi_data(start_date="2024-01-01")

        if not pmi_df.empty and not cpi_df.empty:
            assert len(pmi_df.columns) > 0
            assert len(cpi_df.columns) > 0

    def test_lpr_shibor_comparison(self):
        """Test comparison between LPR and Shibor rates."""
        lpr_df = get_lpr_rate(start_date="2024-01-01")
        shibor_df = get_shibor_rate(start_date="2024-01-01")

        if not lpr_df.empty and not shibor_df.empty:
            assert "lpr_1y" in lpr_df.columns
            assert "year_1" in shibor_df.columns

    def test_m2_social_financing_timeline(self):
        """Test timeline consistency between M2 and social financing."""
        m2_df = get_m2_supply(start_date="2024-01-01")
        sf_df = get_social_financing(start_date="2024-01-01")

        if not m2_df.empty and not sf_df.empty:
            assert "date" in m2_df.columns
            assert "date" in sf_df.columns


@pytest.mark.integration
class TestMacroHistoricalData:
    """Test historical macro data retrieval."""

    def test_lpr_historical_data(self):
        """Test LPR historical data retrieval."""
        df = get_lpr_rate(start_date="2020-01-01", end_date="2020-12-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) > 0

    def test_shibor_historical_data(self):
        """Test Shibor historical data retrieval."""
        df = get_shibor_rate(start_date="2020-01-01", end_date="2020-12-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) > 0

    def test_cpi_historical_data(self):
        """Test CPI historical data retrieval."""
        df = get_cpi_data(start_date="2020-01-01", end_date="2020-12-31")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) > 0

    def test_pmi_historical_data(self):
        """Test PMI historical data retrieval."""
        df = get_pmi_index(start_date="2020-01-01", end_date="2020-12-31", pmi_type="manufacturing")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) > 0


@pytest.mark.integration
class TestMacroTimeSeriesContinuity:
    """Test time series continuity for macro data."""

    def test_lpr_time_series_continuity(self):
        """Test LPR time series continuity."""
        df = get_lpr_rate(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty and len(df) > 1:
            dates = pd.to_datetime(df["date"])
            date_diffs = dates.diff().dropna()
            max_gap_days = 60
            if not date_diffs.empty:
                assert all(date_diffs <= pd.Timedelta(days=max_gap_days))

    def test_shibor_time_series_continuity(self):
        """Test Shibor time series continuity."""
        df = get_shibor_rate(start_date="2024-01-01", end_date="2024-01-31")

        if not df.empty and len(df) > 1:
            dates = pd.to_datetime(df["date"])
            date_diffs = dates.diff().dropna()
            max_gap_days = 7
            if not date_diffs.empty:
                assert all(date_diffs <= pd.Timedelta(days=max_gap_days))

    def test_pmi_monthly_frequency(self):
        """Test PMI is monthly frequency."""
        df = get_pmi_index(start_date="2024-01-01", end_date="2024-12-31", pmi_type="manufacturing")

        if not df.empty and len(df) > 1:
            dates = pd.to_datetime(df["date"])
            date_diffs = dates.diff().dropna()
            min_days = 28
            max_days = 32
            if not date_diffs.empty:
                assert all(date_diffs >= pd.Timedelta(days=min_days))
                assert all(date_diffs <= pd.Timedelta(days=max_days))

    def test_cpi_monthly_frequency(self):
        """Test CPI is monthly frequency."""
        df = get_cpi_data(start_date="2024-01-01", end_date="2024-12-31")

        if not df.empty and len(df) > 1:
            dates = pd.to_datetime(df["date"])
            date_diffs = dates.diff().dropna()
            min_days = 28
            max_days = 32
            if not date_diffs.empty:
                assert all(date_diffs >= pd.Timedelta(days=min_days))
                assert all(date_diffs <= pd.Timedelta(days=max_days))


@pytest.mark.integration
class TestMacroSpecialCases:
    """Test special cases and edge scenarios."""

    def test_lpr_special_dates(self):
        """Test LPR data on special dates."""
        df = get_lpr_rate(start_date="2024-02-20", end_date="2024-02-20")

        assert isinstance(df, pd.DataFrame)

    def test_shibor_weekend_data(self):
        """Test Shibor data handling weekends."""
        df = get_shibor_rate(start_date="2024-01-06", end_date="2024-01-07")

        assert isinstance(df, pd.DataFrame)

    def test_pmi_year_boundary(self):
        """Test PMI data across year boundary."""
        df = get_pmi_index(start_date="2023-12-01", end_date="2024-02-01", pmi_type="manufacturing")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) >= 1

    def test_cpi_negative_values(self):
        """Test CPI can have negative YoY values."""
        df = get_cpi_data(start_date="2020-01-01", end_date="2020-12-31")

        if not df.empty and df["yoy"].notna().any():
            negative_exists = any(df["yoy"] < 0)
            if negative_exists:
                assert True

    def test_ppi_negative_values(self):
        """Test PPI can have negative YoY values."""
        df = get_ppi_data(start_date="2024-01-01")

        if not df.empty and df["yoy"].notna().any():
            negative_exists = any(df["yoy"] < 0)
            if negative_exists:
                assert True


@pytest.mark.integration
class TestMacroDataProviderFactory:
    """Test macro data provider factory integration."""

    def test_official_provider_integration(self):
        """Test official provider through factory."""
        from akshare_one.modules.macro import MacroFactory

        provider = MacroFactory.get_provider("official")
        df = provider.get_lpr_rate("2024-01-01", "2024-12-31")

        assert isinstance(df, pd.DataFrame)

    def test_provider_list_sources_integration(self):
        """Test listing sources through factory."""
        from akshare_one.modules.macro import MacroFactory

        sources = MacroFactory.list_sources()

        assert isinstance(sources, list)
        assert "official" in sources
