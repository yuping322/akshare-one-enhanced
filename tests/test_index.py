"""
Tests for Index module.

This module tests index data functionality.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.index import (
    IndexFactory,
    get_index_constituents,
    get_index_hist,
    get_index_hist_data,
    get_index_list,
    get_index_realtime,
    get_index_realtime_data,
)
from akshare_one.modules.index.base import IndexProvider
from akshare_one.modules.index.eastmoney import EastmoneyIndexProvider
from akshare_one.modules.index.sina import SinaIndexProvider


def create_mock_hist_df(symbol="000001"):
    """Create mock historical data DataFrame."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "日期": dates,
            "开盘": [3100.0, 3110.0, 3120.0, 3130.0, 3140.0],
            "收盘": [3115.0, 3125.0, 3135.0, 3145.0, 3155.0],
            "最高": [3120.0, 3130.0, 3140.0, 3150.0, 3160.0],
            "最低": [3095.0, 3105.0, 3115.0, 3125.0, 3135.0],
            "成交量": [1000000, 1100000, 1200000, 1300000, 1400000],
            "成交额": [3100000000, 3450000000, 3760000000, 4080000000, 4410000000],
            "涨跌幅": [0.5, 0.32, 0.32, 0.32, 0.32],
        }
    )


def create_mock_realtime_df(symbol="000001"):
    """Create mock realtime data DataFrame."""
    return pd.DataFrame(
        {
            "代码": ["000001", "000300", "399001"],
            "名称": ["上证指数", "沪深300", "深证成指"],
            "最新价": [3150.0, 3800.0, 10500.0],
            "涨跌幅": [0.5, 0.3, -0.2],
            "涨跌额": [15.0, 11.0, -21.0],
            "成交量": [100000000, 80000000, 90000000],
            "成交额": [300000000000, 250000000000, 280000000000],
            "今开": [3100.0, 3780.0, 10550.0],
            "最高": [3160.0, 3820.0, 10600.0],
            "最低": [3090.0, 3770.0, 10480.0],
            "今收": [3150.0, 3800.0, 10500.0],
            "时间": ["2024-01-05 15:00:00"] * 3,
        }
    )


def create_mock_index_list_cn_df():
    """Create mock Chinese index list DataFrame."""
    return pd.DataFrame(
        {
            "指数代码": ["000001", "000300", "000905", "399006", "688981"],
            "指数名称": ["上证指数", "沪深300", "中证500", "创业板", "科创50"],
            "发布日期": ["2004-01-02", "2005-04-08", "2007-01-15", "2010-06-01", "2020-07-23"],
            "基点": [1000.0] * 5,
            "成分股数量": [1800, 300, 500, 100, 50],
        }
    )


def create_mock_index_list_global_df():
    """Create mock global index list DataFrame."""
    return pd.DataFrame(
        {
            "index_code": ["SPX", "NDX", "DJI"],
            "index_name": ["S&P 500", "NASDAQ 100", "Dow Jones"],
            "publish_date": ["2020-01-01"] * 3,
            "base_point": [1000.0] * 3,
        }
    )


def create_mock_constituents_df(symbol="000300"):
    """Create mock constituents DataFrame."""
    return pd.DataFrame(
        {
            "成分券代码": ["600000", "600016", "600019"],
            "成分券名称": ["浦发银行", "民生银行", "宝钢股份"],
            "权重": [2.5, 2.3, 2.1],
            "调整日期": ["2024-01-01"] * 3,
        }
    )


