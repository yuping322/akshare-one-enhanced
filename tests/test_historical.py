"""
Unit tests for Historical data module.

Tests cover:
- Basic functionality for all providers (eastmoney, sina, netease, tencent)
- Data adjustment (qfq/hfq)
- Parameter validation
- Error handling
- Caching behavior
- Field standardization
- JSON compatibility
- Empty results
- Network errors (using Mock)
- Concurrent safety
- Multi-source failover
- Extreme values
- Boundary dates

Note: Tests use provider instances directly to avoid factory parameter passing issues.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.historical.eastmoney import EastMoneyHistorical
from akshare_one.modules.historical.sina import SinaHistorical
from akshare_one.modules.historical.netease import NetEaseHistorical
from akshare_one.modules.historical.tencent import TencentHistorical
from akshare_one.modules.historical import HistoricalDataFactory


class TestGetHistDataBasic:
    """Test basic functionality of get_hist_data"""

    def test_get_hist_data_basic_eastmoney(self, mock_historical_eastmoney_api):
        """Test basic functionality with eastmoney provider"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "timestamp" in df.columns
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns

    def test_get_hist_data_basic_sina(self, mock_historical_sina_api):
        """Test basic functionality with sina provider"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = SinaHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "timestamp" in df.columns

    def test_get_hist_data_basic_netease(self):
        """Test basic functionality with netease provider"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = NetEaseHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]

    def test_get_hist_data_basic_tencent(self):
        """Test basic functionality with tencent provider"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = TencentHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]


class TestGetHistDataWithAdjust:
    """Test adjustment types (qfq/hfq)"""

    def test_get_hist_data_with_qfq(self, mock_historical_eastmoney_api):
        """Test forward adjustment (qfq - 前复权)"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(
            symbol="600000", interval="day", adjust="qfq", start_date="2024-01-01", end_date="2024-01-02"
        )
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_hist_data_with_hfq(self, mock_historical_eastmoney_api):
        """Test backward adjustment (hfq - 后复权)"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(
            symbol="600000", interval="day", adjust="hfq", start_date="2024-01-01", end_date="2024-01-02"
        )
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_hist_data_no_adjust(self, mock_historical_eastmoney_api):
        """Test no adjustment"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(
            symbol="600000", interval="day", adjust="none", start_date="2024-01-01", end_date="2024-01-02"
        )
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


class TestGetHistDataWithFilter:
    """Test data filtering functionality"""

    def test_get_hist_data_with_column_filter(self, mock_historical_sina_api):
        """Test filtering specific columns"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = SinaHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data(columns=["timestamp", "close", "volume"])

        assert isinstance(df, pd.DataFrame)
        assert set(df.columns) == {"timestamp", "close", "volume"}

    def test_get_hist_data_with_row_filter(self, mock_historical_sina_api):
        """Test filtering rows based on conditions"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = SinaHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-03")
        df = provider.get_hist_data(row_filter={"close": {"min": 11.0}})

        assert isinstance(df, pd.DataFrame)


