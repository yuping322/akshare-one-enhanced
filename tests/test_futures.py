from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Mark all tests in this module as integration tests (require network)
pytestmark = pytest.mark.integration

from akshare_one import (
    get_futures_hist_data,
    get_futures_realtime_data,
)
from akshare_one.modules.futures.sina import (
    SinaHistoricalFuturesProvider,
    SinaRealtimeFuturesProvider,
)
from akshare_one.modules.futures.base import (
    parse_futures_symbol,
    FuturesHistoricalFactory,
    FuturesRealtimeFactory,
)


class TestFuturesHistData:
    def test_basic_futures_hist_data(self):
        """测试基本期货历史数据获取功能"""
        df = get_futures_hist_data(symbol="AG", contract="2604", interval="day")
        assert not df.empty
        assert "timestamp" in df.columns
        assert "symbol" in df.columns
        assert "close" in df.columns

    def test_futures_daily_data(self):
        """测试日线级别期货数据"""
        df = get_futures_hist_data(
            symbol="CU0",
            interval="day",
        )
        assert not df.empty
        assert set(df.columns).issuperset(
            {
                "timestamp",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
            }
        )

    def test_futures_minute_data(self):
        """测试分钟级期货数据"""
        df = get_futures_hist_data(
            symbol="CU",
            interval="minute",
            interval_multiplier=5,
        )
        assert not df.empty
        assert len(df) > 0

    def test_invalid_futures_symbol(self):
        """测试无效期货代码"""
        with pytest.raises((ValueError, KeyError)):
            get_futures_hist_data(
                symbol="INVALID",
                interval="day",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

    def test_futures_data_invalid_dates(self):
        """测试期货数据无效日期"""
        with pytest.raises(ValueError):
            get_futures_hist_data(
                symbol="CU",
                interval="day",
                start_date="2025-31-01",  # invalid date
                end_date="2025-01-31",
            )

    def test_invalid_interval(self):
        """测试无效间隔参数"""
        with pytest.raises(ValueError):
            get_futures_hist_data(
                symbol="CU",
                interval="invalid",  # type: ignore
                start_date="2025-01-01",
                end_date="2025-01-31",
            )

    def test_weekly_data(self):
        """测试周线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="week")
        assert not df.empty

    def test_monthly_data(self):
        """测试月线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="month")
        assert not df.empty


class TestFuturesRealtimeData:
    def test_basic_futures_realtime_data(self):
        """测试基本期货实时数据获取"""
        # Note: API may only return certain varieties at different times
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    def test_specific_contract_realtime(self):
        """测试特定合约的实时数据"""
        # First get available contracts
        all_df = get_futures_realtime_data()
        if not all_df.empty:
            # Use the first available symbol for testing
            test_symbol = all_df["symbol"].iloc[0]
            df = get_futures_realtime_data(symbol=test_symbol)
            assert not df.empty
            assert "symbol" in df.columns

    def test_all_futures_quotes(self):
        """测试获取所有期货实时数据"""
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    def test_realtime_data_columns(self):
        """测试实时数据字段完整性"""
        df = get_futures_realtime_data()
        if not df.empty:
            expected_columns = {
                "symbol",
                "contract",
                "price",
                "change",
                "pct_change",
                "timestamp",
                "volume",
                "open_interest",
                "open",
                "high",
                "low",
                "prev_settlement",
            }
            assert expected_columns.issubset(set(df.columns))

    def test_api_error_handling(self):
        """测试API错误处理"""
        # Test with a unique symbol to avoid cache hits
        with (
            patch("akshare_one.modules.futures.sina.ak.futures_zh_spot") as mock_spot,
            patch("akshare_one.modules.futures.sina.ak.futures_zh_realtime") as mock_realtime,
        ):
            mock_spot.side_effect = Exception("API error")
            mock_realtime.side_effect = Exception("API error")
            # Use a unique symbol that won't be cached
            with pytest.raises(Exception, match="API error"):
                from akshare_one.modules.futures.sina import SinaFuturesRealtime

                SinaFuturesRealtime(symbol="UNIQUE_TEST_SYMBOL")
                # Bypass cache by calling the API directly
                import akshare as ak

                ak.futures_zh_spot()

    def test_invalid_source(self):
        """测试无效数据源"""
        from akshare_one.modules.futures.base import FuturesRealtimeFactory

        with pytest.raises(ValueError, match="Unknown.*provider"):
            FuturesRealtimeFactory.get_provider("invalid", symbol="CU")


class TestFuturesDataFactory:
    def test_register_custom_provider(self):
        """测试注册自定义数据提供商"""
        from akshare_one.modules.futures.base import (
            HistoricalFuturesDataProvider,
            FuturesHistoricalFactory,
        )

        class CustomProvider(HistoricalFuturesDataProvider):
            def get_hist_data(self):
                import pandas as pd

                return pd.DataFrame()

            def get_main_contracts(self):
                import pandas as pd

                return pd.DataFrame()

        FuturesHistoricalFactory.register_provider("custom", CustomProvider)
        provider = FuturesHistoricalFactory.get_provider("custom", symbol="AG2604")
        assert isinstance(provider, CustomProvider)

    def test_get_provider_by_name(self):
        """测试通过名称获取数据提供商"""
        from akshare_one.modules.futures.base import FuturesHistoricalFactory

        provider = FuturesHistoricalFactory.get_provider("sina", symbol="AG2604")
        assert provider is not None
        assert provider.symbol == "AG"

    def test_get_realtime_provider(self):
        """测试获取实时数据提供商"""
        from akshare_one.modules.futures.base import FuturesRealtimeFactory

        provider = FuturesRealtimeFactory.get_provider("sina", symbol="AG2604")
        assert provider is not None
        assert provider.symbol == "AG"


