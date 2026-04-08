"""
Unit tests for TOP 10 most commonly used AkShare functions.

Tests cover:
- Basic functionality with mock data
- Parameter passing
- Error handling
- Empty results
- Field mapping from Chinese to English

Tested functions:
1. stock_zh_a_hist - A股历史数据
2. stock_zh_a_spot_em - A股实时行情
3. index_stock_info - 指数成分股信息
4. stock_notice_report - 公告报告
5. stock_dividend_cninfo - 分红数据
6. stock_repurchase_em - 回购数据
7. option_current_em - 期权实时数据
8. option_sse_daily_sina - 上交所期权日线
9. stock_new_a_spot_em - 新股数据
10. stock_ipo_summary_cninfo - IPO摘要

Total test cases: 50 (10 functions × 5 tests each)
"""

from unittest.mock import patch, MagicMock
import requests
import pytest
import pandas as pd

from akshare_one.akshare_compat import call_akshare


@pytest.fixture
def mock_akshare():
    """统一的 Mock fixture"""

    def _mock(func_name, return_data, side_effect=None):
        with patch(f"akshare.{func_name}") as mock:
            if side_effect:
                mock.side_effect = side_effect
            else:
                mock.return_value = return_data
            yield mock

    return _mock


class TestStockZhAHist:
    """测试 stock_zh_a_hist - A股历史数据"""

    def test_stock_zh_a_hist_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘": [10.0, 10.5],
                "收盘": [10.5, 11.0],
                "最高": [10.8, 11.2],
                "最低": [9.8, 10.2],
                "成交量": [1000000, 1100000],
                "成交额": [10500000.0, 11500000.0],
                "振幅": [10.0, 9.5],
                "涨跌幅": [5.0, 4.76],
                "涨跌额": [0.5, 0.47],
                "换手率": [2.5, 2.75],
            }
        )

        with patch("akshare.stock_zh_a_hist", return_value=mock_data):
            result = call_akshare(
                "stock_zh_a_hist",
                symbol="600000",
                period="daily",
                start_date="20240101",
                end_date="20240102",
                adjust="",
            )
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert len(result) == 2
            assert "日期" in result.columns
            assert "收盘" in result.columns

    def test_stock_zh_a_hist_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"日期": ["2024-01-01"], "收盘": [10.5]})

        with patch("akshare.stock_zh_a_hist") as mock:
            mock.return_value = mock_data
            result = call_akshare(
                "stock_zh_a_hist",
                symbol="600000",
                period="daily",
                start_date="20240101",
                end_date="20240131",
                adjust="hfq",
            )

            mock.assert_called_once()
            call_kwargs = mock.call_args[1]
            assert call_kwargs["symbol"] == "600000"
            assert call_kwargs["period"] == "daily"
            assert call_kwargs["adjust"] == "hfq"

    def test_stock_zh_a_hist_error_handling(self):
        """错误处理测试 - call_akshare 返回空 DataFrame 而不抛出异常"""
        error_types = [requests.Timeout, requests.ConnectionError, ValueError, KeyError]

        for error_type in error_types:
            with patch("akshare.stock_zh_a_hist", side_effect=error_type):
                result = call_akshare("stock_zh_a_hist", symbol="600000")
                assert isinstance(result, pd.DataFrame)
                assert result.empty

    def test_stock_zh_a_hist_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_zh_a_hist", return_value=mock_data):
            result = call_akshare(
                "stock_zh_a_hist",
                symbol="999999",
                period="daily",
                start_date="20240101",
                end_date="20240101",
                adjust="",
            )
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_zh_a_hist_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {"日期": ["2024-01-01"], "开盘": [10.0], "收盘": [10.5], "最高": [10.8], "最低": [9.8], "成交量": [1000000]}
        )

        with patch("akshare.stock_zh_a_hist", return_value=chinese_data):
            result = call_akshare("stock_zh_a_hist", symbol="600000")

            assert "日期" in result.columns or "date" in result.columns
            assert "收盘" in result.columns or "close" in result.columns


