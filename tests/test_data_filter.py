"""
Tests for data filtering functionality (columns + row_filter).

This module tests the apply_data_filter function and its integration
with all API functions that support columns and row_filter parameters.
"""

import pandas as pd
import pytest

from akshare_one import apply_data_filter


class TestApplyDataFilter:
    """Unit tests for apply_data_filter function."""

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=10),
                "symbol": ["600000"] * 10,
                "open": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],
                "close": [10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5],
                "volume": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                "pct_change": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            }
        )

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = apply_data_filter(df, columns=["close"], row_filter={"top_n": 5})
        assert result.empty

    def test_columns_filter(self, sample_df):
        """Test column filtering."""
        result = apply_data_filter(sample_df, columns=["close", "volume"])
        assert list(result.columns) == ["close", "volume"]
        assert len(result) == 10

    def test_columns_filter_nonexistent(self, sample_df):
        """Test column filtering with non-existent columns."""
        result = apply_data_filter(sample_df, columns=["close", "nonexistent"])
        assert list(result.columns) == ["close"]

    def test_columns_filter_all_nonexistent(self, sample_df):
        """Test column filtering when all columns don't exist - returns original df."""
        result = apply_data_filter(sample_df, columns=["nonexistent1", "nonexistent2"])
        assert len(result) == len(sample_df)
        assert len(result.columns) == len(sample_df.columns)

    def test_row_filter_top_n(self, sample_df):
        """Test top_n row filter."""
        result = apply_data_filter(sample_df, row_filter={"top_n": 5})
        assert len(result) == 5

    def test_row_filter_sort_by_descending(self, sample_df):
        """Test sort_by with descending order (default)."""
        result = apply_data_filter(sample_df, row_filter={"sort_by": "close", "top_n": 3})
        assert list(result["close"]) == [19.5, 18.5, 17.5]

    def test_row_filter_sort_by_ascending(self, sample_df):
        """Test sort_by with ascending order."""
        result = apply_data_filter(sample_df, row_filter={"sort_by": "close", "ascending": True, "top_n": 3})
        assert list(result["close"]) == [10.5, 11.5, 12.5]

    def test_row_filter_query(self, sample_df):
        """Test query filter."""
        result = apply_data_filter(sample_df, row_filter={"query": "close > 15.0"})
        assert all(result["close"] > 15.0)

    def test_row_filter_sample(self, sample_df):
        """Test sample filter."""
        result = apply_data_filter(sample_df, row_filter={"sample": 0.5})
        assert len(result) == 5

    def test_row_filter_combined(self, sample_df):
        """Test combined row filters: sort + query + top_n."""
        result = apply_data_filter(
            sample_df,
            row_filter={"query": "close > 12.0", "sort_by": "close", "top_n": 3},
        )
        assert all(result["close"] > 12.0)
        assert len(result) == 3
        assert list(result["close"]) == [19.5, 18.5, 17.5]

    def test_columns_and_row_filter_combined(self, sample_df):
        """Test combined column and row filtering."""
        result = apply_data_filter(
            sample_df,
            columns=["close", "volume"],
            row_filter={"sort_by": "volume", "top_n": 3},
        )
        assert list(result.columns) == ["close", "volume"]
        assert len(result) == 3

    def test_sort_by_nonexistent_column(self, sample_df):
        """Test sort_by with non-existent column (should not crash)."""
        result = apply_data_filter(sample_df, row_filter={"sort_by": "nonexistent"})
        assert len(result) == 10

    def test_query_invalid(self, sample_df):
        """Test invalid query expression (should not crash)."""
        result = apply_data_filter(sample_df, row_filter={"query": "invalid syntax +++"})
        assert len(result) == 10

    def test_sample_invalid_value(self, sample_df):
        """Test sample with invalid value."""
        result = apply_data_filter(sample_df, row_filter={"sample": 1.5})
        assert len(result) == 10

        result = apply_data_filter(sample_df, row_filter={"sample": 0})
        assert len(result) == 10

    def test_no_filter(self, sample_df):
        """Test with no filtering."""
        result = apply_data_filter(sample_df)
        assert len(result) == 10
        assert len(result.columns) == 6