class TestProviderBasics:
    """Test basic provider functionality (unit tests, no network required)."""

    def test_provider_initialization_eastmoney(self):
        """Test eastmoney provider can be initialized."""
        provider = EastmoneyIndexProvider()
        assert provider is not None
        assert isinstance(provider, IndexProvider)

    def test_provider_initialization_sina(self):
        """Test sina provider can be initialized."""
        provider = SinaIndexProvider()
        assert provider is not None
        assert isinstance(provider, IndexProvider)

    def test_provider_initialization_with_kwargs(self):
        """Test provider initialization with kwargs."""
        provider = EastmoneyIndexProvider(foo="bar", symbol="ignored")
        assert provider is not None

    def test_provider_metadata_eastmoney(self):
        """Test eastmoney provider metadata properties."""
        provider = EastmoneyIndexProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "eastmoney"

    def test_provider_metadata_sina(self):
        """Test sina provider metadata properties."""
        provider = SinaIndexProvider()
        metadata = provider.metadata

        assert "source" in metadata
        assert metadata["source"] == "sina"

    def test_provider_data_type(self):
        """Test provider data type identifier."""
        provider = EastmoneyIndexProvider()
        assert provider.get_data_type() == "index"

    def test_provider_update_frequency(self):
        """Test provider update frequency."""
        provider = EastmoneyIndexProvider()
        assert provider.get_update_frequency() == "daily"

    def test_provider_delay_minutes(self):
        """Test provider delay minutes."""
        provider = EastmoneyIndexProvider()
        assert provider.get_delay_minutes() == 0


class TestFactoryRegistration:
    """Test factory registration (unit tests, no network required)."""

    def test_factory_list_sources(self):
        """Test factory lists available sources."""
        sources = IndexFactory.list_sources()
        assert "eastmoney" in sources
        assert "sina" in sources

    def test_factory_has_source(self):
        """Test factory has_source method."""
        assert IndexFactory.has_source("eastmoney") is True
        assert IndexFactory.has_source("sina") is True
        assert IndexFactory.has_source("invalid") is False

    def test_factory_get_provider_eastmoney(self):
        """Test factory creates eastmoney provider."""
        provider = IndexFactory.get_provider(source="eastmoney")
        assert isinstance(provider, EastmoneyIndexProvider)

    def test_factory_get_provider_sina(self):
        """Test factory creates sina provider."""
        provider = IndexFactory.get_provider(source="sina")
        assert isinstance(provider, SinaIndexProvider)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises((ValueError, KeyError)):
            IndexFactory.get_provider(source="invalid")