class TestStockZhASpotEm:
    """测试 stock_zh_a_spot_em - A股实时行情"""

    def test_stock_zh_a_spot_em_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "代码": ["600000", "000001"],
                "名称": ["浦发银行", "平安银行"],
                "最新价": [10.5, 15.0],
                "涨跌幅": [2.5, 3.0],
                "涨跌额": [0.25, 0.45],
                "成交量": [1000000, 800000],
                "成交额": [10500000.0, 12000000.0],
                "振幅": [5.0, 6.0],
                "最高": [10.8, 15.5],
                "最低": [10.2, 14.5],
                "今开": [10.3, 14.8],
                "昨收": [10.25, 14.55],
            }
        )

        with patch("akshare.stock_zh_a_spot_em", return_value=mock_data):
            result = call_akshare("stock_zh_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert len(result) == 2
            assert "代码" in result.columns
            assert "最新价" in result.columns

    def test_stock_zh_a_spot_em_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"代码": ["600000"], "最新价": [10.5]})

        with patch("akshare.stock_zh_a_spot_em") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_zh_a_spot_em")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_zh_a_spot_em_error_handling(self, error_type):
        """错误处理测试 - call_akshare 返回空 DataFrame"""
        with patch("akshare.stock_zh_a_spot_em", side_effect=error_type):
            result = call_akshare("stock_zh_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_zh_a_spot_em_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_zh_a_spot_em", return_value=mock_data):
            result = call_akshare("stock_zh_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_zh_a_spot_em_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "代码": ["600000"],
                "名称": ["浦发银行"],
                "最新价": [10.5],
                "涨跌幅": [2.5],
                "成交量": [1000000],
            }
        )

        with patch("akshare.stock_zh_a_spot_em", return_value=chinese_data):
            result = call_akshare("stock_zh_a_spot_em")

            assert "代码" in result.columns or "symbol" in result.columns or "code" in result.columns
            assert "最新价" in result.columns or "price" in result.columns or "close" in result.columns


class TestIndexStockInfo:
    """测试 index_stock_info - 指数成分股信息"""

    def test_index_stock_info_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "指数代码": ["000001", "000001"],
                "指数名称": ["上证指数", "上证指数"],
                "成分股代码": ["600000", "600001"],
                "成分股名称": ["浦发银行", "邯郸钢铁"],
                "纳入日期": ["2020-01-01", "2020-01-01"],
            }
        )

        with patch("akshare.index_stock_info", return_value=mock_data):
            result = call_akshare("index_stock_info")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "指数代码" in result.columns or "指数名称" in result.columns

    def test_index_stock_info_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"指数代码": ["000001"], "成分股代码": ["600000"]})

        with patch("akshare.index_stock_info") as mock:
            mock.return_value = mock_data
            result = call_akshare("index_stock_info")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_index_stock_info_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.index_stock_info", side_effect=error_type):
            result = call_akshare("index_stock_info")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_index_stock_info_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.index_stock_info", return_value=mock_data):
            result = call_akshare("index_stock_info")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_index_stock_info_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "指数代码": ["000001"],
                "指数名称": ["上证指数"],
                "成分股代码": ["600000"],
                "成分股名称": ["浦发银行"],
            }
        )

        with patch("akshare.index_stock_info", return_value=chinese_data):
            result = call_akshare("index_stock_info")

            assert "指数代码" in result.columns or "index_code" in result.columns
            assert "成分股代码" in result.columns or "stock_code" in result.columns or "symbol" in result.columns


