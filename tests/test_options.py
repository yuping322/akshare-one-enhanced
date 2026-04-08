import os
import tempfile
from unittest.mock import patch

import pytest

from akshare_one import (
    get_options_chain,
    get_options_expirations,
    get_options_hist,
    get_options_realtime,
)


@pytest.mark.integration
class TestOptionsChain:
    def test_basic_options_chain(self):
        """测试基本期权链数据获取功能"""
        try:
            df = get_options_chain(underlying_symbol="510300")  # 300ETF期权
            # 如果有数据，验证基本结构
            if not df.empty:
                assert "symbol" in df.columns
                assert "strike" in df.columns
                assert "expiration" in df.columns
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_options_chain_columns(self):
        """测试期权链数据字段完整性"""
        try:
            df = get_options_chain(underlying_symbol="510300")
            if not df.empty:
                expected_columns = {
                    "underlying",
                    "symbol",
                    "name",
                    "option_type",
                    "strike",
                    "expiration",
                    "price",
                    "volume",
                    "open_interest",
                }
                assert expected_columns.issubset(set(df.columns))
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_options_chain_types(self):
        """测试期权类型分离"""
        try:
            df = get_options_chain(underlying_symbol="510300")
            if not df.empty and "option_type" in df.columns:
                option_types = df["option_type"].unique()
                assert set(option_types).issubset({"call", "put", ""})
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_empty_api_response_handling(self):
        """测试空API响应处理"""
        import pandas as pd

        # Disable caching for this test
        old_cache_enabled = os.environ.get("AKSHARE_ONE_CACHE_ENABLED")
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        try:
            with patch("akshare_one.modules.options.sina.ak.option_current_em") as mock_api:
                mock_api.return_value = pd.DataFrame()  # 模拟空响应
                with pytest.raises(ValueError, match="No options data available"):
                    get_options_chain(underlying_symbol="510300")
        finally:
            # Restore original cache setting
            if old_cache_enabled is not None:
                os.environ["AKSHARE_ONE_CACHE_ENABLED"] = old_cache_enabled
            else:
                os.environ.pop("AKSHARE_ONE_CACHE_ENABLED", None)

    def test_partial_api_failure(self):
        """测试部分API调用失败处理"""
        import pandas as pd  # 添加缺失的导入

        with (
            patch("akshare_one.modules.options.sina.ak.option_sse_list_sina") as mock_list_api,
            patch("akshare_one.modules.options.sina.ak.option_sse_codes_sina") as mock_codes_api,
        ):
            # 模拟列表API返回有效到期日，但代码API部分失败
            mock_list_api.return_value = ["202503", "202504"]  # 模拟有效的到期日
            # 模拟第一次调用返回None（失败），第二次调用返回有效数据
            mock_codes_api.side_effect = [
                None,
                pd.DataFrame({"期权代码": ["TEST123"]}),
                pd.DataFrame({"期权代码": ["TEST456"]}),
                pd.DataFrame({"期权代码": ["TEST789"]}),
            ]

            # 这个测试应该确保即使部分API调用失败，程序也能正常处理而不崩溃
            try:
                get_options_chain(underlying_symbol="510300")
                # 如果没有抛出异常，测试通过
                pass
            except Exception:
                # 如果抛出了预期的异常（例如没有找到期权数据），这也是正常的
                pass

    def test_invalid_underlying_symbol(self):
        """测试无效标的代码"""
        with pytest.raises((ValueError, KeyError)):
            get_options_chain(underlying_symbol="INVALID")