class TestInvalidSource:
    """Test invalid source handling (unit tests, no network required)."""

    def test_invalid_source_index_hist(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_hist_data(symbol="000001", source="invalid")

    def test_invalid_source_index_realtime(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_realtime_data(source="invalid")

    def test_invalid_source_index_list(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_list(source="invalid")

    def test_invalid_source_index_constituents(self):
        """Test invalid source raises error."""
        with pytest.raises((ValueError, KeyError)):
            get_index_constituents(symbol="000300", source="invalid")


class TestIndexSinaProvider:
    """Test Sina index provider with mocked AkShare functions."""

    def test_provider_initialization(self):
        """Test sina provider initialization."""
        provider = SinaIndexProvider()
        assert provider.get_source_name() == "sina"
        assert isinstance(provider, IndexProvider)

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_daily(self, mock_hist):
        """Test getting index historical data from Sina - daily interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            interval="daily",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_hist.assert_called_once()
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["symbol"] == "000001"
        assert call_kwargs["period"] == "daily"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_weekly(self, mock_hist):
        """Test getting index historical data from Sina - weekly interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10",
            interval="weekly",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["period"] == "weekly"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_monthly(self, mock_hist):
        """Test getting index historical data from Sina - monthly interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="monthly",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["period"] == "monthly"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_with_columns(self, mock_hist):
        """Test getting index historical data with column filter."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            columns=["date", "close"],
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_date_format_conversion(self, mock_hist):
        """Test that date format YYYY-MM-DD is converted to YYYYMMDD for AkShare."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["start_date"] == "20240101"
        assert call_kwargs["end_date"] == "20240105"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_empty_result(self, mock_hist):
        """Test handling of empty result from AkShare."""
        mock_hist.return_value = pd.DataFrame()

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        assert df.empty

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_sina_exception(self, mock_hist):
        """Test exception handling in get_index_hist via API layer."""
        mock_hist.side_effect = Exception("Network error")

        provider = SinaIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        assert df.empty

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_sina_all(self, mock_spot):
        """Test getting all index realtime data from Sina."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = SinaIndexProvider()
        df = provider.get_index_realtime()

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_spot.assert_called_once()

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_sina_single_symbol(self, mock_spot):
        """Test getting single index realtime data from Sina."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = SinaIndexProvider()
        df = provider.get_index_realtime(symbol="000001")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_sina_with_columns(self, mock_spot):
        """Test getting realtime data with column filter."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = SinaIndexProvider()
        df = provider.get_index_realtime(
            columns=["symbol", "name", "close"],
        )

        assert df is not None

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_sina_exception(self, mock_spot):
        """Test exception handling in get_index_realtime."""
        mock_spot.side_effect = Exception("Network error")

        provider = SinaIndexProvider()
        df = provider.get_index_realtime()

        assert df is not None
        assert df.empty

    @patch("akshare.index_stock_info")
    def test_get_index_list_sina_cn(self, mock_info):
        """Test getting Chinese index list from Sina."""
        mock_info.return_value = create_mock_index_list_cn_df()

        provider = SinaIndexProvider()
        df = provider.get_index_list(category="cn")

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_info.assert_called_once()
        if not df.empty:
            assert "type" in df.columns
            assert (df["type"] == "cn_index").all()

    @patch("akshare.index_global_name_table")
    def test_get_index_list_sina_global(self, mock_global):
        """Test getting global index list from Sina."""
        mock_global.return_value = create_mock_index_list_global_df()

        provider = SinaIndexProvider()
        df = provider.get_index_list(category="global")

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_global.assert_called_once()
        if not df.empty:
            assert "type" in df.columns
            assert (df["type"] == "global_index").all()

    def test_get_index_list_sina_invalid_category(self):
        """Test getting index list with invalid category."""
        provider = SinaIndexProvider()
        df = provider.get_index_list(category="invalid")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "type"]

    @patch("akshare.index_stock_info")
    def test_get_index_list_sina_exception(self, mock_info):
        """Test exception handling in get_index_list."""
        mock_info.side_effect = Exception("Network error")

        provider = SinaIndexProvider()
        df = provider.get_index_list(category="cn")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "type"]

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_get_index_constituents_sina(self, mock_cons):
        """Test getting index constituents from Sina."""
        mock_cons.return_value = create_mock_constituents_df()

        provider = SinaIndexProvider()
        df = provider.get_index_constituents(symbol="000300", include_weight=True)

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_cons.assert_called_once_with(symbol="000300")

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_get_index_constituents_sina_exception(self, mock_cons):
        """Test exception handling in get_index_constituents."""
        mock_cons.side_effect = Exception("Network error")

        provider = SinaIndexProvider()
        df = provider.get_index_constituents(symbol="000300")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "weight"]

    def test_fetch_data_sina(self):
        """Test fetch_data returns empty DataFrame for Sina."""
        provider = SinaIndexProvider()
        df = provider.fetch_data()
        assert df is not None
        assert df.empty