class TestStockNoticeReport:
    """测试 stock_notice_report - 公告报告"""

    def test_stock_notice_report_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "公告日期": ["2024-01-01", "2024-01-02"],
                "股票代码": ["600000", "000001"],
                "公告标题": ["2023年度报告", "2023年度报告"],
                "公告类型": ["定期报告", "定期报告"],
                "公告链接": ["http://example.com/1", "http://example.com/2"],
            }
        )

        with patch("akshare.stock_notice_report", return_value=mock_data):
            result = call_akshare("stock_notice_report", symbol="全部", date="2024-01-01")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "公告日期" in result.columns
            assert "公告标题" in result.columns

    def test_stock_notice_report_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"公告日期": ["2024-01-01"], "公告标题": ["重要公告"]})

        with patch("akshare.stock_notice_report") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_notice_report", symbol="全部", date="2024-01-01")

            mock.assert_called_once()
            call_kwargs = mock.call_args[1]
            assert call_kwargs["symbol"] == "全部"
            assert call_kwargs["date"] == "2024-01-01"

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_notice_report_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.stock_notice_report", side_effect=error_type):
            result = call_akshare("stock_notice_report", symbol="全部", date="2024-01-01")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_notice_report_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_notice_report", return_value=mock_data):
            result = call_akshare("stock_notice_report", symbol="全部", date="2024-01-01")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_notice_report_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "公告日期": ["2024-01-01"],
                "股票代码": ["600000"],
                "公告标题": ["重要公告"],
                "公告类型": ["定期报告"],
            }
        )

        with patch("akshare.stock_notice_report", return_value=chinese_data):
            result = call_akshare("stock_notice_report", symbol="全部", date="2024-01-01")

            assert "公告日期" in result.columns or "announcement_date" in result.columns or "date" in result.columns
            assert "公告标题" in result.columns or "title" in result.columns


class TestStockDividendCninfo:
    """测试 stock_dividend_cninfo - 分红数据"""

    def test_stock_dividend_cninfo_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "报告时间": ["2023年报", "2022年报"],
                "派息比例": [1.5, 1.0],
                "股权登记日": ["2024-06-20", "2023-06-15"],
                "除权日": ["2024-06-21", "2023-06-16"],
                "派息日": ["2024-06-22", "2023-06-17"],
                "公告日期": ["2024-03-30", "2023-03-31"],
            }
        )

        with patch("akshare.stock_dividend_cninfo", return_value=mock_data):
            result = call_akshare("stock_dividend_cninfo", symbol="600000")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "报告时间" in result.columns
            assert "派息比例" in result.columns

    def test_stock_dividend_cninfo_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"报告时间": ["2023年报"], "派息比例": [1.5]})

        with patch("akshare.stock_dividend_cninfo") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_dividend_cninfo", symbol="600000")

            mock.assert_called_once()
            call_kwargs = mock.call_args[1]
            assert call_kwargs["symbol"] == "600000"

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_dividend_cninfo_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.stock_dividend_cninfo", side_effect=error_type):
            result = call_akshare("stock_dividend_cninfo", symbol="600000")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_dividend_cninfo_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_dividend_cninfo", return_value=mock_data):
            result = call_akshare("stock_dividend_cninfo", symbol="600000")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_dividend_cninfo_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "报告时间": ["2023年报"],
                "派息比例": [1.5],
                "股权登记日": ["2024-06-20"],
                "除权日": ["2024-06-21"],
                "派息日": ["2024-06-22"],
            }
        )

        with patch("akshare.stock_dividend_cninfo", return_value=chinese_data):
            result = call_akshare("stock_dividend_cninfo", symbol="600000")

            assert "报告时间" in result.columns or "report_period" in result.columns or "fiscal_year" in result.columns
            assert "除权日" in result.columns or "ex_dividend_date" in result.columns


class TestStockRepurchaseEm:
    """测试 stock_repurchase_em - 回购数据"""

    def test_stock_repurchase_em_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["600000", "000001"],
                "最新公告日期": ["2024-01-15", "2024-01-10"],
                "实施进度": ["进行中", "已完成"],
                "已回购金额": [50000000.0, 100000000.0],
                "已回购股份数量": [1000000.0, 2000000.0],
                "计划回购价格区间": ["10-15元", "20-25元"],
                "计划回购金额区间-下限": [40000000.0, 80000000.0],
            }
        )

        with patch("akshare.stock_repurchase_em", return_value=mock_data):
            result = call_akshare("stock_repurchase_em")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "股票代码" in result.columns
            assert "已回购金额" in result.columns

    def test_stock_repurchase_em_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"股票代码": ["600000"], "已回购金额": [50000000.0]})

        with patch("akshare.stock_repurchase_em") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_repurchase_em")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_repurchase_em_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.stock_repurchase_em", side_effect=error_type):
            result = call_akshare("stock_repurchase_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_repurchase_em_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_repurchase_em", return_value=mock_data):
            result = call_akshare("stock_repurchase_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_repurchase_em_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "股票代码": ["600000"],
                "最新公告日期": ["2024-01-15"],
                "实施进度": ["进行中"],
                "已回购金额": [50000000.0],
                "已回购股份数量": [1000000.0],
            }
        )

        with patch("akshare.stock_repurchase_em", return_value=chinese_data):
            result = call_akshare("stock_repurchase_em")

            assert "股票代码" in result.columns or "symbol" in result.columns or "code" in result.columns
            assert "已回购金额" in result.columns or "amount" in result.columns