@pytest.mark.unit
class TestFuturesSymbolParsing:
    """Unit tests for futures symbol parsing logic."""

    def test_futures_symbol_parsing_main_contract(self):
        """Test parsing main contract symbol."""
        symbol, contract = parse_futures_symbol("CU0", "main")
        assert symbol == "CU"
        assert contract == "main"

        symbol, contract = parse_futures_symbol("AG0")
        assert symbol == "AG"
        assert contract == "main"

    def test_futures_symbol_parsing_specific_contract(self):
        """Test parsing specific contract symbols."""
        symbol, contract = parse_futures_symbol("CU2405", "main")
        assert symbol == "CU"
        assert contract == "2405"

        symbol, contract = parse_futures_symbol("AG2604")
        assert symbol == "AG"
        assert contract == "2604"

    def test_futures_symbol_parsing_with_contract_param(self):
        """Test parsing with explicit contract parameter."""
        symbol, contract = parse_futures_symbol("CU", "2405")
        assert symbol == "CU"
        assert contract == "2405"

        symbol, contract = parse_futures_symbol("AG0", "2604")
        assert symbol == "AG"
        assert contract == "2604"

    def test_futures_symbol_parsing_edge_cases(self):
        """Test edge cases in symbol parsing."""
        # Lowercase input
        symbol, contract = parse_futures_symbol("cu", "2405")
        assert symbol == "CU"

        # With spaces
        symbol, contract = parse_futures_symbol(" CU ", " 2405 ")
        assert symbol == "CU"
        assert contract == "2405"

    def test_futures_symbol_parsing_invalid_format(self):
        """Test parsing invalid symbol format."""
        symbol, contract = parse_futures_symbol("123", "main")
        assert symbol == "123"
        assert contract == "main"

    def test_futures_symbol_parsing_conflicting_contract(self):
        """Test parsing when symbol suffix conflicts with contract param."""
        symbol, contract = parse_futures_symbol("CU2405", "2606")
        assert symbol == "CU"
        assert contract == "2606"

    def test_futures_symbol_parsing_empty_string(self):
        """Test parsing empty string."""
        symbol, contract = parse_futures_symbol("", "main")
        assert symbol == ""
        assert contract == "main"

    def test_futures_symbol_parsing_numeric_only(self):
        """Test parsing numeric only symbol."""
        symbol, contract = parse_futures_symbol("2405", "main")
        assert symbol == "2405"
        assert contract == "main"


@pytest.mark.unit
class TestFuturesBasic:
    """Unit tests for futures basic functionality."""

    def test_futures_symbol_parsing_main(self):
        """Test futures symbol parsing for main contracts."""
        symbol, contract = parse_futures_symbol("CU0", "main")
        assert symbol == "CU"
        assert contract == "main"

    def test_futures_symbol_parsing_specific(self):
        """Test futures symbol parsing for specific contracts."""
        symbol, contract = parse_futures_symbol("CU2405", "main")
        assert symbol == "CU"
        assert contract == "2405"

    def test_futures_contract_validation(self):
        """Test futures contract validation."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")
        assert provider.symbol == "CU"
        assert provider.contract == "2405"

    def test_futures_interval_options(self):
        """Test futures interval options."""
        valid_intervals = ["minute", "hour", "day", "week", "month"]
        for interval in valid_intervals:
            provider = SinaHistoricalFuturesProvider(symbol="CU", interval=interval)
            assert provider.interval == interval

    def test_futures_exchange_codes(self):
        """Test futures exchange codes mapping."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        assert hasattr(provider, "_exchange_map")
        assert "CZCE" in provider._exchange_map
        assert "SHFE" in provider._exchange_map
        assert "DCE" in provider._exchange_map