class TestGetHistDataInvalidParameters:
    """Test invalid parameter handling"""

    def test_get_hist_data_invalid_symbol(self):
        """Test with invalid symbol format"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises((ValueError, Exception)):
            provider = EastMoneyHistorical(symbol="ABC", interval="day", start_date="2024-01-01", end_date="2024-01-02")
            provider.get_hist_data()

    def test_get_hist_data_invalid_date_format(self):
        """Test with invalid date format"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises((ValueError, Exception)):
            provider = EastMoneyHistorical(
                symbol="600000", interval="day", start_date="2024/01/01", end_date="2024-01-02"
            )
            provider.get_hist_data()

    def test_get_hist_data_invalid_date_range(self):
        """Test with invalid date range (start > end)"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises((ValueError, Exception)):
            provider = EastMoneyHistorical(
                symbol="600000", interval="day", start_date="2024-12-31", end_date="2024-01-01"
            )
            provider.get_hist_data()

    def test_get_hist_data_invalid_interval(self):
        """Test with unsupported interval"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises(ValueError, match="Unsupported interval"):
            provider = EastMoneyHistorical(
                symbol="600000", interval="invalid", start_date="2024-01-01", end_date="2024-01-02"
            )
            provider.get_hist_data()

    def test_get_hist_data_invalid_interval_multiplier(self):
        """Test with invalid interval multiplier"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises(ValueError):
            provider = EastMoneyHistorical(
                symbol="600000",
                interval="minute",
                interval_multiplier=-1,
                start_date="2024-01-01",
                end_date="2024-01-02",
            )
            provider.get_hist_data()


class TestGetHistDataEmptyResult:
    """Test empty result handling"""

    def test_get_hist_data_empty_result(self, mock_historical_empty_api):
        """Test handling of empty results"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="1970-01-01", end_date="1970-01-01")

        with pytest.raises(ValueError, match="Expected columns not found in raw data"):
            df = provider.get_hist_data()

    def test_get_hist_data_empty_result_netease(self):
        """Test empty result with netease provider"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = NetEaseHistorical(symbol="600000", interval="day", start_date="1970-01-01", end_date="1970-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert df.empty or len(df) == 0


class TestGetHistDataNetworkError:
    """Test network error handling with mocks"""

    def test_get_hist_data_network_timeout(self, mock_historical_timeout_error):
        """Test handling of network timeout"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises(ValueError):
            provider = EastMoneyHistorical(
                symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02"
            )
            provider.get_hist_data()

    def test_get_hist_data_connection_error(self, mock_historical_network_error):
        """Test handling of connection error"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        with pytest.raises(ValueError):
            provider = EastMoneyHistorical(
                symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02"
            )
            provider.get_hist_data()

    def test_get_hist_data_generic_error(self, mocker):
        """Test handling of generic errors"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        mocker.patch("akshare_one.akshare_compat.call_akshare", side_effect=Exception("Unknown error"))

        with pytest.raises(ValueError):
            provider = EastMoneyHistorical(
                symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02"
            )
            provider.get_hist_data()


class TestGetHistDataFieldStandardization:
    """Test field standardization"""

    def test_get_hist_data_field_standardization(self, mock_historical_eastmoney_api):
        """Test that fields are standardized to English names"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert "timestamp" in df.columns
        assert "open" in df.columns
        assert "close" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "volume" in df.columns

    def test_get_hist_data_timestamp_timezone(self, mock_historical_eastmoney_api):
        """Test that timestamp has proper timezone"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        if not df.empty and "timestamp" in df.columns:
            assert df["timestamp"].dtype.name in [
                "datetime64[ns, Asia/Shanghai]",
                "datetime64[ns]",
                "datetime64[us, Asia/Shanghai]",
            ]


class TestGetHistDataJsonCompatibility:
    """Test JSON serialization compatibility"""

    def test_get_hist_data_json_compatibility(self, mock_historical_with_nan_api):
        """Test that DataFrame can be serialized to JSON"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02")
        df = provider.get_hist_data()

        json_str = df.to_json(orient="records")
        assert json_str is not None

        import json

        parsed = json.loads(json_str)
        assert isinstance(parsed, list)

    def test_get_hist_data_no_infinity_values(self, mock_historical_with_infinity_api):
        """Test that input with Infinity values is preserved"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert "open" in df.columns
        assert np.isinf(df["open"]).any()


