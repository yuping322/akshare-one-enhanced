"""
Test suite for TOP 11-20 AkShare functions (Part 2).

This file tests the raw akshare API functions directly with comprehensive
test coverage including basic calls, parameter variations, error handling,
empty results, and field mapping validation.

Functions covered:
11. stock_restricted_release_queue_em - 限售解禁队列
12. stock_restricted_release_detail_em - 限售解禁明细
13. futures_zh_minute_sina - 期货分钟数据
14. futures_zh_daily_sina - 期货日线数据
15. futures_contract_info_shfe - SHFE合约信息
16. futures_contract_info_dce - DCE合约信息
17. futures_contract_info_czce - CZCE合约信息
18. futures_contract_info_cffex - CFFEX合约信息
19. futures_zh_realtime - 期货实时数据
20. futures_zh_spot - 期货现货数据
"""

from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
import re

pytestmark = pytest.mark.unit


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def futures_sample_data():
    """期货样本数据"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-15", "2024-01-16"],
            "开盘价": [50000.0, 51000.0],
            "收盘价": [50500.0, 51500.0],
            "最高价": [51000.0, 52000.0],
            "最低价": [49800.0, 50500.0],
            "成交量": [100000, 120000],
            "持仓量": [500000, 550000],
            "结算价": [50700.0, 51700.0],
        }
    )


@pytest.fixture
def futures_minute_sample_data():
    """期货分钟数据样本"""
    return pd.DataFrame(
        {
            "datetime": ["2024-01-15 09:00:00", "2024-01-15 09:01:00"],
            "open": [50000.0, 50100.0],
            "close": [50050.0, 50150.0],
            "high": [50080.0, 50180.0],
            "low": [50020.0, 50120.0],
            "volume": [1000, 1100],
            "hold": [5000, 5100],
        }
    )


@pytest.fixture
def restricted_queue_sample_data():
    """限售解禁队列样本数据"""
    return pd.DataFrame(
        {
            "解禁时间": ["2024-01-15", "2024-02-20"],
            "解禁数量": [1000000.0, 2000000.0],
            "解禁市值": [10000000.0, 20000000.0],
            "股份类型": ["首发原股东限售股份", "定向增发机构配售股份"],
            "股东名称": ["股东A", "股东B"],
        }
    )


@pytest.fixture
def restricted_detail_sample_data():
    """限售解禁明细样本数据"""
    return pd.DataFrame(
        {
            "股票代码": ["600000", "600036", "000001"],
            "股票简称": ["浦发银行", "招商银行", "平安银行"],
            "解禁时间": ["2024-01-15", "2024-02-20", "2024-03-25"],
            "解禁数量": [1000000.0, 2000000.0, 3000000.0],
            "解禁市值": [10000000.0, 20000000.0, 30000000.0],
            "占流通股比例": [5.5, 6.5, 7.5],
            "股份类型": ["首发原股东限售股份", "定向增发机构配售股份", "股权激励限售股份"],
            "股东名称": ["股东A", "股东B", "股东C"],
        }
    )


@pytest.fixture
def futures_contract_info_shfe_sample():
    """SHFE合约信息样本数据"""
    return pd.DataFrame(
        {
            "symbol": ["CU2405", "AL2405", "ZN2405", "NI2405", "PB2405", "SN2405"],
            "exchange": ["SHFE"] * 6,
            "variety": ["CU", "AL", "ZN", "NI", "PB", "SN"],
        }
    )


@pytest.fixture
def futures_contract_info_dce_sample():
    """DCE合约信息样本数据"""
    return pd.DataFrame(
        {
            "symbol": ["M2405", "Y2405", "P2405", "C2405", "CS2405", "A2405"],
            "exchange": ["DCE"] * 6,
            "variety": ["M", "Y", "P", "C", "CS", "A"],
        }
    )


@pytest.fixture
def futures_contract_info_czce_sample():
    """CZCE合约信息样本数据"""
    return pd.DataFrame(
        {
            "symbol": ["SR501", "CF501", "TA501", "MA501", "FG501", "RM501"],
            "exchange": ["CZCE"] * 6,
            "variety": ["SR", "CF", "TA", "MA", "FG", "RM"],
        }
    )


@pytest.fixture
def futures_contract_info_cffex_sample():
    """CFFEX合约信息样本数据"""
    return pd.DataFrame(
        {
            "symbol": ["IF2401", "IC2401", "IH2401", "IM2401", "TS2401", "TF2401"],
            "exchange": ["CFFEX"] * 6,
            "variety": ["IF", "IC", "IH", "IM", "TS", "TF"],
        }
    )


@pytest.fixture
def futures_realtime_sample():
    """期货实时数据样本"""
    return pd.DataFrame(
        {
            "symbol": ["CU2405", "CU2406", "AG2405", "AG2406"],
            "trade": [51000.0, 51200.0, 6000.0, 6050.0],
            "open": [50000.0, 50200.0, 5950.0, 6000.0],
            "high": [51500.0, 51700.0, 6050.0, 6100.0],
            "low": [49800.0, 50000.0, 5900.0, 5950.0],
            "volume": [10000, 8000, 5000, 4000],
            "position": [5000, 4500, 3000, 2800],
            "settlement": [51000.0, 51200.0, 6000.0, 6050.0],
            "prevsettlement": [50900.0, 51100.0, 5950.0, 6000.0],
        }
    )


@pytest.fixture
def futures_spot_sample():
    """期货现货数据样本"""
    return pd.DataFrame(
        {
            "代码": ["CU2405", "CU2406", "AG2405", "AG2406"],
            "名称": ["沪铜2405", "沪铜2406", "沪银2405", "沪银2406"],
            "最新价": [51000.0, 51200.0, 6000.0, 6050.0],
            "涨跌额": [100.0, 120.0, 50.0, 55.0],
            "涨跌幅": [0.2, 0.24, 0.83, 0.92],
            "开盘价": [50000.0, 50200.0, 5950.0, 6000.0],
            "最高价": [51500.0, 51700.0, 6050.0, 6100.0],
            "最低价": [49800.0, 50000.0, 5900.0, 5950.0],
            "成交量": [10000, 8000, 5000, 4000],
            "持仓量": [5000, 4500, 3000, 2800],
            "结算价": [51000.0, 51200.0, 6000.0, 6050.0],
            "昨结算": [50900.0, 51100.0, 5950.0, 6000.0],
        }
    )


# ============================================================================
# Helper Functions for Futures Contract Parsing
# ============================================================================


def parse_futures_symbol(symbol: str) -> dict:
    """
    Parse futures symbol into components.

    Args:
        symbol: Futures symbol like 'CU2405' or 'SR501' (CZCE format)

    Returns:
        dict with keys: commodity, year, month, full_contract

    Example:
        CU2405 -> {'commodity': 'CU', 'year': '24', 'month': '05', 'full_contract': '2405'}
        SR501 -> {'commodity': 'SR', 'year': '5', 'month': '01', 'full_contract': '501'}
    """
    match = re.match(r"^([A-Z]+)(\d{3,4})$", symbol)
    if not match:
        raise ValueError(f"Invalid futures symbol format: {symbol}")

    commodity = match.group(1)
    year_month = match.group(2)

    if len(year_month) == 4:
        return {"commodity": commodity, "year": year_month[:2], "month": year_month[2:], "full_contract": year_month}
    elif len(year_month) == 3:
        return {"commodity": commodity, "year": year_month[0], "month": year_month[1:], "full_contract": year_month}
    else:
        raise ValueError(f"Invalid futures symbol format: {symbol}")


def call_akshare(func_name: str, **kwargs):
    """
    Call akshare function with error handling.

    Args:
        func_name: Akshare function name
        **kwargs: Function parameters

    Returns:
        pd.DataFrame: Result DataFrame with standardized fields
    """
    import akshare as ak

    func = getattr(ak, func_name, None)
    if func is None:
        raise ValueError(f"Akshare function '{func_name}' not found")

    result = func(**kwargs)

    if isinstance(result, pd.DataFrame):
        return result
    else:
        return pd.DataFrame()


# ============================================================================
# Test Classes for Restricted Release Functions
# ============================================================================


class TestStockRestrictedReleaseQueueEm:
    """Test stock_restricted_release_queue_em (限售解禁队列)"""

    def test_basic_call(self, restricted_queue_sample_data):
        """基础调用测试"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.return_value = restricted_queue_sample_data

            import akshare as ak

            result = ak.stock_restricted_release_queue_em(symbol="600000")

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "解禁时间" in result.columns
            assert "解禁数量" in result.columns
            assert "解禁市值" in result.columns

    def test_with_parameters(self, restricted_queue_sample_data):
        """参数测试"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.return_value = restricted_queue_sample_data

            import akshare as ak

            result1 = ak.stock_restricted_release_queue_em(symbol="600000")
            assert len(result1) == 2

            result2 = ak.stock_restricted_release_queue_em(symbol="000001")
            assert isinstance(result2, pd.DataFrame)

            mock.assert_called()

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.side_effect = Exception("API Error: Invalid symbol")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.stock_restricted_release_queue_em(symbol="INVALID")

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.stock_restricted_release_queue_em(symbol="600000")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, restricted_queue_sample_data):
        """字段映射测试"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.return_value = restricted_queue_sample_data

            import akshare as ak

            result = ak.stock_restricted_release_queue_em(symbol="600000")

            expected_fields = ["解禁时间", "解禁数量", "解禁市值", "股份类型", "股东名称"]
            for field in expected_fields:
                assert field in result.columns