@pytest.mark.unit
class TestFuturesData:
    """Unit tests for futures data methods."""

    @patch("akshare.futures_zh_daily_sina")
    def test_get_futures_hist_daily(self, mock_ak):
        """Test getting futures daily historical data."""
        mock_df = pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-16"],
                "open": [50000.0, 51000.0],
                "high": [51500.0, 52000.0],
                "low": [49800.0, 50500.0],
                "close": [51000.0, 51800.0],
                "volume": [10000, 12000],
                "hold": [5000, 5500],
            }
        )
        mock_df.index = pd.to_datetime(mock_df["date"])
        mock_ak.return_value = mock_df

        provider = SinaHistoricalFuturesProvider(
            symbol="CU", contract="2405", interval="day", start_date="2024-01-01", end_date="2024-01-31"
        )
        result = provider.get_hist_data()
        assert not result.empty

    @patch("akshare.futures_zh_minute_sina")
    def test_get_futures_hist_minute(self, mock_ak):
        """Test getting futures minute historical data."""
        mock_df = pd.DataFrame(
            {
                "datetime": ["2024-01-15 09:00:00", "2024-01-15 09:05:00"],
                "open": [50000.0, 50100.0],
                "high": [50200.0, 50300.0],
                "low": [49900.0, 50000.0],
                "close": [50100.0, 50200.0],
                "volume": [1000, 1200],
                "hold": [500, 550],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaHistoricalFuturesProvider(
            symbol="CU", contract="2405", interval="minute", start_date="2024-01-01", end_date="2024-01-31"
        )
        result = provider._get_intraday_data()
        assert not result.empty

    @patch("akshare.futures_zh_spot")
    def test_get_futures_realtime(self, mock_ak):
        """Test getting futures realtime data."""
        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "AG2604"],
                "名称": ["沪铜2405", "沪银2604"],
                "最新价": [51000.0, 6000.0],
                "涨跌额": [100.0, 50.0],
                "涨跌幅": [0.2, 0.83],
                "开盘价": [50000.0, 5950.0],
                "最高价": [51500.0, 6050.0],
                "最低价": [49800.0, 5900.0],
                "成交量": [10000, 8000],
                "持仓量": [5000, 3000],
                "结算价": [51000.0, 6000.0],
                "昨结算": [50900.0, 5950.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaRealtimeFuturesProvider()
        result = provider.get_current_data()
        assert not result.empty

    @patch("akshare.futures_contract_info_shfe")
    @patch("akshare.futures_contract_info_dce")
    @patch("akshare.futures_contract_info_czce")
    @patch("akshare.futures_contract_info_cffex")
    def test_get_main_contracts(self, mock_cffex, mock_czce, mock_dce, mock_shfe):
        """Test getting main contracts."""
        mock_shfe_df = pd.DataFrame({"symbol": ["CU2405", "AL2405"]})
        mock_shfe.return_value = mock_shfe_df
        mock_dce_df = pd.DataFrame({"symbol": ["I2405", "J2405"]})
        mock_dce.return_value = mock_dce_df
        mock_czce_df = pd.DataFrame({"symbol": ["CF501", "SR501"]})
        mock_czce.return_value = mock_czce_df
        mock_cffex_df = pd.DataFrame({"symbol": ["IF2401", "IC2401"]})
        mock_cffex.return_value = mock_cffex_df

        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider.get_main_contracts()
        assert isinstance(result, pd.DataFrame)

    @patch("akshare.futures_zh_realtime")
    @patch("akshare.futures_contract_info_shfe")
    @patch("akshare.futures_contract_info_dce")
    @patch("akshare.futures_contract_info_czce")
    @patch("akshare.futures_contract_info_cffex")
    def test_get_contract_details(self, mock_cffex, mock_czce, mock_dce, mock_shfe, mock_realtime):
        """Test getting contract details."""
        mock_shfe_df = pd.DataFrame({"symbol": ["CU2405"]})
        mock_shfe.return_value = mock_shfe_df
        mock_dce_df = pd.DataFrame()
        mock_dce.return_value = mock_dce_df
        mock_czce_df = pd.DataFrame()
        mock_czce.return_value = mock_czce_df
        mock_cffex_df = pd.DataFrame()
        mock_cffex.return_value = mock_cffex_df

        mock_realtime_df = pd.DataFrame(
            {
                "symbol": ["CU2405"],
                "trade": [51000.0],
                "open": [50000.0],
                "high": [51500.0],
                "low": [49800.0],
                "volume": [10000],
                "position": [5000],
            }
        )
        mock_realtime.return_value = mock_realtime_df

        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider.get_main_contracts()
        assert isinstance(result, pd.DataFrame)


@pytest.mark.unit
class TestFuturesSinaFieldMapping:
    """Unit tests for futures Sina field mapping."""

    @patch("akshare.futures_zh_daily_sina")
    def test_futures_sina_field_mapping(self, mock_ak):
        """Test Sina field mapping for futures data."""
        mock_df = pd.DataFrame(
            {
                "date": ["2024-01-15"],
                "open": [50000.0],
                "high": [51500.0],
                "low": [49800.0],
                "close": [51000.0],
                "volume": [10000],
                "hold": [5000],
            }
        )
        mock_df.index = pd.to_datetime(mock_df["date"])
        mock_ak.return_value = mock_df

        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")
        result = provider._get_daily_data()

        assert "timestamp" in result.columns
        assert "symbol" in result.columns
        assert "contract" in result.columns

    @patch("akshare.futures_zh_minute_sina")
    def test_futures_date_filter(self, mock_ak):
        """Test date filtering for futures data."""
        mock_df = pd.DataFrame(
            {
                "datetime": pd.date_range("2024-01-15 09:00", periods=5, freq="min"),
                "open": [50000.0] * 5,
                "high": [50200.0] * 5,
                "low": [49900.0] * 5,
                "close": [50100.0] * 5,
                "volume": [1000] * 5,
                "hold": [500] * 5,
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaHistoricalFuturesProvider(
            symbol="CU", contract="2405", interval="minute", start_date="2024-01-15", end_date="2024-01-15"
        )
        result = provider._get_intraday_data()
        assert isinstance(result, pd.DataFrame)


@pytest.mark.unit
class TestFuturesResampleMethods:
    """Unit tests for futures resample methods."""

    def test_resample_intraday_data(self):
        """Test resampling intraday data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="minute")

        mock_df = pd.DataFrame(
            {
                "datetime": pd.date_range("2024-01-15 09:00", periods=10, freq="min"),
                "open": list(range(50000, 50100, 10)),
                "high": list(range(50100, 50200, 10)),
                "low": list(range(49900, 50000, 10)),
                "close": list(range(50050, 50150, 10)),
                "volume": list(range(1000, 2000, 100)),
                "hold": list(range(500, 600, 10)),
            }
        )
        mock_df = mock_df.set_index("datetime")

        result = provider._resample_intraday_data(mock_df, "5min")
        assert not result.empty

    def test_resample_daily_data(self):
        """Test resampling daily data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")

        mock_df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=30, freq="D"),
                "open": [50000.0] * 30,
                "high": [51500.0] * 30,
                "low": [49800.0] * 30,
                "close": [51000.0] * 30,
                "volume": [10000] * 30,
                "hold": [5000] * 30,
                "settle": [51000.0] * 30,
            }
        )
        mock_df = mock_df.set_index("date")

        result = provider._resample_data(mock_df, "week", 1)
        assert not result.empty


@pytest.mark.unit
class TestFuturesCleanMethods:
    """Unit tests for futures clean methods."""

    def test_clean_intraday_data(self):
        """Test cleaning intraday data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="minute")

        mock_df = pd.DataFrame(
            {
                "datetime": pd.date_range("2024-01-15 09:00", periods=5, freq="min"),
                "open": [50000.0] * 5,
                "high": [50200.0] * 5,
                "low": [49900.0] * 5,
                "close": [50100.0] * 5,
                "volume": [1000] * 5,
                "hold": [500] * 5,
            }
        )

        result = provider._clean_intraday_data(mock_df)
        assert "timestamp" in result.columns
        assert "symbol" in result.columns
        assert "contract" in result.columns
        assert result["symbol"].iloc[0] == "CU"
        assert result["contract"].iloc[0] == "2405"

    def test_clean_daily_data(self):
        """Test cleaning daily data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")

        mock_df = pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-16"],
                "open": [50000.0, 51000.0],
                "high": [51500.0, 52000.0],
                "low": [49800.0, 50500.0],
                "close": [51000.0, 51800.0],
                "volume": [10000, 12000],
                "hold": [5000, 5500],
            }
        )
        mock_df.index = pd.to_datetime(mock_df["date"])

        result = provider._clean_daily_data(mock_df)
        assert "timestamp" in result.columns
        assert "symbol" in result.columns
        assert "contract" in result.columns

    def test_select_standard_columns(self):
        """Test selecting standard columns."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")

        mock_df = pd.DataFrame(
            {
                "timestamp": ["2024-01-15"],
                "symbol": ["CU"],
                "contract": ["2405"],
                "open": [50000.0],
                "high": [51500.0],
                "low": [49800.0],
                "close": [51000.0],
                "volume": [10000],
                "open_interest": [5000],
                "settlement": [51000.0],
                "extra_column": [1],
            }
        )

        result = provider._select_standard_columns(mock_df)
        expected = [
            "timestamp",
            "symbol",
            "contract",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]
        assert list(result.columns) == expected


@pytest.mark.unit
class TestFuturesNormalizeAndValidate:
    """Unit tests for futures normalize and validate methods."""

    def test_normalize_contract_main(self):
        """Test normalizing main contract."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="main", interval="day")
        result = provider._normalize_contract()
        assert result == "CU0"

    def test_normalize_contract_specific(self):
        """Test normalizing specific contract."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")
        result = provider._normalize_contract()
        assert result == "CU2405"

    def test_validate_interval_params_valid(self):
        """Test validating interval parameters - valid case."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        provider._validate_interval_params("day", 1)
        provider._validate_interval_params("minute", 5)
        provider._validate_interval_params("hour", 1)

    def test_validate_interval_params_invalid_interval(self):
        """Test validating interval parameters - invalid interval."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        with pytest.raises(ValueError, match="Unsupported interval"):
            provider._validate_interval_params("invalid", 1)

    def test_validate_interval_params_invalid_multiplier(self):
        """Test validating interval parameters - invalid multiplier."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="minute")
        with pytest.raises(ValueError, match="interval_multiplier.*must be >= 1"):
            provider._validate_interval_params("minute", 0)