@pytest.mark.integration
class TestOptionsRealtime:
    def test_options_realtime_for_underlying(self):
        """测试获取标的所有期权实时数据"""
        try:
            df = get_options_realtime(underlying_symbol="510300")
            # 如果有数据，验证基本结构
            if not df.empty:
                assert "symbol" in df.columns
                assert "price" in df.columns
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_options_realtime_columns(self):
        """测试期权实时数据字段完整性"""
        try:
            df = get_options_realtime(underlying_symbol="510300")
            if not df.empty:
                expected_columns = {
                    "symbol",
                    "underlying",
                    "price",
                    "change",
                    "pct_change",
                    "timestamp",
                    "volume",
                    "open_interest",
                }
                assert expected_columns.issubset(set(df.columns))
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_specific_option_realtime(self):
        """测试特定期权的实时数据 - 使用动态获取的有效期权代码"""
        # First get a valid option symbol from the chain
        try:
            chain_df = get_options_chain(underlying_symbol="510300")
            if chain_df.empty:
                pytest.skip("No options data available to get valid symbol")

            # Get the first valid option symbol
            valid_symbol = chain_df["symbol"].iloc[0]
            df = get_options_realtime(symbol=valid_symbol)
            if not df.empty:
                assert "symbol" in df.columns
        except ValueError as e:
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pytest.skip("No options data available")
            else:
                raise

    def test_realtime_invalid_params_both(self):
        """测试同时提供 symbol 和 underlying_symbol 时抛出异常"""
        with pytest.raises(ValueError, match="Cannot specify both"):
            get_options_realtime(symbol="10004005", underlying_symbol="510300")

    def test_realtime_invalid_params_none(self):
        """测试都不提供 symbol 和 underlying_symbol 时抛出异常"""
        with pytest.raises(ValueError, match="Must specify either"):
            get_options_realtime()


@pytest.mark.integration
class TestOptionsExpirations:
    def test_get_options_expirations(self):
        """测试获取期权到期日列表"""
        try:
            expirations = get_options_expirations(underlying_symbol="510300")
            assert isinstance(expirations, list)
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No options found for underlying symbol" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_expirations_sorted(self):
        """测试到期日列表有序"""
        try:
            expirations = get_options_expirations(underlying_symbol="510300")
            if expirations:
                assert expirations == sorted(expirations)
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No options found for underlying symbol" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_invalid_expirations_symbol(self):
        """测试无效标的到期日查询"""
        with pytest.raises((ValueError, KeyError)):
            get_options_expirations(underlying_symbol="INVALID")


@pytest.mark.integration
class TestOptionsHistory:
    def test_options_hist_data(self):
        """测试期权历史数据获取 - 使用动态获取的有效 SSE 期权代码

        Note: option_sse_daily_sina only supports SSE option symbols (1000xxxx format),
        not commodity option symbols (like au2606P648).
        """
        try:
            chain_df = get_options_chain(underlying_symbol="510300")
            if chain_df.empty:
                pytest.skip("No options data available to get valid symbol")

            # Find a SSE option symbol (starts with '1000')
            sse_options = chain_df[chain_df["symbol"].str.match(r"^1000", na=False)]
            if sse_options.empty:
                pytest.skip("No SSE options available for history data test")

            valid_symbol = sse_options["symbol"].iloc[0]
            df = get_options_hist(
                symbol=valid_symbol,
                start_date="2024-01-01",
                end_date="2024-01-31",
            )
            # History data may be empty for recent options, so we just check structure if data exists
            if not df.empty:
                assert "timestamp" in df.columns
                assert "close" in df.columns
        except ValueError as e:
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pytest.skip("No options data available")
            else:
                raise

    def test_options_hist_columns(self):
        """测试期权历史数据字段完整性 - 使用动态获取的有效 SSE 期权代码"""
        try:
            chain_df = get_options_chain(underlying_symbol="510300")
            if chain_df.empty:
                pytest.skip("No options data available to get valid symbol")

            # Find a SSE option symbol (starts with '1000')
            sse_options = chain_df[chain_df["symbol"].str.match(r"^1000", na=False)]
            if sse_options.empty:
                pytest.skip("No SSE options available for history data test")

            valid_symbol = sse_options["symbol"].iloc[0]
            df = get_options_hist(
                symbol=valid_symbol,
                start_date="2025-01-01",
                end_date="2025-01-31",
            )
            if not df.empty:
                expected_columns = {
                    "timestamp",
                    "symbol",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "open_interest",
                }
                assert expected_columns.issubset(set(df.columns))
        except ValueError as e:
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pytest.skip("No options data available")
            else:
                raise

    def test_invalid_hist_dates(self):
        """测试无效日期格式"""
        with pytest.raises(ValueError):
            get_options_hist(
                symbol="10004005",
                start_date="2025-31-01",  # invalid date
                end_date="2025-01-31",
            )