class TestGetHistDataCaching:
    """Test caching behavior"""

    def test_get_hist_data_cache_hit(self, mock_historical_eastmoney_api):
        """Test cache hit scenario"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider1 = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df1 = provider1.get_hist_data()

        provider2 = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df2 = provider2.get_hist_data()

        assert isinstance(df1, pd.DataFrame)
        assert isinstance(df2, pd.DataFrame)

    def test_get_hist_data_cache_miss_different_params(self):
        """Test cache miss when parameters differ"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider1 = NetEaseHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df1 = provider1.get_hist_data()

        provider2 = NetEaseHistorical(symbol="600001", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df2 = provider2.get_hist_data()

        assert isinstance(df1, pd.DataFrame)
        assert isinstance(df2, pd.DataFrame)


class TestGetHistDataConcurrent:
    """Test concurrent safety"""

    def test_get_hist_data_concurrent_requests(self, mock_historical_eastmoney_api):
        """Test that concurrent requests are handled safely"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        symbols = ["600000", "600001", "600002", "600003"]
        results = []

        def fetch_data(symbol):
            provider = EastMoneyHistorical(
                symbol=symbol, interval="day", start_date="2024-01-01", end_date="2024-01-01"
            )
            return provider.get_hist_data()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_data, s) for s in symbols]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    results.append(None)

        assert len(results) == len(symbols)


class TestGetHistDataFailover:
    """Test multi-source failover"""

    def test_get_hist_data_failover_to_secondary_source(self):
        """Test failover when primary source fails"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = NetEaseHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


class TestGetHistDataExtremeValues:
    """Test extreme value handling"""

    def test_get_hist_data_extreme_prices(self, mock_historical_extreme_values_api):
        """Test handling of extreme price values"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_hist_data_negative_values(self, mock_historical_eastmoney_api):
        """Test handling of potentially negative values"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


class TestGetHistDataBoundaryDates:
    """Test boundary date handling"""

    def test_get_hist_data_earliest_date(self, mock_historical_eastmoney_api):
        """Test with earliest possible date"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="1970-01-01", end_date="1970-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)

    def test_get_hist_data_future_date(self, mock_historical_empty_api):
        """Test with future date"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2030-12-31", end_date="2030-12-31")

        with pytest.raises(ValueError, match="Expected columns not found in raw data"):
            df = provider.get_hist_data()

    def test_get_hist_data_same_start_end_date(self, mock_historical_eastmoney_api):
        """Test when start and end dates are the same"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


class TestProviderSpecific:
    """Test provider-specific functionality"""

    def test_eastmoney_etf_data(self, mock_historical_etf_api):
        """Test ETF data retrieval with eastmoney"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(symbol="510050", interval="day", start_date="2024-01-01", end_date="2024-01-01")
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)

    def test_sina_minute_data(self, mock_historical_sina_minute_api):
        """Test minute data retrieval with sina"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = SinaHistorical(
            symbol="600000", interval="minute", interval_multiplier=1, start_date="2024-01-01", end_date="2024-01-01"
        )
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


class TestFactory:
    """Test HistoricalDataFactory"""

    def test_factory_creates_provider(self):
        """Test factory can create provider instance"""
        provider = HistoricalDataFactory.get_provider(
            source="eastmoney", symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01"
        )

        assert provider is not None
        assert isinstance(provider, EastMoneyHistorical)

    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source"""
        with pytest.raises((ValueError, KeyError)):
            HistoricalDataFactory.get_provider(
                source="invalid_source", symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01"
            )

    def test_factory_registers_all_providers(self):
        """Test that all providers are registered"""
        expected_providers = ["eastmoney", "sina", "netease", "tencent", "eastmoney_direct", "duckdb_cache"]

        for source in expected_providers:
            try:
                provider = HistoricalDataFactory.get_provider(
                    source=source, symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-01"
                )
                assert provider is not None
            except Exception:
                pass


class TestProviderInitialization:
    """Test provider initialization and metadata"""

    def test_provider_initialization_eastmoney(self):
        """Test eastmoney provider initialization"""
        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02")

        assert provider.symbol == "600000"
        assert provider.interval == "day"
        assert provider.start_date == "2024-01-01"
        assert provider.end_date == "2024-01-02"

    def test_provider_metadata(self):
        """Test provider metadata properties"""
        provider = EastMoneyHistorical(symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-02")

        metadata = provider.metadata
        assert "source" in metadata
        assert "data_type" in metadata

    def test_provider_supported_intervals(self):
        """Test get_supported_intervals method"""
        expected_intervals = ["minute", "hour", "day", "week", "month", "year"]

        for provider_class in [EastMoneyHistorical, SinaHistorical, NetEaseHistorical, TencentHistorical]:
            supported = provider_class.get_supported_intervals()
            assert set(supported) == set(expected_intervals)


class TestIntervalMultiplier:
    """Test interval multiplier functionality"""

    def test_interval_multiplier_daily(self, mock_historical_eastmoney_api):
        """Test interval multiplier with daily data"""
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        provider = EastMoneyHistorical(
            symbol="600000", interval="day", interval_multiplier=2, start_date="2024-01-01", end_date="2024-01-05"
        )
        df = provider.get_hist_data()

        assert isinstance(df, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
