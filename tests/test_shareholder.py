"""
Unit tests for shareholder module.

Tests cover:
- Shareholder changes (增减持)
- Top shareholders (十大股东/十大流通股东)
- Institution holdings (机构持股)
"""

from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from akshare_one.modules.shareholder import (
    get_shareholder_changes,
    get_top_shareholders,
    get_institution_holdings,
    ShareholderFactory,
)
from akshare_one.modules.shareholder.sse import SSEShareholderProvider
from akshare_one.modules.shareholder.eastmoney import EastmoneyShareholderProvider

TEST_SYMBOL = "600000"
TEST_SYMBOL_INVALID = "999999"


class TestGetShareholderDataBasic:
    """测试基础功能"""

    def test_get_shareholder_data_basic(self):
        """测试基础功能 - 获取股东变动数据"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert not df.empty
            assert "symbol" in df.columns
            assert "holder_name" in df.columns

    def test_get_shareholder_data_invalid_symbol(self):
        """测试无效股票代码"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL_INVALID)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_get_shareholder_data_field_validation(self):
        """测试字段验证"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            required_fields = ["symbol", "name", "holder_name", "position", "change_shares", "reason", "change_date"]
            for field in required_fields:
                assert field in df.columns


class TestGetShareholderTop10:
    """测试前10大股东"""

    def test_get_shareholder_top10(self):
        """测试获取前10大股东数据"""
        with patch("akshare.stock_institute_hold") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "证券代码": [TEST_SYMBOL],
                    "证券简称": ["浦发银行"],
                    "机构数": [10],
                    "机构数变化": [2],
                    "持股比例": [5.5],
                    "持股比例增幅": [0.5],
                }
            )
            mock_ak.return_value = mock_df

            df = get_top_shareholders(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert "symbol" in df.columns
            assert "institution_count" in df.columns


class TestGetShareholderChanges:
    """测试股东变动"""

    def test_get_shareholder_changes(self):
        """测试获取股东变动数据"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL, TEST_SYMBOL],
                    "公司名称": ["浦发银行", "浦发银行"],
                    "姓名": ["张三", "李四"],
                    "职务": ["董事", "监事"],
                    "变动数": [1000, -500],
                    "变动原因": ["增持", "减持"],
                    "变动日期": ["2024-01-15", "2024-01-16"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2

    def test_get_shareholder_changes_with_date_range(self):
        """测试带日期范围的股东变动查询"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL, start_date="2024-01-01", end_date="2024-01-31")

            assert isinstance(df, pd.DataFrame)
            assert not df.empty


class TestShareholderSSEProvider:
    """测试SSE源Provider"""

    def test_sse_provider_initialization(self):
        """测试SSE Provider初始化"""
        provider = SSEShareholderProvider()
        assert provider is not None
        assert provider.get_source_name() == "sse"

    def test_sse_provider_metadata(self):
        """测试SSE Provider元数据"""
        provider = SSEShareholderProvider()

        assert provider.get_data_type() == "shareholder"
        assert provider.get_update_frequency() == "daily"
        assert provider.get_delay_minutes() == 0

    def test_sse_provider_get_shareholder_changes(self):
        """测试SSE Provider获取股东变动"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert "symbol" in df.columns
            assert "holder_name" in df.columns
            assert "change_shares" in df.columns

    def test_sse_provider_top_shareholders_returns_empty(self):
        """测试SSE Provider前10大股东返回空DataFrame"""
        provider = SSEShareholderProvider()
        df = provider.get_top_shareholders(symbol=TEST_SYMBOL)

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_sse_provider_institution_holdings_returns_empty(self):
        """测试SSE Provider机构持股返回空DataFrame"""
        provider = SSEShareholderProvider()
        df = provider.get_institution_holdings(symbol=TEST_SYMBOL)

        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestShareholderEastmoneyProvider:
    """测试Eastmoney源Provider"""

    def test_eastmoney_provider_initialization(self):
        """测试Eastmoney Provider初始化"""
        provider = EastmoneyShareholderProvider()
        assert provider is not None
        assert provider.get_source_name() == "eastmoney"

    def test_eastmoney_provider_metadata(self):
        """测试Eastmoney Provider元数据"""
        provider = EastmoneyShareholderProvider()

        assert provider.get_data_type() == "shareholder"
        assert provider.get_update_frequency() == "daily"

    def test_eastmoney_provider_get_shareholder_changes(self):
        """测试Eastmoney Provider获取股东变动"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = EastmoneyShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert "symbol" in df.columns

    def test_eastmoney_provider_get_top_shareholders(self):
        """测试Eastmoney Provider获取前10大股东"""
        with patch("akshare.stock_institute_hold") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "证券代码": [TEST_SYMBOL],
                    "证券简称": ["浦发银行"],
                    "机构数": [15],
                    "机构数变化": [3],
                    "持股比例": [8.5],
                    "持股比例增幅": [1.2],
                }
            )
            mock_ak.return_value = mock_df

            provider = EastmoneyShareholderProvider()
            df = provider.get_top_shareholders(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert "symbol" in df.columns
            assert "institution_count" in df.columns

    def test_eastmoney_provider_get_institution_holdings(self):
        """测试Eastmoney Provider获取机构持股"""
        with patch("akshare.stock_institute_hold") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "证券代码": [TEST_SYMBOL],
                    "证券简称": ["浦发银行"],
                    "机构数": [20],
                    "持股比例": [12.5],
                    "占流通股比例": [15.3],
                }
            )
            mock_ak.return_value = mock_df

            provider = EastmoneyShareholderProvider()
            df = provider.get_institution_holdings(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert "symbol" in df.columns
            assert "institution_count" in df.columns


class TestShareholderDataJsonCompatibility:
    """测试JSON序列化兼容性"""

    def test_shareholder_data_json_compatibility(self):
        """测试数据JSON序列化兼容性"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            json_str = df.to_json(orient="records")
            assert json_str is not None

            import json

            parsed = json.loads(json_str)
            assert isinstance(parsed, list)

    def test_no_nan_in_numeric_columns(self):
        """测试数值列无NaN值"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            for col in df.select_dtypes(include=["float64", "float32"]).columns:
                assert not df[col].isna().any() or df[col].isna().all()

    def test_no_infinity_values(self):
        """测试无无穷大值"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            import numpy as np

            for col in df.select_dtypes(include=["float64", "float32"]).columns:
                assert not np.isinf(df[col]).any()


class TestErrorHandling:
    """测试错误处理"""

    def test_api_timeout_handling(self):
        """测试API超时处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            import requests

            mock_ak.side_effect = requests.Timeout("Connection timeout")

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_api_connection_error_handling(self):
        """测试API连接错误处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            import requests

            mock_ak.side_effect = requests.ConnectionError("Connection refused")

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_api_exception_handling(self):
        """测试API异常处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_ak.side_effect = Exception("Unexpected error")

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty


class TestEmptyResults:
    """测试空结果处理"""

    def test_empty_dataframe_handling(self):
        """测试空DataFrame处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_ak.return_value = pd.DataFrame()

            df = get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_no_data_for_symbol(self):
        """测试无数据的股票代码"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL_INVALID)

            assert isinstance(df, pd.DataFrame)
            assert df.empty


class TestFactory:
    """测试工厂类"""

    def test_factory_creates_eastmoney_provider(self):
        """测试工厂创建Eastmoney Provider"""
        provider = ShareholderFactory.get_provider(source="eastmoney")
        assert provider is not None
        assert isinstance(provider, EastmoneyShareholderProvider)

    def test_factory_invalid_source(self):
        """测试工厂无效数据源"""
        with pytest.raises((ValueError, KeyError)):
            ShareholderFactory.get_provider(source="invalid_source")


class TestPublicAPI:
    """测试公开API"""

    def test_get_shareholder_changes_api(self):
        """测试股东变动API"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            assert callable(get_shareholder_changes)

            df = get_shareholder_changes(symbol=TEST_SYMBOL)
            assert isinstance(df, pd.DataFrame)

    def test_get_top_shareholders_api(self):
        """测试前10大股东API"""
        with patch("akshare.stock_institute_hold") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "证券代码": [TEST_SYMBOL],
                    "证券简称": ["浦发银行"],
                    "机构数": [10],
                    "持股比例": [5.5],
                }
            )
            mock_ak.return_value = mock_df

            assert callable(get_top_shareholders)

            df = get_top_shareholders(symbol=TEST_SYMBOL)
            assert isinstance(df, pd.DataFrame)

    def test_get_institution_holdings_api(self):
        """测试机构持股API"""
        with patch("akshare.stock_institute_hold") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "证券代码": [TEST_SYMBOL],
                    "证券简称": ["浦发银行"],
                    "机构数": [15],
                    "持股比例": [8.5],
                }
            )
            mock_ak.return_value = mock_df

            assert callable(get_institution_holdings)

            df = get_institution_holdings(symbol=TEST_SYMBOL)
            assert isinstance(df, pd.DataFrame)

    def test_api_default_source(self):
        """测试API默认数据源"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL)
            assert isinstance(df, pd.DataFrame)


class TestDateFiltering:
    """测试日期过滤"""

    def test_date_range_filtering(self):
        """测试日期范围过滤"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL, TEST_SYMBOL, TEST_SYMBOL],
                    "公司名称": ["浦发银行", "浦发银行", "浦发银行"],
                    "姓名": ["张三", "李四", "王五"],
                    "职务": ["董事", "监事", "高管"],
                    "变动数": [1000, 2000, 3000],
                    "变动原因": ["增持", "增持", "增持"],
                    "变动日期": ["2024-01-10", "2024-01-20", "2024-02-01"],
                }
            )
            mock_ak.return_value = mock_df

            df = get_shareholder_changes(symbol=TEST_SYMBOL, start_date="2024-01-15", end_date="2024-01-25")

            assert isinstance(df, pd.DataFrame)
            if not df.empty:
                assert len(df) == 1
                assert df.iloc[0]["holder_name"] == "李四"