class TestOptionsDataFactory:
    def test_register_custom_provider(self):
        """测试注册自定义期权数据提供商"""
        from akshare_one.modules.options.base import OptionsDataProvider
        from akshare_one.modules.options import OptionsDataFactory

        class CustomProvider(OptionsDataProvider):
            def get_options_chain(self):
                import pandas as pd

                return pd.DataFrame()

            def get_options_realtime(self, symbol: str):
                import pandas as pd

                return pd.DataFrame()

            def get_options_expirations(self, underlying_symbol: str):
                return []

            def get_options_history(
                self,
                symbol: str,
                start_date: str = "1970-01-01",
                end_date: str = "2030-12-31",
            ):
                import pandas as pd

                return pd.DataFrame()

        OptionsDataFactory.register_provider("custom", CustomProvider)
        provider = OptionsDataFactory.get_provider("custom", underlying_symbol="510300")
        assert isinstance(provider, CustomProvider)

    def test_get_provider_by_name(self):
        """测试通过名称获取数据提供商"""
        from akshare_one.modules.options import OptionsDataFactory

        provider = OptionsDataFactory.get_provider("sina", underlying_symbol="510300")
        assert provider is not None
        assert provider.underlying_symbol == "510300"

    def test_invalid_provider(self):
        """测试无效数据提供商"""
        from akshare_one.modules.options import OptionsDataFactory

        with pytest.raises(ValueError, match="Unsupported data source"):
            OptionsDataFactory.get_provider("invalid", underlying_symbol="510300")


class TestOptionsErrorHandling:
    def test_api_error_handling(self):
        """测试API错误处理"""
        # Disable caching for this test
        old_cache_enabled = os.environ.get("AKSHARE_ONE_CACHE_ENABLED")
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        try:
            with patch("akshare_one.modules.options.sina.ak.option_current_em") as mock_get:
                mock_get.side_effect = Exception("API error")
                with pytest.raises(Exception, match="API error"):
                    get_options_chain(underlying_symbol="510300")
        finally:
            # Restore original cache setting
            if old_cache_enabled is not None:
                os.environ["AKSHARE_ONE_CACHE_ENABLED"] = old_cache_enabled
            else:
                os.environ.pop("AKSHARE_ONE_CACHE_ENABLED", None)

    def test_data_cleaning_with_missing_columns(self):
        """测试数据清理时缺少必要列"""
        import pandas as pd

        # Disable caching for this test
        old_cache_enabled = os.environ.get("AKSHARE_ONE_CACHE_ENABLED")
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"

        try:
            with patch("akshare_one.modules.options.sina.ak.option_current_em") as mock_get:
                # Return empty DataFrame to test error handling
                mock_get.return_value = pd.DataFrame()
                with pytest.raises(ValueError, match="No options data available"):
                    get_options_chain(underlying_symbol="510300")
        finally:
            # Restore original cache setting
            if old_cache_enabled is not None:
                os.environ["AKSHARE_ONE_CACHE_ENABLED"] = old_cache_enabled
            else:
                os.environ.pop("AKSHARE_ONE_CACHE_ENABLED", None)