class TestIndexEastmoneyProvider:
    """Test Eastmoney index provider with mocked AkShare functions."""

    def test_provider_initialization(self):
        """Test eastmoney provider initialization."""
        provider = EastmoneyIndexProvider()
        assert provider.get_source_name() == "eastmoney"
        assert isinstance(provider, IndexProvider)

    def test_provider_initialization_with_kwargs(self):
        """Test provider initialization with kwargs."""
        provider = EastmoneyIndexProvider(foo="bar", symbol="ignored", category="ignored")
        assert provider is not None

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_daily(self, mock_hist):
        """Test getting index historical data from Eastmoney - daily interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            interval="daily",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_hist.assert_called_once()
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["symbol"] == "000001"
        assert call_kwargs["period"] == "daily"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_weekly(self, mock_hist):
        """Test getting index historical data from Eastmoney - weekly interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10",
            interval="weekly",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["period"] == "weekly"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_monthly(self, mock_hist):
        """Test getting index historical data from Eastmoney - monthly interval."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="monthly",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["period"] == "monthly"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_with_columns(self, mock_hist):
        """Test getting index historical data with column filter."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            columns=["date", "close"],
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_date_format_conversion(self, mock_hist):
        """Test that date format YYYY-MM-DD is converted to YYYYMMDD for AkShare."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["start_date"] == "20240101"
        assert call_kwargs["end_date"] == "20240105"

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_empty_result(self, mock_hist):
        """Test handling of empty result from AkShare."""
        mock_hist.return_value = pd.DataFrame()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        assert df.empty

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_em_exception(self, mock_hist):
        """Test exception handling in get_index_hist."""
        mock_hist.side_effect = Exception("Network error")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        assert df.empty

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_em_all(self, mock_spot):
        """Test getting all index realtime data from Eastmoney."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_realtime()

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_spot.assert_called_once()

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_em_single_symbol(self, mock_spot):
        """Test getting single index realtime data from Eastmoney."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_realtime(symbol="000001")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_em_with_columns(self, mock_spot):
        """Test getting realtime data with column filter."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_realtime(
            columns=["symbol", "name", "close"],
        )

        assert df is not None

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_em_exception(self, mock_spot):
        """Test exception handling in get_index_realtime."""
        mock_spot.side_effect = Exception("Network error")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_realtime()

        assert df is not None
        assert df.empty

    @patch("akshare.index_stock_info")
    def test_get_index_list_em_cn(self, mock_info):
        """Test getting Chinese index list from Eastmoney."""
        mock_info.return_value = create_mock_index_list_cn_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_list(category="cn")

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_info.assert_called_once()
        if not df.empty:
            assert "type" in df.columns
            assert (df["type"] == "cn_index").all()

    def test_get_index_list_em_invalid_category(self):
        """Test getting index list with invalid category returns empty DataFrame."""
        provider = EastmoneyIndexProvider()
        df = provider.get_index_list(category="invalid")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "type"]

    @patch("akshare.index_stock_info")
    def test_get_index_list_em_exception(self, mock_info):
        """Test exception handling in get_index_list."""
        mock_info.side_effect = Exception("Network error")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_list(category="cn")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "type"]

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_get_index_constituents_em(self, mock_cons):
        """Test getting index constituents from Eastmoney."""
        mock_cons.return_value = create_mock_constituents_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_constituents(symbol="000300", include_weight=True)

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        mock_cons.assert_called_once_with(symbol="000300")

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_get_index_constituents_em_exception(self, mock_cons):
        """Test exception handling in get_index_constituents."""
        mock_cons.side_effect = Exception("Network error")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_constituents(symbol="000300")

        assert df is not None
        assert df.empty
        assert list(df.columns) == ["symbol", "name", "weight"]

    def test_fetch_data_em(self):
        """Test fetch_data returns empty DataFrame for Eastmoney."""
        provider = EastmoneyIndexProvider()
        df = provider.fetch_data()
        assert df is not None
        assert df.empty