class TestSSEProviderComprehensive:
    """SSE Provider全面测试"""

    def test_sse_provider_source_name(self):
        """测试SSE Provider源名称"""
        provider = SSEShareholderProvider()
        assert provider.get_source_name() == "sse"

    def test_sse_provider_data_type(self):
        """测试SSE Provider数据类型"""
        provider = SSEShareholderProvider()
        assert provider.get_data_type() == "shareholder"

    def test_sse_provider_fetch_data(self):
        """测试SSE Provider fetch_data方法"""
        provider = SSEShareholderProvider()
        df = provider.fetch_data()
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_sse_provider_get_shareholder_changes_basic(self):
        """测试SSE Provider获取股东变动基础功能"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert not df.empty
            mock_ak.assert_called_once()

    def test_sse_provider_get_shareholder_changes_with_date_range(self):
        """测试SSE Provider带日期范围获取股东变动"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL, start_date="2024-01-01", end_date="2024-01-31")

            assert isinstance(df, pd.DataFrame)
            assert not df.empty

    def test_sse_provider_get_shareholder_changes_invalid_symbol(self):
        """测试SSE Provider无效股票代码"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL_INVALID)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_get_shareholder_changes_empty_dataframe(self):
        """测试SSE Provider空DataFrame返回"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_ak.return_value = pd.DataFrame()

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_get_shareholder_changes_exception(self):
        """测试SSE Provider异常处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_ak.side_effect = Exception("API Error")

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_get_top_shareholders_basic(self):
        """测试SSE Provider获取前10大股东"""
        provider = SSEShareholderProvider()
        df = provider.get_top_shareholders(symbol=TEST_SYMBOL)

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert "rank" in df.columns
        assert "holder_name" in df.columns

    def test_sse_provider_get_institution_holdings_basic(self):
        """测试SSE Provider获取机构持股"""
        provider = SSEShareholderProvider()
        df = provider.get_institution_holdings(symbol=TEST_SYMBOL)

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert "institution_count" in df.columns

    def test_sse_provider_shareholder_changes_field_validation(self):
        """测试SSE Provider股东变动字段验证"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                    "变动后持股数": [5000],
                    "本次变动前持股数": [4000],
                    "本次变动平均价格": [10.5],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            expected_fields = [
                "symbol",
                "name",
                "holder_name",
                "position",
                "change_shares",
                "reason",
                "change_date",
                "shares_before",
                "shares_after",
                "avg_price",
            ]
            for field in expected_fields:
                assert field in df.columns

    def test_sse_provider_json_compatibility(self):
        """测试SSE Provider JSON兼容性"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            import json

            json_str = df.to_json(orient="records")
            assert json_str is not None
            parsed = json.loads(json_str)
            assert isinstance(parsed, list)

    def test_sse_provider_dataframe_columns(self):
        """测试SSE Provider DataFrame列"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df.columns, pd.Index)

    def test_sse_provider_data_types(self):
        """测试SSE Provider数据类型"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert pd.api.types.is_datetime64_any_dtype(df["change_date"])
            assert pd.api.types.is_string_dtype(df["symbol"])

    def test_sse_provider_uses_correct_akshare_function(self):
        """验证SSE Provider使用正确的akshare函数"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            mock_ak.assert_called_once()

    def test_sse_provider_invalid_date_range(self):
        """测试SSE Provider无效日期范围"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-06-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL, start_date="2024-01-01", end_date="2024-01-31")

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_multiple_records(self):
        """测试SSE Provider多条记录"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL, TEST_SYMBOL],
                    "公司名称": ["浦发银行", "浦发银行"],
                    "姓名": ["张三", "李四"],
                    "职务": ["董事", "监事"],
                    "变动数": [1000, -500],
                    "变动原因": ["增持", "减持"],
                    "变动日期": ["2024-01-15", "2024-01-16"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2

    def test_sse_provider_top_shareholders_columns(self):
        """测试SSE Provider前10大股东列结构"""
        provider = SSEShareholderProvider()
        df = provider.get_top_shareholders(symbol=TEST_SYMBOL)

        expected_columns = ["rank", "holder_name", "shares", "pct", "change"]
        for col in expected_columns:
            assert col in df.columns

    def test_sse_provider_institution_holdings_columns(self):
        """测试SSE Provider机构持股列结构"""
        provider = SSEShareholderProvider()
        df = provider.get_institution_holdings(symbol=TEST_SYMBOL)

        expected_columns = ["institution_count", "holding_pct", "change_pct"]
        for col in expected_columns:
            assert col in df.columns

    def test_sse_provider_get_shareholder_changes_without_symbol(self):
        """测试SSE Provider不带股票代码获取股东变动"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": ["600000", "600001"],
                    "公司名称": ["浦发银行", "另一银行"],
                    "姓名": ["张三", "李四"],
                    "职务": ["董事", "监事"],
                    "变动数": [1000, 2000],
                    "变动原因": ["增持", "增持"],
                    "变动日期": ["2024-01-15", "2024-01-16"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes()

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2

    def test_sse_provider_negative_change_shares(self):
        """测试SSE Provider减持数据"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [-500],
                    "变动原因": ["减持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.iloc[0]["change_shares"] == -500

    def test_sse_provider_api_timeout_handling(self):
        """测试SSE Provider API超时处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            import requests

            mock_ak.side_effect = requests.Timeout("Connection timeout")

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_api_connection_error(self):
        """测试SSE Provider API连接错误处理"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            import requests

            mock_ak.side_effect = requests.ConnectionError("Connection refused")

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert df.empty

    def test_sse_provider_default_date_range(self):
        """测试SSE Provider默认日期范围"""
        with patch("akshare.stock_share_hold_change_sse") as mock_ak:
            mock_df = pd.DataFrame(
                {
                    "公司代码": [TEST_SYMBOL],
                    "公司名称": ["浦发银行"],
                    "姓名": ["张三"],
                    "职务": ["董事"],
                    "变动数": [1000],
                    "变动原因": ["增持"],
                    "变动日期": ["2024-01-15"],
                }
            )
            mock_ak.return_value = mock_df

            provider = SSEShareholderProvider()
            df = provider.get_shareholder_changes(symbol=TEST_SYMBOL)

            assert isinstance(df, pd.DataFrame)
            assert not df.empty


class TestSSEProviderMockData:
    """SSE Provider Mock数据测试"""

    @pytest.fixture
    def mock_sse_shareholder_data(self):
        """Mock SSE股东数据"""
        with patch("akshare.stock_share_hold_change_sse") as mock:
            mock.return_value = pd.DataFrame(
                {
                    "公司代码": ["600000", "600001"],
                    "公司名称": ["浦发银行", "民生银行"],
                    "姓名": ["张三", "李四"],
                    "职务": ["董事", "监事"],
                    "变动数": [1000, -500],
                    "变动原因": ["增持", "减持"],
                    "变动日期": ["2024-01-15", "2024-01-16"],
                    "变动后持股数": [5000, 3000],
                    "本次变动前持股数": [4000, 3500],
                    "本次变动平均价格": [10.5, 11.2],
                }
            )
            yield mock

    def test_mock_data_structure(self, mock_sse_shareholder_data):
        """测试Mock数据结构"""
        provider = SSEShareholderProvider()
        df = provider.get_shareholder_changes()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "symbol" in df.columns
        assert "holder_name" in df.columns

    def test_mock_data_field_mapping(self, mock_sse_shareholder_data):
        """测试Mock数据字段映射"""
        provider = SSEShareholderProvider()
        df = provider.get_shareholder_changes()

        assert df.iloc[0]["symbol"] == "600000"
        assert df.iloc[0]["holder_name"] == "张三"
        assert df.iloc[0]["change_shares"] == 1000

    def test_mock_data_symbol_filtering(self, mock_sse_shareholder_data):
        """测试Mock数据股票代码过滤"""
        provider = SSEShareholderProvider()
        df = provider.get_shareholder_changes(symbol="600000")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "600000"

    def test_mock_data_date_filtering(self, mock_sse_shareholder_data):
        """测试Mock数据日期过滤"""
        provider = SSEShareholderProvider()
        df = provider.get_shareholder_changes(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_mock_data_complete_fields(self, mock_sse_shareholder_data):
        """测试Mock数据完整字段"""
        provider = SSEShareholderProvider()
        df = provider.get_shareholder_changes(symbol="600000")

        expected_fields = [
            "symbol",
            "name",
            "holder_name",
            "position",
            "change_shares",
            "reason",
            "change_date",
            "shares_before",
            "shares_after",
            "avg_price",
        ]
        for field in expected_fields:
            assert field in df.columns