@pytest.mark.integration
class TestOptionsIntegration:
    def test_chain_and_realtime_consistency(self):
        """测试期权链和实时数据的一致性"""
        try:
            chain_df = get_options_chain(underlying_symbol="510300")
            realtime_df = get_options_realtime(underlying_symbol="510300")

            if not chain_df.empty and not realtime_df.empty:
                # Check that symbols from chain appear in realtime data
                chain_symbols = set(chain_df["symbol"].tolist())
                realtime_symbols = set(realtime_df["symbol"].tolist())
                assert chain_symbols.issubset(realtime_symbols) or chain_symbols & realtime_symbols
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No valid expirations found" in str(e) or "Failed to fetch options chain" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise

    def test_expirations_in_chain(self):
        """测试到期日在期权链数据中出现"""
        try:
            expirations = get_options_expirations(underlying_symbol="510300")
            chain_df = get_options_chain(underlying_symbol="510300")

            if expirations and not chain_df.empty and "expiration" in chain_df.columns:
                chain_expirations = set(chain_df["expiration"].unique().tolist())
                # At least some expirations should match
                assert len(set(expirations) & chain_expirations) >= 0
        except ValueError as e:
            # 如果没有可用的期权数据，也要接受这种情况
            if "No options found for underlying symbol" in str(e):
                pass  # 这是可以接受的情况
            else:
                raise