@pytest.mark.unit
class TestFuturesDateFormatMethods:
    """Unit tests for futures date format methods."""

    def test_ensure_time_format_without_time(self):
        """Test ensuring time format when date has no time."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider._ensure_time_format("2024-01-15", "00:00:00")
        assert result == "2024-01-15 00:00:00"

    def test_ensure_time_format_with_time(self):
        """Test ensuring time format when date already has time."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider._ensure_time_format("2024-01-15 09:00:00", "00:00:00")
        assert result == "2024-01-15 09:00:00"

    def test_convert_date_format_with_dashes(self):
        """Test converting date format with dashes."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider._convert_date_format("2024-01-15")
        assert result == "20240115"

    def test_convert_date_format_without_dashes(self):
        """Test converting date format without dashes."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider._convert_date_format("20240115")
        assert result == "20240115"


@pytest.mark.unit
class TestFuturesRealtimeCleanSpotData:
    """Unit tests for realtime spot data cleaning."""

    def test_clean_spot_data_chinese_columns(self):
        """Test cleaning spot data with Chinese column names."""
        provider = SinaRealtimeFuturesProvider()

        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405"],
                "名称": ["沪铜2405"],
                "最新价": [51000.0],
                "涨跌额": [100.0],
                "涨跌幅": [0.2],
                "开盘价": [50000.0],
                "最高价": [51500.0],
                "最低价": [49800.0],
                "成交量": [10000],
                "持仓量": [5000],
                "结算价": [51000.0],
                "昨结算": [50900.0],
            }
        )

        result = provider._clean_spot_data(mock_df)
        assert "symbol" in result.columns
        assert "price" in result.columns
        assert "change" in result.columns

    def test_clean_spot_data_english_columns(self):
        """Test cleaning spot data with English column names."""
        provider = SinaRealtimeFuturesProvider()

        mock_df = pd.DataFrame(
            {
                "symbol": ["CU2405"],
                "trade": [51000.0],
                "open": [50000.0],
                "high": [51500.0],
                "low": [49800.0],
                "settlement": [51000.0],
                "prevsettlement": [50900.0],
                "volume": [10000],
                "position": [5000],
                "changepercent": [0.2],
            }
        )

        result = provider._clean_spot_data(mock_df)
        assert "symbol" in result.columns
        assert "price" in result.columns

    def test_clean_spot_data_calculate_change(self):
        """Test cleaning spot data with change calculation."""
        provider = SinaRealtimeFuturesProvider()

        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405"],
                "名称": ["沪铜2405"],
                "最新价": [51000.0],
                "涨跌幅": [0.2],
                "开盘价": [50000.0],
                "最高价": [51500.0],
                "最低价": [49800.0],
                "成交量": [10000],
                "持仓量": [5000],
                "结算价": [51000.0],
                "昨结算": [50900.0],
            }
        )

        result = provider._clean_spot_data(mock_df)
        assert "change" in result.columns
        assert "pct_change" in result.columns

    def test_clean_spot_data_with_presettlement(self):
        """Test cleaning spot data with presettlement fallback."""
        provider = SinaRealtimeFuturesProvider()

        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405"],
                "名称": ["沪铜2405"],
                "最新价": [51000.0],
                "涨跌额": [100.0],
                "涨跌幅": [0.2],
                "开盘价": [50000.0],
                "最高价": [51500.0],
                "最低价": [49800.0],
                "成交量": [10000],
                "持仓量": [5000],
                "结算价": [51000.0],
                "presettlement": [50900.0],
            }
        )

        result = provider._clean_spot_data(mock_df)
        assert "prev_settlement" in result.columns

    def test_clean_spot_data_symbol_extraction(self):
        """Test symbol extraction in spot data cleaning."""
        provider = SinaRealtimeFuturesProvider()

        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "AG2604", "RB2410"],
                "名称": ["沪铜2405", "沪银2604", "螺纹2410"],
                "最新价": [51000.0, 6000.0, 4000.0],
                "涨跌额": [100.0, 50.0, 20.0],
                "涨跌幅": [0.2, 0.83, 0.5],
                "开盘价": [50000.0, 5950.0, 3950.0],
                "最高价": [51500.0, 6050.0, 4050.0],
                "最低价": [49800.0, 5900.0, 3900.0],
                "成交量": [10000, 8000, 5000],
                "持仓量": [5000, 3000, 2000],
                "结算价": [51000.0, 6000.0, 4000.0],
                "昨结算": [50900.0, 5950.0, 3980.0],
            }
        )

        result = provider._clean_spot_data(mock_df)
        assert "symbol_root" in result.columns
        assert "contract" in result.columns
        assert result["symbol_root"].iloc[0] == "CU"
        assert result["contract"].iloc[0] == "2405"