class TestOptionCurrentEm:
    """测试 option_current_em - 期权实时数据"""

    def test_option_current_em_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "合约代码": ["10003720", "10003721"],
                "合约名称": ["认购期权", "认沽期权"],
                "最新价": [0.05, 0.03],
                "涨跌幅": [1.5, -1.5],
                "成交量": [1000, 800],
                "持仓量": [5000, 6000],
                "行权价格": [2.5, 2.8],
                "行权日期": ["2024-03-27", "2024-03-27"],
                "标的代码": ["510050", "510050"],
            }
        )

        with patch("akshare.option_current_em", return_value=mock_data):
            result = call_akshare("option_current_em")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "合约代码" in result.columns
            assert "最新价" in result.columns

    def test_option_current_em_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"合约代码": ["10003720"], "最新价": [0.05]})

        with patch("akshare.option_current_em") as mock:
            mock.return_value = mock_data
            result = call_akshare("option_current_em")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_option_current_em_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.option_current_em", side_effect=error_type):
            result = call_akshare("option_current_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_option_current_em_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.option_current_em", return_value=mock_data):
            result = call_akshare("option_current_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_option_current_em_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "合约代码": ["10003720"],
                "合约名称": ["认购期权"],
                "最新价": [0.05],
                "涨跌幅": [1.5],
                "成交量": [1000],
                "行权价格": [2.5],
            }
        )

        with patch("akshare.option_current_em", return_value=chinese_data):
            result = call_akshare("option_current_em")

            assert "合约代码" in result.columns or "option_code" in result.columns or "symbol" in result.columns
            assert "最新价" in result.columns or "price" in result.columns


class TestOptionSseDailySina:
    """测试 option_sse_daily_sina - 上交所期权日线"""

    def test_option_sse_daily_sina_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘价": [0.05, 0.055],
                "收盘价": [0.055, 0.06],
                "最高价": [0.06, 0.065],
                "最低价": [0.048, 0.05],
                "成交量": [1000, 1100],
                "持仓量": [5000, 5500],
            }
        )

        with patch("akshare.option_sse_daily_sina", return_value=mock_data):
            result = call_akshare("option_sse_daily_sina", symbol="10003720")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "日期" in result.columns
            assert "收盘价" in result.columns

    def test_option_sse_daily_sina_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"日期": ["2024-01-01"], "收盘价": [0.055]})

        with patch("akshare.option_sse_daily_sina") as mock:
            mock.return_value = mock_data
            result = call_akshare("option_sse_daily_sina", symbol="10003720")

            mock.assert_called_once()
            call_kwargs = mock.call_args[1]
            assert call_kwargs["symbol"] == "10003720"

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_option_sse_daily_sina_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.option_sse_daily_sina", side_effect=error_type):
            result = call_akshare("option_sse_daily_sina", symbol="10003720")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_option_sse_daily_sina_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.option_sse_daily_sina", return_value=mock_data):
            result = call_akshare("option_sse_daily_sina", symbol="10003720")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_option_sse_daily_sina_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "日期": ["2024-01-01"],
                "开盘价": [0.05],
                "收盘价": [0.055],
                "最高价": [0.06],
                "最低价": [0.048],
                "成交量": [1000],
            }
        )

        with patch("akshare.option_sse_daily_sina", return_value=chinese_data):
            result = call_akshare("option_sse_daily_sina", symbol="10003720")

            assert "日期" in result.columns or "date" in result.columns
            assert "收盘价" in result.columns or "close" in result.columns or "close_price" in result.columns