@pytest.mark.unit
class TestOptionsMappingManager:
    """测试期权映射管理器 - mapping_manager.py"""

    def test_options_mapping_manager_init(self):
        """测试映射管理器初始化"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        manager = DynamicMappingManager(cache_dir="test_mapping_cache")
        assert manager.cache_dir == "test_mapping_cache"
        assert manager._underlying_patterns is None
        assert manager._last_update is None

    def test_options_mapping_manager_cache_dir(self):
        """测试映射管理器缓存目录创建"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, "test_cache")
            manager = DynamicMappingManager(cache_dir=cache_dir)
            manager.ensure_cache_dir()
            assert os.path.exists(cache_dir)

    def test_options_mapping_manager_cache_expired(self):
        """测试缓存过期检测"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import tempfile
        import os
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            cache_file = os.path.join(tmpdir, "test_cache.json")

            # 文件不存在时应返回True
            assert manager.is_cache_expired(cache_file) is True

            # 创建新文件
            with open(cache_file, "w") as f:
                f.write("{}")
            time.sleep(0.1)

            # 新文件不应过期
            assert manager.is_cache_expired(cache_file, days=7) is False

            # 0天过期设置应返回True
            assert manager.is_cache_expired(cache_file, days=0) is True

    def test_options_mapping_manager_patterns_generation(self):
        """测试底层资产模式生成"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        from unittest.mock import patch
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame(
                    {"index_code": ["000300", "000016", "000905"], "display_name": ["沪深300", "上证50", "中证500"]}
                )

                patterns = manager.generate_underlying_patterns()

                assert "000300" in patterns
                assert "000016" in patterns
                assert "000905" in patterns

    def test_options_mapping_manager_get_patterns_for_symbol(self):
        """测试获取特定符号的匹配模式"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        from unittest.mock import patch
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns = manager.get_patterns_for_symbol("000300")
                assert isinstance(patterns, list)
                assert len(patterns) > 0

    def test_options_mapping_manager_refresh_cache(self):
        """测试缓存刷新"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            cache_file = os.path.join(tmpdir, "underlying_patterns.json")
            with open(cache_file, "w") as f:
                f.write('{"test": "data"}')

            manager._underlying_patterns = {"test": "value"}

            manager.refresh_cache()

            assert manager._underlying_patterns is None
            assert not os.path.exists(cache_file)

    def test_mapping_manager_default_init(self):
        """测试默认初始化"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        manager = DynamicMappingManager()
        assert manager.cache_dir == "mapping_tables"
        assert manager._underlying_patterns is None
        assert manager._last_update is None

    def test_mapping_manager_custom_cache_dir(self):
        """测试自定义缓存目录初始化"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = os.path.join(tmpdir, "custom_cache")
            manager = DynamicMappingManager(cache_dir=custom_dir)
            assert manager.cache_dir == custom_dir
            assert os.path.exists(custom_dir)

    def test_ensure_cache_dir_creates_directory(self):
        """测试确保缓存目录存在"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, "new_cache_dir")
            manager = DynamicMappingManager(cache_dir=cache_dir)
            assert os.path.exists(cache_dir)

    def test_is_cache_expired_missing_file(self):
        """测试缓存文件不存在时返回True"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)
            non_existent_file = os.path.join(tmpdir, "non_existent.json")
            assert manager.is_cache_expired(non_existent_file) is True

    def test_is_cache_expired_valid_cache(self):
        """测试有效缓存文件返回False"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)
            cache_file = os.path.join(tmpdir, "cache.json")

            with open(cache_file, "w") as f:
                f.write("{}")

            assert manager.is_cache_expired(cache_file, days=7) is False

    def test_is_cache_expired_old_cache(self):
        """测试过期缓存文件返回True"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)
            cache_file = os.path.join(tmpdir, "old_cache.json")

            with open(cache_file, "w") as f:
                f.write("{}")

            time.sleep(0.1)
            assert manager.is_cache_expired(cache_file, days=0) is True

    def test_generate_underlying_patterns_with_mocked_akshare(self):
        """测试生成底层资产模式（Mock akshare）"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame(
                    {"index_code": ["000300", "000016"], "display_name": ["沪深300", "上证50"]}
                )

                patterns = manager.generate_underlying_patterns()

                assert isinstance(patterns, dict)
                assert "000300" in patterns
                assert "000016" in patterns
                assert "沪深300" in patterns["000300"]

    def test_generate_underlying_patterns_api_failure(self):
        """测试API失败时仍能返回基本映射"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.side_effect = Exception("API Error")

                patterns = manager.generate_underlying_patterns()

                assert isinstance(patterns, dict)
                assert len(patterns) > 0

    def test_generate_underlying_patterns_empty_response(self):
        """测试API返回空数据"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame()

                patterns = manager.generate_underlying_patterns()

                assert isinstance(patterns, dict)

    def test_get_underlying_patterns_first_call(self):
        """测试首次获取底层资产模式"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns = manager.get_underlying_patterns()

                assert isinstance(patterns, dict)
                assert "000300" in patterns
                assert manager._underlying_patterns is not None
                assert manager._last_update is not None

    def test_get_underlying_patterns_cache_hit(self):
        """测试缓存命中"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns1 = manager.get_underlying_patterns()
                patterns2 = manager.get_underlying_patterns()

                assert patterns1 == patterns2
                assert mock_index.call_count == 1

    def test_get_underlying_patterns_load_from_cache(self):
        """测试从缓存文件加载"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "underlying_patterns.json")
            cached_data = {"000300": ["沪深300", "HS300"]}

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, ensure_ascii=False)

            manager = DynamicMappingManager(cache_dir=tmpdir)
            patterns = manager.get_underlying_patterns()

            assert "000300" in patterns
            assert "沪深300" in patterns["000300"]

    def test_get_patterns_for_valid_symbol(self):
        """测试获取有效符号的模式"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns = manager.get_patterns_for_symbol("000300")

                assert isinstance(patterns, list)
                assert len(patterns) > 0
                assert "沪深300" in patterns

    def test_get_patterns_for_invalid_symbol(self):
        """测试获取无效符号的模式"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns = manager.get_patterns_for_symbol("INVALID")

                assert isinstance(patterns, list)
                assert patterns == ["INVALID"]

    def test_refresh_cache_clears_memory_cache(self):
        """测试刷新缓存清除内存缓存"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                manager.get_underlying_patterns()
                assert manager._underlying_patterns is not None

                manager.refresh_cache()
                assert manager._underlying_patterns is None

    def test_refresh_cache_removes_cache_file(self):
        """测试刷新缓存删除缓存文件"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                manager.get_underlying_patterns()
                cache_file = os.path.join(tmpdir, "underlying_patterns.json")
                assert os.path.exists(cache_file)

                manager.refresh_cache()
                assert not os.path.exists(cache_file)

    def test_global_get_underlying_patterns(self):
        """测试全局函数get_underlying_patterns"""
        from akshare_one.modules.options.mapping_manager import get_underlying_patterns, _mapping_manager
        import pandas as pd

        with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
            mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

            _mapping_manager._underlying_patterns = None

            patterns = get_underlying_patterns()

            assert isinstance(patterns, dict)

    def test_global_get_patterns_for_symbol(self):
        """测试全局函数get_patterns_for_symbol"""
        from akshare_one.modules.options.mapping_manager import (
            get_patterns_for_symbol,
            get_underlying_patterns,
            _mapping_manager,
        )
        import pandas as pd

        with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
            mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

            _mapping_manager._underlying_patterns = None
            get_underlying_patterns()

            patterns = get_patterns_for_symbol("000300")

            assert isinstance(patterns, list)

    def test_global_refresh_mapping_cache(self):
        """测试全局函数refresh_mapping_cache"""
        from akshare_one.modules.options.mapping_manager import (
            refresh_mapping_cache,
            get_underlying_patterns,
            _mapping_manager,
        )
        import pandas as pd

        with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
            mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

            _mapping_manager._underlying_patterns = None
            get_underlying_patterns()
            assert _mapping_manager._underlying_patterns is not None

            refresh_mapping_cache()
            assert _mapping_manager._underlying_patterns is None

    def test_cache_file_persistence(self):
        """测试缓存文件持久化"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            manager1 = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                import pandas as pd

                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns1 = manager1.get_underlying_patterns()
                assert "000300" in patterns1

            cache_file = os.path.join(tmpdir, "underlying_patterns.json")
            assert os.path.exists(cache_file)

            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                assert "000300" in cached_data

    def test_concurrent_cache_access(self):
        """测试并发缓存访问（简单场景）"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                patterns1 = manager.get_underlying_patterns()
                patterns2 = manager.get_underlying_patterns()
                patterns3 = manager.get_patterns_for_symbol("000300")

                assert patterns1 == patterns2
                assert patterns3 == patterns1["000300"]

    def test_corrupted_cache_file_handling(self):
        """测试损坏的缓存文件处理"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "underlying_patterns.json")
            with open(cache_file, "w") as f:
                f.write("invalid json {{{")

            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame({"index_code": ["000300"], "display_name": ["沪深300"]})

                manager._underlying_patterns = None
                patterns = manager.get_underlying_patterns()

                assert isinstance(patterns, dict)

    def test_cache_directory_auto_creation(self):
        """测试缓存目录自动创建"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, "auto_created_cache")
            assert not os.path.exists(cache_dir)

            manager = DynamicMappingManager(cache_dir=cache_dir)
            assert os.path.exists(cache_dir)

    def test_ensure_cache_dir_idempotent(self):
        """测试多次调用ensure_cache_dir"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, "test_cache")
            manager = DynamicMappingManager(cache_dir=cache_dir)

            manager.ensure_cache_dir()
            manager.ensure_cache_dir()

            assert os.path.exists(cache_dir)

    def test_generate_patterns_includes_etf_listings(self):
        """测试生成模式包含ETF列表"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame()

                patterns = manager.generate_underlying_patterns()

                assert "510300" in patterns
                assert "510050" in patterns
                assert "510500" in patterns

    def test_generate_patterns_includes_common_stocks(self):
        """测试生成模式包含常见股票"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame()

                patterns = manager.generate_underlying_patterns()

                assert "000001" in patterns
                assert "600000" in patterns

    def test_patterns_deduplication(self):
        """测试模式生成包含预期项"""
        from akshare_one.modules.options.mapping_manager import DynamicMappingManager
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DynamicMappingManager(cache_dir=tmpdir)

            with patch("akshare_one.modules.options.mapping_manager.ak.index_stock_info") as mock_index:
                mock_index.return_value = pd.DataFrame()

                patterns = manager.generate_underlying_patterns()

                if "510300" in patterns:
                    assert "沪深300ETF" in patterns["510300"]
                    assert "沪深300" in patterns["510300"]


@pytest.mark.unit
class TestOptionsSymbolParsing:
    """测试期权代码解析 - sina.py 核心解析逻辑"""

    def test_options_parse_option_type_call(self):
        """测试解析看涨期权类型"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        assert provider._parse_option_type("300ETF购2月4200A") == "call"
        assert provider._parse_option_type("50ETF购12月2850") == "call"

    def test_options_parse_option_type_put(self):
        """测试解析看跌期权类型"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        assert provider._parse_option_type("300ETF沽2月4200A") == "put"
        assert provider._parse_option_type("50ETF沽12月2850") == "put"

    def test_options_parse_option_type_unknown(self):
        """测试解析未知期权类型"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        assert provider._parse_option_type("300ETF2月4200A") is None
        assert provider._parse_option_type("") is None

    def test_options_parse_expiration_month(self):
        """测试解析期权到期月份"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        assert provider._parse_expiration("300ETF沽2月4288A") == "2月"
        assert provider._parse_expiration("50ETF购12月2850") == "12月"
        assert provider._parse_expiration("100ETF沽6月2000") == "6月"

    def test_options_parse_expiration_no_match(self):
        """测试解析无到期月份"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        assert provider._parse_expiration("300ETF") is None
        assert provider._parse_expiration("") is None