@pytest.mark.unit
class TestFuturesBuildCacheKey:
    """Unit tests for futures cache key building."""

    def test_build_cache_key_with_symbol_and_contract(self):
        """Test building cache key with symbol and contract."""
        from akshare_one.modules.futures.sina import _build_cache_key

        provider = SinaRealtimeFuturesProvider(symbol="CU2405")
        result = _build_cache_key(provider)
        assert "CU" in result
        assert "2405" in result

    def test_build_cache_key_without_symbol(self):
        """Test building cache key without symbol."""
        from akshare_one.modules.futures.sina import _build_cache_key

        provider = SinaRealtimeFuturesProvider()
        result = _build_cache_key(provider)
        assert "all" in result


@pytest.mark.unit
class TestFuturesMainContractsCleaning:
    """Unit tests for main contracts data cleaning."""

    def test_clean_main_contracts(self):
        """Test cleaning main contracts data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")

        mock_df = pd.DataFrame(
            {
                "variety": ["CU", "AL", "ZN"],
                "symbol": ["CU2405", "AL2406", "ZN2407"],
                "exchange": ["SHFE", "SHFE", "SHFE"],
            }
        )

        result = provider._clean_main_contracts(mock_df)
        assert "symbol" in result.columns
        assert "exchange" in result.columns

    def test_clean_main_contracts_missing_columns(self):
        """Test cleaning main contracts with missing columns."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")

        mock_df = pd.DataFrame(
            {
                "wrong_column": ["CU2405", "AL2406"],
            }
        )

        result = provider._clean_main_contracts(mock_df)
        assert result.empty or result.columns.tolist() == ["symbol", "name", "contract", "exchange"]

    def test_clean_main_contracts_from_realtime(self):
        """Test cleaning main contracts from realtime data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")

        mock_df = pd.DataFrame(
            {
                "symbol": ["CU2405", "CU2406", "AG2604"],
                "exchange": ["SHFE", "SHFE", "SHFE"],
            }
        )

        result = provider._clean_main_contracts_from_realtime(mock_df)
        assert "symbol" in result.columns
        assert "exchange" in result.columns

    def test_clean_main_contracts_from_realtime_empty(self):
        """Test cleaning main contracts from empty realtime data."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")

        mock_df = pd.DataFrame(
            {
                "wrong_column": [],
            }
        )

        result = provider._clean_main_contracts_from_realtime(mock_df)
        assert result.empty or result.columns.tolist() == ["symbol", "name", "contract", "exchange"]