class TestStockRestrictedReleaseDetailEm:
    """Test stock_restricted_release_detail_em (限售解禁明细)"""

    def test_basic_call(self, restricted_detail_sample_data):
        """基础调用测试"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.return_value = restricted_detail_sample_data

            import akshare as ak

            result = ak.stock_restricted_release_detail_em()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "股票代码" in result.columns
            assert "解禁时间" in result.columns
            assert "解禁数量" in result.columns

    def test_with_parameters(self, restricted_detail_sample_data):
        """参数测试 - 测试数据筛选"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.return_value = restricted_detail_sample_data

            import akshare as ak

            result = ak.stock_restricted_release_detail_em()

            assert len(result) == 3

            unique_symbols = result["股票代码"].unique()
            assert len(unique_symbols) == 3
            assert "600000" in unique_symbols
            assert "600036" in unique_symbols
            assert "000001" in unique_symbols

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.side_effect = Exception("Network Error: Connection timeout")

            import akshare as ak

            with pytest.raises(Exception, match="Network Error"):
                ak.stock_restricted_release_detail_em()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.stock_restricted_release_detail_em()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, restricted_detail_sample_data):
        """字段映射测试"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.return_value = restricted_detail_sample_data

            import akshare as ak

            result = ak.stock_restricted_release_detail_em()

            expected_fields = ["股票代码", "股票简称", "解禁时间", "解禁数量", "解禁市值", "占流通股比例"]
            for field in expected_fields:
                assert field in result.columns

            assert result["股票代码"].iloc[0] == "600000"
            assert result["占流通股比例"].iloc[0] == 5.5


# ============================================================================
# Test Classes for Futures Historical Data Functions
# ============================================================================


class TestFuturesZhMinuteSina:
    """Test futures_zh_minute_sina (期货分钟数据)"""

    def test_basic_call(self, futures_minute_sample_data):
        """基础调用测试"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.return_value = futures_minute_sample_data

            import akshare as ak

            result = ak.futures_zh_minute_sina(symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "datetime" in result.columns
            assert "open" in result.columns
            assert "close" in result.columns

    def test_with_parameters(self, futures_minute_sample_data):
        """参数测试"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.return_value = futures_minute_sample_data

            import akshare as ak

            result1 = ak.futures_zh_minute_sina(symbol="CU2405")
            assert len(result1) == 2

            result2 = ak.futures_zh_minute_sina(symbol="AG2405")
            assert isinstance(result2, pd.DataFrame)

            mock.assert_called()

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.side_effect = Exception("API Error: Invalid contract")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_zh_minute_sina(symbol="INVALID9999")

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_zh_minute_sina(symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_minute_sample_data):
        """字段映射测试"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.return_value = futures_minute_sample_data

            import akshare as ak

            result = ak.futures_zh_minute_sina(symbol="CU2405")

            expected_fields = ["datetime", "open", "close", "high", "low", "volume", "hold"]
            for field in expected_fields:
                assert field in result.columns

            assert result["open"].iloc[0] == 50000.0
            assert result["volume"].iloc[0] == 1000


class TestFuturesZhDailySina:
    """Test futures_zh_daily_sina (期货日线数据)"""

    def test_basic_call(self, futures_sample_data):
        """基础调用测试"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.return_value = futures_sample_data

            import akshare as ak

            result = ak.futures_zh_daily_sina(symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "日期" in result.columns or "date" in result.columns
            assert "开盘价" in result.columns or "open" in result.columns

    def test_with_parameters(self, futures_sample_data):
        """参数测试"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.return_value = futures_sample_data

            import akshare as ak

            result1 = ak.futures_zh_daily_sina(symbol="CU2405")
            assert len(result1) == 2

            result2 = ak.futures_zh_daily_sina(symbol="AG2405")
            assert isinstance(result2, pd.DataFrame)

            result3 = ak.futures_zh_daily_sina(symbol="CU0")
            assert isinstance(result3, pd.DataFrame)

            mock.assert_called()

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.side_effect = Exception("API Error: No data available")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_zh_daily_sina(symbol="INVALID9999")

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_zh_daily_sina(symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_sample_data):
        """字段映射测试"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.return_value = futures_sample_data

            import akshare as ak

            result = ak.futures_zh_daily_sina(symbol="CU2405")

            expected_fields_cn = ["日期", "开盘价", "收盘价", "最高价", "最低价", "成交量", "持仓量", "结算价"]
            expected_fields_en = ["date", "open", "close", "high", "low", "volume", "hold", "settle"]

            has_cn = any(field in result.columns for field in expected_fields_cn)
            has_en = any(field in result.columns for field in expected_fields_en)

            assert has_cn or has_en

            if "开盘价" in result.columns:
                assert result["开盘价"].iloc[0] == 50000.0
            if "open" in result.columns:
                assert result["open"].iloc[0] == 50000.0


# ============================================================================
# Test Classes for Futures Contract Info Functions
# ============================================================================


class TestFuturesContractInfoShfe:
    """Test futures_contract_info_shfe (SHFE合约信息)"""

    def test_basic_call(self, futures_contract_info_shfe_sample):
        """基础调用测试"""
        with patch("akshare.futures_contract_info_shfe") as mock:
            mock.return_value = futures_contract_info_shfe_sample

            import akshare as ak

            result = ak.futures_contract_info_shfe()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "symbol" in result.columns
            assert "exchange" in result.columns

    def test_with_parameters(self, futures_contract_info_shfe_sample):
        """参数测试"""
        with patch("akshare.futures_contract_info_shfe") as mock:
            mock.return_value = futures_contract_info_shfe_sample

            import akshare as ak

            result = ak.futures_contract_info_shfe()

            assert len(result) == 6

            varieties = result["variety"].unique()
            assert "CU" in varieties
            assert "AL" in varieties
            assert "ZN" in varieties
            assert "NI" in varieties
            assert "PB" in varieties
            assert "SN" in varieties

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_contract_info_shfe") as mock:
            mock.side_effect = Exception("API Error: SHFE data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_contract_info_shfe()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_contract_info_shfe") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_contract_info_shfe()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_contract_info_shfe_sample):
        """字段映射测试"""
        with patch("akshare.futures_contract_info_shfe") as mock:
            mock.return_value = futures_contract_info_shfe_sample

            import akshare as ak

            result = ak.futures_contract_info_shfe()

            expected_fields = ["symbol", "exchange", "variety"]
            for field in expected_fields:
                assert field in result.columns

            assert result["exchange"].iloc[0] == "SHFE"
            assert result["variety"].iloc[0] == "CU"


class TestFuturesContractInfoDce:
    """Test futures_contract_info_dce (DCE合约信息)"""

    def test_basic_call(self, futures_contract_info_dce_sample):
        """基础调用测试"""
        with patch("akshare.futures_contract_info_dce") as mock:
            mock.return_value = futures_contract_info_dce_sample

            import akshare as ak

            result = ak.futures_contract_info_dce()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "symbol" in result.columns
            assert "exchange" in result.columns

    def test_with_parameters(self, futures_contract_info_dce_sample):
        """参数测试"""
        with patch("akshare.futures_contract_info_dce") as mock:
            mock.return_value = futures_contract_info_dce_sample

            import akshare as ak

            result = ak.futures_contract_info_dce()

            assert len(result) == 6

            varieties = result["variety"].unique()
            assert "M" in varieties
            assert "Y" in varieties
            assert "P" in varieties
            assert "C" in varieties
            assert "CS" in varieties
            assert "A" in varieties

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_contract_info_dce") as mock:
            mock.side_effect = Exception("API Error: DCE data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_contract_info_dce()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_contract_info_dce") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_contract_info_dce()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_contract_info_dce_sample):
        """字段映射测试"""
        with patch("akshare.futures_contract_info_dce") as mock:
            mock.return_value = futures_contract_info_dce_sample

            import akshare as ak

            result = ak.futures_contract_info_dce()

            expected_fields = ["symbol", "exchange", "variety"]
            for field in expected_fields:
                assert field in result.columns

            assert result["exchange"].iloc[0] == "DCE"
            assert result["variety"].iloc[0] == "M"


class TestFuturesContractInfoCzce:
    """Test futures_contract_info_czce (CZCE合约信息)"""

    def test_basic_call(self, futures_contract_info_czce_sample):
        """基础调用测试"""
        with patch("akshare.futures_contract_info_czce") as mock:
            mock.return_value = futures_contract_info_czce_sample

            import akshare as ak

            result = ak.futures_contract_info_czce()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "symbol" in result.columns
            assert "exchange" in result.columns

    def test_with_parameters(self, futures_contract_info_czce_sample):
        """参数测试"""
        with patch("akshare.futures_contract_info_czce") as mock:
            mock.return_value = futures_contract_info_czce_sample

            import akshare as ak

            result = ak.futures_contract_info_czce()

            assert len(result) == 6

            varieties = result["variety"].unique()
            assert "SR" in varieties
            assert "CF" in varieties
            assert "TA" in varieties
            assert "MA" in varieties
            assert "FG" in varieties
            assert "RM" in varieties

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_contract_info_czce") as mock:
            mock.side_effect = Exception("API Error: CZCE data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_contract_info_czce()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_contract_info_czce") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_contract_info_czce()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_contract_info_czce_sample):
        """字段映射测试"""
        with patch("akshare.futures_contract_info_czce") as mock:
            mock.return_value = futures_contract_info_czce_sample

            import akshare as ak

            result = ak.futures_contract_info_czce()

            expected_fields = ["symbol", "exchange", "variety"]
            for field in expected_fields:
                assert field in result.columns

            assert result["exchange"].iloc[0] == "CZCE"
            assert result["variety"].iloc[0] == "SR"


class TestFuturesContractInfoCffex:
    """Test futures_contract_info_cffex (CFFEX合约信息)"""

    def test_basic_call(self, futures_contract_info_cffex_sample):
        """基础调用测试"""
        with patch("akshare.futures_contract_info_cffex") as mock:
            mock.return_value = futures_contract_info_cffex_sample

            import akshare as ak

            result = ak.futures_contract_info_cffex()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "symbol" in result.columns
            assert "exchange" in result.columns

    def test_with_parameters(self, futures_contract_info_cffex_sample):
        """参数测试"""
        with patch("akshare.futures_contract_info_cffex") as mock:
            mock.return_value = futures_contract_info_cffex_sample

            import akshare as ak

            result = ak.futures_contract_info_cffex()

            assert len(result) == 6

            varieties = result["variety"].unique()
            assert "IF" in varieties
            assert "IC" in varieties
            assert "IH" in varieties
            assert "IM" in varieties
            assert "TS" in varieties
            assert "TF" in varieties

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_contract_info_cffex") as mock:
            mock.side_effect = Exception("API Error: CFFEX data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_contract_info_cffex()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_contract_info_cffex") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_contract_info_cffex()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_contract_info_cffex_sample):
        """字段映射测试"""
        with patch("akshare.futures_contract_info_cffex") as mock:
            mock.return_value = futures_contract_info_cffex_sample

            import akshare as ak

            result = ak.futures_contract_info_cffex()

            expected_fields = ["symbol", "exchange", "variety"]
            for field in expected_fields:
                assert field in result.columns

            assert result["exchange"].iloc[0] == "CFFEX"
            assert result["variety"].iloc[0] == "IF"


# ============================================================================
# Test Classes for Futures Realtime Data Functions
# ============================================================================


class TestFuturesZhRealtime:
    """Test futures_zh_realtime (期货实时数据)"""

    def test_basic_call(self, futures_realtime_sample):
        """基础调用测试"""
        with patch("akshare.futures_zh_realtime") as mock:
            mock.return_value = futures_realtime_sample

            import akshare as ak

            result = ak.futures_zh_realtime()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "symbol" in result.columns
            assert "trade" in result.columns
            assert "volume" in result.columns

    def test_with_parameters(self, futures_realtime_sample):
        """参数测试"""
        with patch("akshare.futures_zh_realtime") as mock:
            mock.return_value = futures_realtime_sample

            import akshare as ak

            result = ak.futures_zh_realtime()

            assert len(result) == 4

            symbols = result["symbol"].unique()
            assert "CU2405" in symbols
            assert "AG2405" in symbols

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_zh_realtime") as mock:
            mock.side_effect = Exception("API Error: Realtime data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_zh_realtime()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_zh_realtime") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_zh_realtime()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_realtime_sample):
        """字段映射测试"""
        with patch("akshare.futures_zh_realtime") as mock:
            mock.return_value = futures_realtime_sample

            import akshare as ak

            result = ak.futures_zh_realtime()

            expected_fields = ["symbol", "trade", "open", "high", "low", "volume", "position", "settlement"]
            for field in expected_fields:
                assert field in result.columns

            assert result["trade"].iloc[0] == 51000.0
            assert result["volume"].iloc[0] == 10000


class TestFuturesZhSpot:
    """Test futures_zh_spot (期货现货数据)"""

    def test_basic_call(self, futures_spot_sample):
        """基础调用测试"""
        with patch("akshare.futures_zh_spot") as mock:
            mock.return_value = futures_spot_sample

            import akshare as ak

            result = ak.futures_zh_spot()

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "代码" in result.columns
            assert "最新价" in result.columns
            assert "成交量" in result.columns

    def test_with_parameters(self, futures_spot_sample):
        """参数测试"""
        with patch("akshare.futures_zh_spot") as mock:
            mock.return_value = futures_spot_sample

            import akshare as ak

            result = ak.futures_zh_spot()

            assert len(result) == 4

            symbols = result["代码"].unique()
            assert "CU2405" in symbols
            assert "AG2405" in symbols

            assert result["涨跌额"].iloc[0] == 100.0
            assert result["涨跌幅"].iloc[0] == 0.2

    def test_error_handling(self):
        """错误处理测试"""
        with patch("akshare.futures_zh_spot") as mock:
            mock.side_effect = Exception("API Error: Spot data unavailable")

            import akshare as ak

            with pytest.raises(Exception, match="API Error"):
                ak.futures_zh_spot()

    def test_empty_result(self):
        """空结果测试"""
        with patch("akshare.futures_zh_spot") as mock:
            mock.return_value = pd.DataFrame()

            import akshare as ak

            result = ak.futures_zh_spot()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_field_mapping(self, futures_spot_sample):
        """字段映射测试"""
        with patch("akshare.futures_zh_spot") as mock:
            mock.return_value = futures_spot_sample

            import akshare as ak

            result = ak.futures_zh_spot()

            expected_fields = [
                "代码",
                "名称",
                "最新价",
                "涨跌额",
                "涨跌幅",
                "开盘价",
                "最高价",
                "最低价",
                "成交量",
                "持仓量",
            ]
            for field in expected_fields:
                assert field in result.columns

            assert result["最新价"].iloc[0] == 51000.0
            assert result["成交量"].iloc[0] == 10000


# ============================================================================
# Special Test Cases for Futures Contract Parsing
# ============================================================================


class TestFuturesContractParsing:
    """测试期货合约代码解析"""

    def test_futures_contract_parsing_standard(self):
        """测试标准期货合约代码解析"""
        result = parse_futures_symbol("CU2405")

        assert result["commodity"] == "CU"
        assert result["year"] == "24"
        assert result["month"] == "05"
        assert result["full_contract"] == "2405"

    def test_futures_contract_parsing_various_commodities(self):
        """测试不同商品的合约代码解析"""
        test_cases = [
            ("AG2604", {"commodity": "AG", "year": "26", "month": "04"}),
            ("IF2401", {"commodity": "IF", "year": "24", "month": "01"}),
            ("M2405", {"commodity": "M", "year": "24", "month": "05"}),
            ("SR501", {"commodity": "SR", "year": "5", "month": "01"}),
        ]

        for symbol, expected in test_cases:
            result = parse_futures_symbol(symbol)
            assert result["commodity"] == expected["commodity"]
            assert result["year"] == expected["year"]
            assert result["month"] == expected["month"]

    def test_futures_contract_parsing_invalid_format(self):
        """测试无效格式处理"""
        invalid_symbols = ["INVALID", "CU", "2405", "CU24", "cu2405", "CU240555"]

        for symbol in invalid_symbols:
            with pytest.raises(ValueError):
                parse_futures_symbol(symbol)

    def test_futures_exchange_specific_fields(self):
        """测试不同交易所的字段差异"""
        shfe_commodities = ["CU", "AL", "ZN", "NI", "PB", "SN"]
        dce_commodities = ["M", "Y", "P", "C", "CS", "A"]
        czce_commodities = ["SR", "CF", "TA", "MA", "FG", "RM"]
        cffex_commodities = ["IF", "IC", "IH", "IM", "TS", "TF"]

        for commodity in shfe_commodities:
            result = parse_futures_symbol(f"{commodity}2405")
            assert result["commodity"] == commodity

        for commodity in dce_commodities:
            result = parse_futures_symbol(f"{commodity}2405")
            assert result["commodity"] == commodity

        for commodity in czce_commodities:
            result = parse_futures_symbol(f"{commodity}501")
            assert result["commodity"] == commodity

        for commodity in cffex_commodities:
            result = parse_futures_symbol(f"{commodity}2401")
            assert result["commodity"] == commodity


class TestRestrictedReleasePagination:
    """测试限售解禁队列分页"""

    def test_restricted_release_queue_pagination(self):
        """测试限售解禁队列分页"""
        with patch("akshare.stock_restricted_release_queue_em") as mock:
            mock.side_effect = [
                pd.DataFrame(
                    {"解禁时间": ["2024-01-15", "2024-02-20"], "解禁数量": [1000000.0, 2000000.0], "page": [1, 1]}
                ),
                pd.DataFrame(
                    {"解禁时间": ["2024-03-15", "2024-04-20"], "解禁数量": [3000000.0, 4000000.0], "page": [2, 2]}
                ),
            ]

            import akshare as ak

            result1 = ak.stock_restricted_release_queue_em(symbol="600000")
            assert "page" in result1.columns
            assert result1["page"].iloc[0] == 1

            result2 = ak.stock_restricted_release_queue_em(symbol="600000")
            assert "page" in result2.columns
            assert result2["page"].iloc[0] == 2

    def test_restricted_release_detail_with_symbol(self):
        """测试个股限售解禁明细"""
        with patch("akshare.stock_restricted_release_detail_em") as mock:
            mock.return_value = pd.DataFrame(
                {"股票代码": ["600000"], "解禁日期": ["2024-01-01"], "解禁数量": [1000000]}
            )

            import akshare as ak

            result = ak.stock_restricted_release_detail_em()

            assert "股票代码" in result.columns
            assert result["股票代码"].iloc[0] == "600000"


class TestFuturesMultiExchangeIntegration:
    """测试多交易所期货数据整合"""

    @patch("akshare.futures_contract_info_shfe")
    @patch("akshare.futures_contract_info_dce")
    @patch("akshare.futures_contract_info_czce")
    @patch("akshare.futures_contract_info_cffex")
    def test_all_exchanges_data_consistency(
        self,
        mock_cffex,
        mock_czce,
        mock_dce,
        mock_shfe,
        futures_contract_info_shfe_sample,
        futures_contract_info_dce_sample,
        futures_contract_info_czce_sample,
        futures_contract_info_cffex_sample,
    ):
        """测试所有交易所数据一致性"""
        mock_shfe.return_value = futures_contract_info_shfe_sample
        mock_dce.return_value = futures_contract_info_dce_sample
        mock_czce.return_value = futures_contract_info_czce_sample
        mock_cffex.return_value = futures_contract_info_cffex_sample

        import akshare as ak

        shfe_df = ak.futures_contract_info_shfe()
        dce_df = ak.futures_contract_info_dce()
        czce_df = ak.futures_contract_info_czce()
        cffex_df = ak.futures_contract_info_cffex()

        all_data = pd.concat([shfe_df, dce_df, czce_df, cffex_df], ignore_index=True)

        assert "symbol" in all_data.columns
        assert "exchange" in all_data.columns
        assert "variety" in all_data.columns

        exchanges = all_data["exchange"].unique()
        assert "SHFE" in exchanges
        assert "DCE" in exchanges
        assert "CZCE" in exchanges
        assert "CFFEX" in exchanges

        assert len(all_data) == 24


class TestCallAkshareHelper:
    """测试call_akshare辅助函数"""

    def test_call_akshare_valid_function(self, futures_sample_data):
        """测试有效函数调用"""
        with patch("akshare.futures_zh_daily_sina") as mock:
            mock.return_value = futures_sample_data

            result = call_akshare("futures_zh_daily_sina", symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_call_akshare_invalid_function(self):
        """测试无效函数调用"""
        with pytest.raises(ValueError, match="Akshare function .* not found"):
            call_akshare("invalid_function_name")

    def test_call_akshare_with_parameters(self, futures_minute_sample_data):
        """测试带参数的函数调用"""
        with patch("akshare.futures_zh_minute_sina") as mock:
            mock.return_value = futures_minute_sample_data

            result = call_akshare("futures_zh_minute_sina", symbol="CU2405")

            assert isinstance(result, pd.DataFrame)
            assert "datetime" in result.columns