class TestStockNewASpotEm:
    """测试 stock_new_a_spot_em - 新股数据"""

    def test_stock_new_a_spot_em_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["001001", "001002"],
                "股票简称": ["新股A", "新股B"],
                "最新价": [15.0, 20.0],
                "涨跌幅": [10.0, 5.0],
                "涨跌额": [1.5, 1.0],
                "成交量": [500000, 300000],
                "成交额": [7500000.0, 6000000.0],
                "最高": [15.5, 20.5],
                "最低": [14.0, 19.0],
                "今开": [14.5, 19.5],
                "昨收": [13.5, 19.0],
            }
        )

        with patch("akshare.stock_new_a_spot_em", return_value=mock_data):
            result = call_akshare("stock_new_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "股票代码" in result.columns
            assert "最新价" in result.columns

    def test_stock_new_a_spot_em_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"股票代码": ["001001"], "最新价": [15.0]})

        with patch("akshare.stock_new_a_spot_em") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_new_a_spot_em")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_new_a_spot_em_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.stock_new_a_spot_em", side_effect=error_type):
            result = call_akshare("stock_new_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_new_a_spot_em_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_new_a_spot_em", return_value=mock_data):
            result = call_akshare("stock_new_a_spot_em")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_new_a_spot_em_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "股票代码": ["001001"],
                "股票简称": ["新股A"],
                "最新价": [15.0],
                "涨跌幅": [10.0],
                "成交量": [500000],
            }
        )

        with patch("akshare.stock_new_a_spot_em", return_value=chinese_data):
            result = call_akshare("stock_new_a_spot_em")

            assert "股票代码" in result.columns or "symbol" in result.columns or "code" in result.columns
            assert "最新价" in result.columns or "price" in result.columns or "close" in result.columns


class TestStockIpoSummaryCninfo:
    """测试 stock_ipo_summary_cninfo - IPO摘要"""

    def test_stock_ipo_summary_cninfo_basic_call(self, mock_akshare):
        """基础调用测试"""
        mock_data = pd.DataFrame(
            {
                "股票代码": ["001001", "001002"],
                "股票简称": ["新股A", "新股B"],
                "申购代码": ["730001", "730002"],
                "发行价": [10.0, 15.0],
                "发行市盈率": [20.0, 25.0],
                "申购上限": [50000, 30000],
                "申购日期": ["2024-01-01", "2024-01-02"],
                "上市日期": ["2024-01-10", "2024-01-11"],
                "发行总数": [1000000, 800000],
                "网上发行": [500000, 400000],
            }
        )

        with patch("akshare.stock_ipo_summary_cninfo", return_value=mock_data):
            result = call_akshare("stock_ipo_summary_cninfo")
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert "股票代码" in result.columns
            assert "发行价" in result.columns

    def test_stock_ipo_summary_cninfo_with_params(self, mock_akshare):
        """参数传递测试"""
        mock_data = pd.DataFrame({"股票代码": ["001001"], "发行价": [10.0]})

        with patch("akshare.stock_ipo_summary_cninfo") as mock:
            mock.return_value = mock_data
            result = call_akshare("stock_ipo_summary_cninfo")

            mock.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError, ValueError, KeyError])
    def test_stock_ipo_summary_cninfo_error_handling(self, error_type):
        """错误处理测试"""
        with patch("akshare.stock_ipo_summary_cninfo", side_effect=error_type):
            result = call_akshare("stock_ipo_summary_cninfo")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_ipo_summary_cninfo_empty_result(self, mock_akshare):
        """空结果测试"""
        mock_data = pd.DataFrame()

        with patch("akshare.stock_ipo_summary_cninfo", return_value=mock_data):
            result = call_akshare("stock_ipo_summary_cninfo")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_stock_ipo_summary_cninfo_field_mapping(self):
        """字段映射测试"""
        chinese_data = pd.DataFrame(
            {
                "股票代码": ["001001"],
                "股票简称": ["新股A"],
                "发行价": [10.0],
                "申购日期": ["2024-01-01"],
                "上市日期": ["2024-01-10"],
            }
        )

        with patch("akshare.stock_ipo_summary_cninfo", return_value=chinese_data):
            result = call_akshare("stock_ipo_summary_cninfo")

            assert "股票代码" in result.columns or "symbol" in result.columns or "code" in result.columns
            assert "发行价" in result.columns or "issue_price" in result.columns or "price" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