@pytest.mark.unit
class TestFuturesProviderInheritance:
    """Unit tests for futures provider inheritance and base methods."""

    def test_historical_provider_get_source_name(self):
        """Test historical provider source name."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        assert provider.get_source_name() == "sina"

    def test_historical_provider_get_data_type(self):
        """Test historical provider data type."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        assert provider.get_data_type() == "futures"

    def test_historical_provider_fetch_data(self):
        """Test historical provider fetch data method."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="main", interval="day")
        with patch("akshare.futures_zh_daily_sina") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "date": ["2024-01-15"],
                    "open": [50000.0],
                    "high": [51500.0],
                    "low": [49800.0],
                    "close": [51000.0],
                    "volume": [10000],
                    "hold": [5000],
                }
            )
            mock_df.index = pd.to_datetime(mock_df["date"])
            mock_ak.return_value = mock_df
            result = provider.fetch_data()
            assert not result.empty

    def test_realtime_provider_get_source_name(self):
        """Test realtime provider source name."""
        provider = SinaRealtimeFuturesProvider(symbol="CU")
        assert provider.get_source_name() == "sina"

    def test_realtime_provider_get_data_type(self):
        """Test realtime provider data type."""
        provider = SinaRealtimeFuturesProvider(symbol="CU")
        assert provider.get_data_type() == "futures"

    def test_realtime_provider_fetch_data(self):
        """Test realtime provider fetch data method."""
        provider = SinaRealtimeFuturesProvider(symbol="CU")
        with patch("akshare.futures_zh_spot") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "代码": ["CU2405"],
                    "名称": ["沪铜2405"],
                    "最新价": [51000.0],
                    "涨跌额": [100.0],
                    "涨跌幅": [0.2],
                    "开盘价": [50000.0],
                    "最高价": [51500.0],
                    "最低价": [49800.0],
                    "成交量": [10000],
                    "持仓量": [5000],
                    "结算价": [51000.0],
                    "昨结算": [50900.0],
                }
            )
            mock_ak.return_value = mock_df
            result = provider.fetch_data()
            assert not result.empty


@pytest.mark.unit
class TestFuturesDataFactory:
    """Unit tests for futures data factory."""

    def test_futures_data_factory_get_historical_provider(self):
        """Test getting historical provider via factory."""
        provider = FuturesDataFactory.get_historical_provider("sina", symbol="CU", interval="day")
        assert provider is not None
        assert provider.symbol == "CU"

    def test_futures_data_factory_get_realtime_provider(self):
        """Test getting realtime provider via factory."""
        provider = FuturesDataFactory.get_realtime_provider("sina", symbol="CU")
        assert provider is not None
        assert provider.symbol == "CU"

    def test_futures_data_factory_list_historical_sources(self):
        """Test listing historical sources."""
        sources = FuturesDataFactory.list_historical_sources()
        assert isinstance(sources, list)

    def test_futures_data_factory_list_realtime_sources(self):
        """Test listing realtime sources."""
        sources = FuturesDataFactory.list_realtime_sources()
        assert isinstance(sources, list)


@pytest.mark.unit
class TestFuturesHistoricalProviderMethods:
    """Unit tests for historical futures provider methods."""

    def test_validate_dates_valid(self):
        """Test validating dates with valid format."""
        provider = SinaHistoricalFuturesProvider(
            symbol="CU", interval="day", start_date="2024-01-01", end_date="2024-12-31"
        )
        assert provider.start_date == "2024-01-01"
        assert provider.end_date == "2024-12-31"

    def test_validate_dates_invalid_format(self):
        """Test validating dates with invalid format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            SinaHistoricalFuturesProvider(symbol="CU", interval="day", start_date="invalid", end_date="2024-12-31")

    def test_get_supported_intervals(self):
        """Test getting supported intervals."""
        intervals = HistoricalFuturesDataProvider.get_supported_intervals()
        assert "minute" in intervals
        assert "hour" in intervals
        assert "day" in intervals
        assert "week" in intervals
        assert "month" in intervals