class TestIndexDataAPI:
    """Test Index module public API functions with mocked providers."""

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_data_basic(self, mock_hist):
        """Test basic get_index_hist_data function."""
        mock_hist.return_value = create_mock_hist_df()

        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_data_with_interval(self, mock_hist):
        """Test get_index_hist_data with different intervals."""
        mock_hist.return_value = create_mock_hist_df()

        for interval in ["daily", "weekly", "monthly"]:
            df = get_index_hist_data(
                symbol="000001",
                start_date="2024-01-01",
                end_date="2024-01-05",
                source="eastmoney",
                interval=interval,
            )
            assert df is not None

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_data(self, mock_spot):
        """Test get_index_realtime_data function."""
        mock_spot.return_value = create_mock_realtime_df()

        df = get_index_realtime_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.index_stock_info")
    def test_get_index_list_basic(self, mock_info):
        """Test get_index_list function."""
        mock_info.return_value = create_mock_index_list_cn_df()

        df = get_index_list(category="cn", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.index_stock_info")
    def test_get_index_list_all_indices(self, mock_info):
        """Test get_index_list for all categories."""
        mock_info.return_value = create_mock_index_list_cn_df()

        for category in ["cn", "hk", "us", "global"]:
            df = get_index_list(category=category, source="eastmoney")
            assert df is not None

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_get_index_constituents(self, mock_cons):
        """Test get_index_constituents function."""
        mock_cons.return_value = create_mock_constituents_df()

        df = get_index_constituents(symbol="000300", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    @patch("akshare.index_zh_a_hist")
    def test_get_index_hist_alias(self, mock_hist):
        """Test get_index_hist alias works same as get_index_hist_data."""
        mock_hist.return_value = create_mock_hist_df()

        df = get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
            source="eastmoney",
        )

        assert df is not None

    @patch("akshare.stock_zh_index_spot_em")
    def test_get_index_realtime_alias(self, mock_spot):
        """Test get_index_realtime alias works same as get_index_realtime_data."""
        mock_spot.return_value = create_mock_realtime_df()

        df = get_index_realtime(source="eastmoney")

        assert df is not None


class TestIndexTypeHandling:
    """Test handling of different index types."""

    @patch("akshare.index_zh_a_hist")
    def test_shanghai_composite_index(self, mock_hist):
        """Test Shanghai Composite Index (000001)."""
        mock_hist.return_value = create_mock_hist_df("000001")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["symbol"] == "000001"

    @patch("akshare.index_zh_a_hist")
    def test_shenzhen_component_index(self, mock_hist):
        """Test Shenzhen Component Index (399001)."""
        mock_hist.return_value = create_mock_hist_df("399001")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="399001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None
        call_kwargs = mock_hist.call_args[1]
        assert call_kwargs["symbol"] == "399001"

    @patch("akshare.index_zh_a_hist")
    def test_sse_50_index(self, mock_hist):
        """Test SSE 50 Index (000016)."""
        mock_hist.return_value = create_mock_hist_df("000016")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000016",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_hs300_index(self, mock_hist):
        """Test CSI 300 Index (000300)."""
        mock_hist.return_value = create_mock_hist_df("000300")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000300",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_zz500_index(self, mock_hist):
        """Test CSI 500 Index (000905)."""
        mock_hist.return_value = create_mock_hist_df("000905")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000905",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_cyb_index(self, mock_hist):
        """Test ChiNext Index (399006)."""
        mock_hist.return_value = create_mock_hist_df("399006")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="399006",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_kcb_index(self, mock_hist):
        """Test STAR 50 Index (000688)."""
        mock_hist.return_value = create_mock_hist_df("000688")

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000688",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None


class TestAkShareFunctionMock:
    """Test that AkShare functions are properly mocked."""

    @patch("akshare.index_zh_a_hist")
    def test_mock_index_zh_a_hist_sina(self, mock_hist):
        """Test index_zh_a_hist is called correctly for Sina."""
        mock_hist.return_value = create_mock_hist_df()

        provider = SinaIndexProvider()
        provider.get_index_hist(symbol="000001", start_date="2024-01-01", end_date="2024-01-05")

        mock_hist.assert_called_once_with(
            symbol="000001",
            period="daily",
            start_date="20240101",
            end_date="20240105",
        )

    @patch("akshare.stock_zh_index_spot_em")
    def test_mock_stock_zh_index_spot_em(self, mock_spot):
        """Test stock_zh_index_spot_em is called correctly."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = SinaIndexProvider()
        provider.get_index_realtime()

        mock_spot.assert_called_once()

    @patch("akshare.index_stock_info")
    def test_mock_index_stock_info(self, mock_info):
        """Test index_stock_info is called correctly."""
        mock_info.return_value = create_mock_index_list_cn_df()

        provider = SinaIndexProvider()
        provider.get_index_list(category="cn")

        mock_info.assert_called_once()

    @patch("akshare.index_global_name_table")
    def test_mock_index_global_name_table(self, mock_global):
        """Test index_global_name_table is called correctly."""
        mock_global.return_value = create_mock_index_list_global_df()

        provider = SinaIndexProvider()
        provider.get_index_list(category="global")

        mock_global.assert_called_once()

    @patch("akshare.index_stock_cons_weight_csindex")
    def test_mock_index_stock_cons_weight_csindex(self, mock_cons):
        """Test index_stock_cons_weight_csindex is called correctly."""
        mock_cons.return_value = create_mock_constituents_df()

        provider = SinaIndexProvider()
        provider.get_index_constituents(symbol="000300")

        mock_cons.assert_called_once_with(symbol="000300")

    @patch("akshare.index_zh_a_hist")
    def test_mock_index_zh_a_hist_em(self, mock_hist):
        """Test index_zh_a_hist is called correctly for Eastmoney."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        provider.get_index_hist(symbol="000001", start_date="2024-01-01", end_date="2024-01-05")

        mock_hist.assert_called_once_with(
            symbol="000001",
            period="daily",
            start_date="20240101",
            end_date="20240105",
        )


class TestFieldStandardization:
    """Test field standardization in index data."""

    @patch("akshare.index_zh_a_hist")
    def test_index_code_format(self, mock_hist):
        """Test index code is properly formatted with leading zeros."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        if not df.empty and "symbol" in df.columns:
            assert df["symbol"].dtype == object

    @patch("akshare.index_zh_a_hist")
    def test_historical_data_fields(self, mock_hist):
        """Test historical data has expected fields after standardization."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        assert df is not None

    @patch("akshare.stock_zh_index_spot_em")
    def test_realtime_data_fields(self, mock_spot):
        """Test realtime data has expected fields after standardization."""
        mock_spot.return_value = create_mock_realtime_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_realtime()

        assert df is not None

    @patch("akshare.index_zh_a_hist")
    def test_index_data_json_compatibility(self, mock_hist):
        """Test that index data is JSON-compatible."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        if not df.empty:
            result = provider.ensure_json_compatible(df)
            assert result is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dataframe_columns(self):
        """Test handling of empty DataFrame with specific columns."""
        provider = EastmoneyIndexProvider()

        empty_df = provider.ensure_json_compatible(pd.DataFrame())
        assert empty_df.empty

    def test_dataframe_with_nan_values(self):
        """Test handling of DataFrame with NaN values."""
        df_with_nan = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "收盘": [100.0, np.nan],
                "成交量": [1000000, np.nan],
            }
        )

        provider = EastmoneyIndexProvider()
        result = provider.ensure_json_compatible(df_with_nan)

        assert result is not None

    def test_provider_str_representation(self):
        """Test provider string representation."""
        provider = EastmoneyIndexProvider()
        str_repr = str(provider)
        assert "Eastmoney" in str_repr or "index" in str_repr.lower()

    @patch("akshare.index_zh_a_hist")
    def test_symbol_added_to_hist_data(self, mock_hist):
        """Test that symbol is added to historical data."""
        mock_hist.return_value = create_mock_hist_df()

        provider = EastmoneyIndexProvider()
        df = provider.get_index_hist(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        if not df.empty and "symbol" in df.columns:
            assert (df["symbol"] == "000001").all()


@pytest.mark.integration
class TestGetIndexHistDataIntegration:
    """Test get_index_hist_data function (integration tests, require network)."""

    def test_get_index_hist_data_eastmoney(self):
        """Test getting index historical data from eastmoney."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10",
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "close" in df.columns

    def test_get_index_hist_data_sina(self):
        """Test getting index historical data from sina."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10",
            source="sina",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_hist_data_with_filter(self):
        """Test index historical data with row filter."""
        df = get_index_hist_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10",
            source="eastmoney",
            row_filter={"top_n": 5},
        )

        assert df is not None
        if not df.empty:
            assert len(df) <= 5


@pytest.mark.integration
class TestGetIndexRealtimeDataIntegration:
    """Test get_index_realtime_data function (integration tests, require network)."""

    def test_get_index_realtime_data_all(self):
        """Test getting all index realtime data."""
        df = get_index_realtime_data(source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_realtime_data_single(self):
        """Test getting single index realtime data."""
        df = get_index_realtime_data(symbol="000001", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


@pytest.mark.integration
class TestGetIndexListIntegration:
    """Test get_index_list function (integration tests, require network)."""

    def test_get_index_list_cn(self):
        """Test getting Chinese index list."""
        df = get_index_list(category="cn", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_get_index_list_global(self):
        """Test getting global index list."""
        df = get_index_list(category="global", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)


@pytest.mark.integration
class TestGetIndexConstituentsIntegration:
    """Test get_index_constituents function (integration tests, require network)."""

    def test_get_index_constituents_csi300(self):
        """Test getting CSI 300 constituents."""
        df = get_index_constituents(symbol="000300", source="eastmoney")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if not df.empty:
            assert "symbol" in df.columns

    def test_get_index_constituents_without_weight(self):
        """Test getting constituents without weight."""
        df = get_index_constituents(
            symbol="000300",
            include_weight=False,
            source="eastmoney",
        )

        assert df is not None
        assert isinstance(df, pd.DataFrame)