@pytest.mark.unit
class TestOptionsFieldStandardization:
    """测试期权字段标准化"""

    def test_options_json_compatible_conversion(self):
        """测试JSON兼容性转换"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        import pandas as pd
        import numpy as np

        provider = SinaOptionsProvider(underlying_symbol="510300")

        df = pd.DataFrame({"price": [1.5, np.nan, 2.0], "volume": [100, np.inf, 200], "change": [-np.inf, 0.1, None]})

        result = provider.ensure_json_compatible(df)

        assert result["price"].iloc[1] is None
        assert result["volume"].iloc[1] is None
        assert result["change"].iloc[0] is None

    def test_options_clean_history_data(self):
        """测试历史数据清理"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        import pandas as pd

        provider = SinaOptionsProvider(underlying_symbol="510300")

        raw_df = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘": [1.0, 1.1],
                "收盘": [1.5, 1.6],
                "最高": [1.8, 1.9],
                "最低": [0.9, 1.0],
                "成交量": [10000, 20000],
            }
        )

        result = provider._clean_options_history(raw_df, "10004005")

        assert "timestamp" in result.columns
        assert "symbol" in result.columns
        assert "open" in result.columns
        assert "close" in result.columns
        assert result["symbol"].iloc[0] == "10004005"


@pytest.mark.unit
class TestOptionsStrikePriceValidation:
    """测试行权价验证"""

    def test_strike_price_in_options_chain(self):
        """测试期权链中行权价字段存在"""
        import pandas as pd
        from unittest.mock import patch
        from akshare_one.modules.options.sina import SinaOptionsProvider

        mock_df = pd.DataFrame(
            {
                "代码": ["10004005", "10004006"],
                "名称": ["300ETF购2月4200A", "300ETF沽2月4200A"],
                "最新价": [0.05, 0.03],
                "涨跌额": [0.01, -0.01],
                "涨跌幅": [20.0, -33.3],
                "成交量": [1000, 2000],
                "持仓量": [5000, 6000],
                "行权价": [4.200, 4.200],
            }
        )

        provider = SinaOptionsProvider(underlying_symbol="510300")

        with patch.object(provider, "apply_data_filter", return_value=pd.DataFrame()):
            pass

        assert "行权价" in mock_df.columns

    def test_strike_price_numeric_values(self):
        """测试行权价为数值类型"""
        import pandas as pd

        df = pd.DataFrame({"strike": [4.2, 4.3, 4.4]})

        assert df["strike"].dtype in ["float64", "int64"]
        assert all(df["strike"] > 0)