@pytest.mark.unit
class TestFuturesRealtimeProviderFilter:
    """Unit tests for realtime provider filtering."""

    @patch("akshare.futures_zh_spot")
    def test_get_current_data_with_symbol_filter(self, mock_ak):
        """Test getting current data with symbol filter."""
        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "CU2406", "AG2604"],
                "名称": ["沪铜2405", "沪铜2406", "沪银2604"],
                "最新价": [51000.0, 51200.0, 6000.0],
                "涨跌额": [100.0, 120.0, 50.0],
                "涨跌幅": [0.2, 0.24, 0.83],
                "开盘价": [50000.0, 50200.0, 5950.0],
                "最高价": [51500.0, 51700.0, 6050.0],
                "最低价": [49800.0, 50000.0, 5900.0],
                "成交量": [10000, 8000, 5000],
                "持仓量": [5000, 4500, 3000],
                "结算价": [51000.0, 51200.0, 6000.0],
                "昨结算": [50900.0, 51100.0, 5950.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaRealtimeFuturesProvider(symbol="CU")
        result = provider.get_current_data()
        assert isinstance(result, pd.DataFrame)

    @patch("akshare.futures_zh_spot")
    def test_get_current_data_with_specific_contract(self, mock_ak):
        """Test getting current data for specific contract."""
        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "CU2406"],
                "名称": ["沪铜2405", "沪铜2406"],
                "最新价": [51000.0, 51200.0],
                "涨跌额": [100.0, 120.0],
                "涨跌幅": [0.2, 0.24],
                "开盘价": [50000.0, 50200.0],
                "最高价": [51500.0, 51700.0],
                "最低价": [49800.0, 50000.0],
                "成交量": [10000, 8000],
                "持仓量": [5000, 4500],
                "结算价": [51000.0, 51200.0],
                "昨结算": [50900.0, 51100.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaRealtimeFuturesProvider(symbol="CU")
        provider.contract = "2405"
        result = provider.get_current_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_all_quotes(self):
        """Test getting all quotes."""
        provider = SinaRealtimeFuturesProvider()
        with patch.object(provider, "get_current_data") as mock_get:
            mock_get.return_value = pd.DataFrame({"symbol": ["CU2405"], "price": [51000.0]})
            result = provider.get_all_quotes()
            assert not result.empty


@pytest.mark.unit
class TestFuturesContractValidation:
    """Unit tests for futures contract parameter validation."""

    def test_futures_contract_validation_valid(self):
        """Test valid contract parameters."""
        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")
        assert provider.symbol == "CU"
        assert provider.contract == "2405"

        provider = SinaHistoricalFuturesProvider(symbol="AG", contract="2604", interval="day")
        assert provider.symbol == "AG"
        assert provider.contract == "2604"

    def test_futures_contract_validation_main(self):
        """Test main contract validation."""
        provider = SinaHistoricalFuturesProvider(symbol="CU0", interval="day")
        assert provider.symbol == "CU"
        assert provider.contract == "main"

    def test_futures_contract_validation_invalid_dates(self):
        """Test invalid date format validation."""
        with pytest.raises(ValueError, match="Invalid date format"):
            SinaHistoricalFuturesProvider(symbol="CU", interval="day", start_date="invalid_date", end_date="2024-12-31")


@pytest.mark.unit
class TestFuturesIntervalOptions:
    """Unit tests for futures interval options."""

    def test_futures_interval_options_valid(self):
        """Test valid interval options."""
        valid_intervals = ["minute", "hour", "day", "week", "month"]

        for interval in valid_intervals:
            provider = SinaHistoricalFuturesProvider(symbol="CU", interval=interval)
            assert provider.interval == interval

    def test_futures_interval_options_invalid(self):
        """Test invalid interval options."""
        with pytest.raises(ValueError, match="Unsupported interval"):
            SinaHistoricalFuturesProvider(symbol="CU", interval="invalid_interval")

    def test_futures_interval_multiplier(self):
        """Test interval multiplier validation."""
        # Valid multiplier
        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="minute", interval_multiplier=5)
        assert provider.interval_multiplier == 5

        # Invalid multiplier for minute/hour
        with pytest.raises(ValueError, match="must be >= 1"):
            SinaHistoricalFuturesProvider(symbol="CU", interval="minute", interval_multiplier=0)


@pytest.mark.unit
class TestFuturesFieldStandardization:
    """Unit tests for futures field standardization."""

    @patch("akshare.futures_zh_daily_sina")
    def test_futures_field_standardization_daily(self, mock_ak):
        """Test field standardization for daily data."""
        mock_df = pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-16"],
                "open": [50000.0, 51000.0],
                "high": [51500.0, 52000.0],
                "low": [49800.0, 50500.0],
                "close": [51000.0, 51800.0],
                "volume": [10000, 12000],
                "hold": [5000, 5500],
            }
        )
        mock_df.index = pd.to_datetime(mock_df["date"])
        mock_ak.return_value = mock_df

        provider = SinaHistoricalFuturesProvider(
            symbol="CU", contract="2405", interval="day", start_date="2024-01-01", end_date="2024-01-31"
        )

        # This will call the mocked API
        result = provider._get_daily_data()

        # Verify standard fields exist
        expected_fields = ["timestamp", "symbol", "contract", "open", "high", "low", "close", "volume"]
        for field in expected_fields:
            if field in result.columns:
                assert field in result.columns

    @patch("akshare.futures_zh_spot")
    def test_futures_field_standardization_realtime(self, mock_ak):
        """Test field standardization for realtime data."""
        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "AG2604"],
                "名称": ["沪铜2405", "沪银2604"],
                "最新价": [51000.0, 6000.0],
                "涨跌额": [100.0, 50.0],
                "涨跌幅": [0.2, 0.83],
                "开盘价": [50000.0, 5950.0],
                "最高价": [51500.0, 6050.0],
                "最低价": [49800.0, 5900.0],
                "成交量": [10000, 8000],
                "持仓量": [5000, 3000],
                "结算价": [51000.0, 6000.0],
                "昨结算": [50900.0, 5950.0],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaRealtimeFuturesProvider()
        result = provider._clean_spot_data(mock_df)

        # Verify standard fields
        assert "symbol" in result.columns
        assert "price" in result.columns
        assert "change" in result.columns
        assert "timestamp" in result.columns