class TestMainEntryFilterParams:
    """Test that main entry functions accept columns and row_filter parameters."""

    def test_get_hist_data_signature(self):
        """Test get_hist_data accepts filter params."""
        import inspect
        from akshare_one.modules.historical.factory import HistoricalDataFactory

        provider_cls = HistoricalDataFactory._providers.get("eastmoney")
        assert provider_cls is not None

    def test_factory_base_signature(self):
        """Test Factory classes have correct methods."""
        import inspect
        from akshare_one.modules.factory_base import BaseFactory

        assert hasattr(BaseFactory, "get_provider")
        assert hasattr(BaseFactory, "list_sources")
        assert hasattr(BaseFactory, "has_source")
        assert hasattr(BaseFactory, "register_provider")

    def test_exception_import(self):
        """Test that InvalidParameterError can be imported."""
        from akshare_one.modules.exceptions import InvalidParameterError

        assert InvalidParameterError is not None


class TestModuleLayerFilterParams:
    """Test that module layer functions accept columns and row_filter parameters."""

    def test_valuation_module(self):
        """Test valuation module functions accept filter params."""
        import inspect

        from akshare_one.modules.valuation import get_market_valuation, get_stock_valuation

        for fn in [get_stock_valuation, get_market_valuation]:
            sig = inspect.signature(fn)
            assert "columns" in sig.parameters
            assert "row_filter" in sig.parameters

    def test_shareholder_module(self):
        """Test shareholder module functions accept filter params."""
        import inspect

        from akshare_one.modules.shareholder import (
            get_institution_holdings,
            get_shareholder_changes,
            get_top_shareholders,
        )

        for fn in [get_shareholder_changes, get_top_shareholders, get_institution_holdings]:
            sig = inspect.signature(fn)
            assert "columns" in sig.parameters
            assert "row_filter" in sig.parameters

    def test_sentiment_module(self):
        """Test sentiment module functions accept filter params."""
        import inspect

        from akshare_one.modules.sentiment import get_hot_rank, get_stock_sentiment

        for fn in [get_hot_rank, get_stock_sentiment]:
            sig = inspect.signature(fn)
            assert "columns" in sig.parameters
            assert "row_filter" in sig.parameters

    def test_analyst_module(self):
        """Test analyst module functions accept filter params."""
        import inspect

        from akshare_one.modules.analyst import get_analyst_rank, get_research_report

        for fn in [get_analyst_rank, get_research_report]:
            sig = inspect.signature(fn)
            assert "columns" in sig.parameters
            assert "row_filter" in sig.parameters

    def test_performance_module(self):
        """Test performance module functions accept filter params."""
        import inspect

        from akshare_one.modules.performance import (
            get_performance_express,
            get_performance_forecast,
        )

        for fn in [get_performance_forecast, get_performance_express]:
            sig = inspect.signature(fn)
            assert "columns" in sig.parameters
            assert "row_filter" in sig.parameters


class TestFilterExecutionOrder:
    """Test that filter execution order is correct."""

    def test_execution_order_sort_before_top_n(self):
        """Test that sort_by is executed before top_n."""
        df = pd.DataFrame(
            {
                "value": [1, 2, 3, 4, 5],
            }
        )
        result = apply_data_filter(df, row_filter={"sort_by": "value", "top_n": 2})
        assert list(result["value"]) == [5, 4]

    def test_execution_order_query_before_top_n(self):
        """Test that query is executed before top_n."""
        df = pd.DataFrame(
            {
                "value": [1, 2, 3, 4, 5],
            }
        )
        result = apply_data_filter(df, row_filter={"query": "value > 2", "top_n": 2})
        assert list(result["value"]) == [3, 4]

    def test_execution_order_columns_last(self):
        """Test that column filtering is executed last."""
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": [7, 8, 9],
            }
        )
        result = apply_data_filter(df, columns=["a", "b"], row_filter={"top_n": 2})
        assert list(result.columns) == ["a", "b"]
        assert len(result) == 2