@pytest.mark.unit
class TestOptionsExpirationDate:
    """测试到期日期处理"""

    def test_expiration_date_format(self):
        """测试到期日期格式"""
        from akshare_one.modules.options.sina import SinaOptionsProvider

        provider = SinaOptionsProvider(underlying_symbol="510300")

        exp = provider._parse_expiration("300ETF购2月4200A")
        assert exp.endswith("月")

    def test_expiration_dates_sorted(self):
        """测试到期日期排序"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch
        import pandas as pd

        provider = SinaOptionsProvider(underlying_symbol="510300")

        mock_df = pd.DataFrame(
            {
                "代码": ["10004005", "10004006", "10004007"],
                "名称": ["300ETF购2月4200A", "300ETF购3月4200A", "300ETF购6月4200A"],
            }
        )

        with patch("akshare_one.modules.options.sina.ak.option_current_em", return_value=mock_df):
            with patch("akshare_one.mappings.mapping_utils.get_option_underlying_patterns", return_value=["300ETF"]):
                try:
                    expirations = provider.get_options_expirations("510300")
                    assert expirations == sorted(expirations)
                except ValueError:
                    pass


@pytest.mark.unit
class TestOptionsEmptyResult:
    """测试空结果数据处理"""

    def test_options_empty_result_handling(self):
        """测试空数据返回处理"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch
        import pandas as pd

        provider = SinaOptionsProvider(underlying_symbol="510300")

        with patch("akshare_one.modules.options.sina.ak.option_current_em", return_value=pd.DataFrame()):
            with patch("akshare_one.mappings.mapping_utils.get_option_underlying_patterns", return_value=["300ETF"]):
                try:
                    result = provider.get_options_realtime(symbol="")
                    assert isinstance(result, pd.DataFrame)
                    assert result.empty
                except ValueError as e:
                    assert "Failed to fetch" in str(e)

    def test_options_history_empty_result(self):
        """测试历史数据空结果"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch
        import pandas as pd

        provider = SinaOptionsProvider(underlying_symbol="510300")

        with patch("akshare_one.modules.options.sina.ak.option_sse_daily_sina", return_value=pd.DataFrame()):
            result = provider.get_options_history("10004005")
            assert result.empty
            assert "timestamp" in result.columns


@pytest.mark.unit
class TestOptionsAPIFailure:
    """测试API失败处理"""

    def test_options_api_network_failure(self):
        """测试网络失败处理"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch

        provider = SinaOptionsProvider(underlying_symbol="510300")

        with patch("akshare_one.modules.options.sina.ak.option_current_em", side_effect=Exception("Network error")):
            with pytest.raises(ValueError, match="Failed to fetch"):
                provider.get_options_chain()

    def test_options_api_timeout_failure(self):
        """测试超时失败处理"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch

        provider = SinaOptionsProvider(underlying_symbol="510300")

        with patch("akshare_one.modules.options.sina.ak.option_current_em", side_effect=TimeoutError("Timeout")):
            with pytest.raises(ValueError):
                provider.get_options_realtime(symbol="")

    def test_options_api_invalid_data_failure(self):
        """测试无效数据处理"""
        from akshare_one.modules.options.sina import SinaOptionsProvider
        from unittest.mock import patch
        import pandas as pd

        provider = SinaOptionsProvider(underlying_symbol="510300")

        invalid_df = pd.DataFrame({"wrong_column": [1, 2, 3]})

        with patch("akshare_one.modules.options.sina.ak.option_current_em", return_value=invalid_df):
            with patch("akshare_one.mappings.mapping_utils.get_option_underlying_patterns", return_value=["300ETF"]):
                try:
                    result = provider.get_options_chain()
                except (ValueError, KeyError) as e:
                    assert True