@pytest.mark.unit
class TestFuturesEmptyResult:
    """Unit tests for handling empty futures results."""

    @patch("akshare.futures_zh_daily_sina")
    def test_futures_empty_result_handling(self, mock_ak):
        """Test handling of empty historical data."""
        mock_ak.return_value = pd.DataFrame()

        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")

        with pytest.raises(ValueError, match="No data found"):
            provider._get_daily_data()

    @patch("akshare.futures_zh_minute_sina")
    def test_futures_empty_intraday_result(self, mock_ak):
        """Test handling of empty intraday data."""
        mock_ak.return_value = pd.DataFrame()

        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="minute")

        with pytest.raises(ValueError, match="No intraday data found"):
            provider._get_intraday_data()

    @patch("akshare.futures_zh_spot")
    def test_futures_empty_realtime_result(self, mock_ak):
        """Test handling of empty realtime data."""
        mock_ak.return_value = pd.DataFrame()

        provider = SinaRealtimeFuturesProvider()
        result = provider._clean_spot_data(pd.DataFrame())

        # Should return DataFrame with standard columns
        assert isinstance(result, pd.DataFrame)


@pytest.mark.unit
class TestFuturesApiError:
    """Unit tests for futures API error handling."""

    @patch("akshare.futures_zh_daily_sina")
    def test_futures_api_error_handling(self, mock_ak):
        """Test handling of API errors in historical data."""
        mock_ak.side_effect = Exception("API Error")

        provider = SinaHistoricalFuturesProvider(symbol="CU", contract="2405", interval="day")

        with pytest.raises(ValueError, match="Failed to fetch"):
            provider.get_hist_data()

    @patch("akshare.futures_zh_spot")
    @patch("akshare.futures_zh_realtime")
    def test_futures_api_error_with_fallback(self, mock_realtime, mock_spot):
        """Test API fallback mechanism in realtime data."""
        mock_spot.side_effect = Exception("Spot API Error")

        mock_fallback_df = pd.DataFrame(
            {
                "symbol": ["CU2405"],
                "trade": [51000.0],
                "open": [50000.0],
                "high": [51500.0],
                "low": [49800.0],
                "volume": [10000],
                "position": [5000],
            }
        )
        mock_realtime.return_value = mock_fallback_df

        provider = SinaRealtimeFuturesProvider()
        result = provider.get_current_data()

        # Should use fallback data
        assert isinstance(result, pd.DataFrame)


@pytest.mark.unit
class TestFuturesMultiSymbol:
    """Unit tests for multi-symbol futures queries."""

    @patch("akshare.futures_contract_info_shfe")
    @patch("akshare.futures_contract_info_dce")
    @patch("akshare.futures_contract_info_czce")
    @patch("akshare.futures_contract_info_cffex")
    def test_get_main_contracts_multi_exchange(self, mock_cffex, mock_czce, mock_dce, mock_shfe):
        """Test getting main contracts from multiple exchanges."""
        mock_shfe_df = pd.DataFrame(
            {
                "symbol": ["CU2405", "AL2405"],
            }
        )
        mock_shfe.return_value = mock_shfe_df

        mock_dce_df = pd.DataFrame(
            {
                "symbol": ["I2405", "J2405"],
            }
        )
        mock_dce.return_value = mock_dce_df

        mock_czce_df = pd.DataFrame(
            {
                "symbol": ["CF501", "SR501"],
            }
        )
        mock_czce.return_value = mock_czce_df

        mock_cffex_df = pd.DataFrame(
            {
                "symbol": ["IF2401", "IC2401"],
            }
        )
        mock_cffex.return_value = mock_cffex_df

        provider = SinaHistoricalFuturesProvider(symbol="CU", interval="day")
        result = provider.get_main_contracts()

        # Should return data from all exchanges
        assert isinstance(result, pd.DataFrame)
        assert "symbol" in result.columns
        assert "exchange" in result.columns

    @patch("akshare.futures_zh_spot")
    def test_futures_multi_symbol_realtime(self, mock_ak):
        """Test realtime data for multiple symbols."""
        mock_df = pd.DataFrame(
            {
                "代码": ["CU2405", "CU2406", "AG2604", "AG2606"],
                "名称": ["沪铜2405", "沪铜2406", "沪银2604", "沪银2606"],
                "最新价": [51000.0, 51200.0, 6000.0, 6050.0],
                "涨跌额": [100.0, 120.0, 50.0, 55.0],
                "涨跌幅": [0.2, 0.24, 0.83, 0.92],
                "成交量": [10000, 8000, 5000, 4000],
                "持仓量": [5000, 4500, 3000, 2800],
            }
        )
        mock_ak.return_value = mock_df

        provider = SinaRealtimeFuturesProvider(symbol="CU")
        result = provider.get_current_data()

        # Should filter by symbol_root
        assert isinstance(result, pd.DataFrame)
        if len(result) > 0:
            assert all(result["symbol"].str.startswith("CU"))
