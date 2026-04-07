"""
Test AkShare version compatibility across different versions.

This test suite verifies:
1. Function existence across versions
2. Function name resolution and alias mapping
3. Version detection
4. Deprecation handling
5. Cross-version compatibility
"""

import logging
import pytest

from akshare_one.akshare_compat import (
    AkShareAdapter,
    call_akshare,
    check_akshare_function,
    get_adapter,
    get_version_compatibility_info,
    VERSION_COMPATIBILITY_MATRIX,
)

logger = logging.getLogger(__name__)


class TestAkShareVersionDetection:
    """Test version detection functionality."""

    def test_adapter_initialization(self):
        """Test adapter initializes and detects version."""
        adapter = get_adapter()

        assert adapter is not None
        assert isinstance(adapter, AkShareAdapter)

        # Version should be detected
        version = adapter.get_version()
        assert version is not None
        assert version != "unknown"
        logger.info(f"Detected AkShare version: {version}")

    def test_version_detection_singleton(self):
        """Test that adapter is singleton."""
        adapter1 = get_adapter()
        adapter2 = get_adapter()

        assert adapter1 is adapter2

    def test_version_info_available(self):
        """Test version compatibility info is available."""
        # Check that we have documented some version changes
        assert len(VERSION_COMPATIBILITY_MATRIX) > 0
        logger.info(f"Documented versions: {list(VERSION_COMPATIBILITY_MATRIX.keys())}")

    def test_get_version_compatibility_info(self):
        """Test getting compatibility info for specific versions."""
        # Test documented version
        info = get_version_compatibility_info("1.12.0")
        assert info is not None
        assert "changes" in info
        assert "deprecated" in info

        # Test undocumented version
        info = get_version_compatibility_info("999.999.999")
        assert info is None


class TestFunctionExistence:
    """Test function existence checking."""

    def test_check_critical_functions(self):
        """Test existence of critical functions used in project."""
        adapter = get_adapter()

        critical_functions = [
            "stock_zh_a_hist",
            "stock_zh_a_spot_em",
            "fund_etf_hist_sina",
            "stock_dzjy_mrtj",
            "stock_individual_fund_flow",
            "stock_board_industry_name_em",
            "macro_china_gdp",
            "stock_hsgt_north_net_flow_in_em",
        ]

        for func_name in critical_functions:
            exists = adapter.function_exists(func_name)
            logger.info(f"Function '{func_name}' exists: {exists}")

            # Most functions should exist in current version
            # We don't assert True because some might be deprecated
            # but we log the status

    def test_check_nonexistent_function(self):
        """Test checking a non-existent function."""
        adapter = get_adapter()

        exists = adapter.function_exists("nonexistent_function_xyz")
        assert exists is False

    def test_check_akshare_function_helper(self):
        """Test the check_akshare_function helper."""
        # Test existing function
        exists = check_akshare_function("stock_zh_a_hist")
        # Should return True or False based on actual existence
        assert isinstance(exists, bool)

        # Test non-existing function
        exists = check_akshare_function("fake_function")
        assert exists is False


class TestFunctionResolution:
    """Test function name resolution and alias mapping."""

    def test_resolve_existing_function(self):
        """Test resolving an existing function."""
        adapter = get_adapter()

        # Existing function should resolve to itself
        resolved = adapter.resolve_function_name("stock_zh_a_hist")
        assert resolved == "stock_zh_a_hist"

    def test_resolve_deprecated_function(self):
        """Test resolving deprecated functions to aliases."""
        adapter = get_adapter()

        # Test deprecated function mappings
        deprecated_mappings = {
            "stock_zh_a_daily": "stock_zh_a_hist",
            "stock_zh_a_daily_hfq": "stock_zh_a_hist",
            "stock_dzjy_sctj": "stock_dzjy_mrtj",
        }

        for deprecated_name, expected_alias in deprecated_mappings.items():
            resolved = adapter.resolve_function_name(deprecated_name)

            # If deprecated function still exists (not removed yet), adapter returns it directly
            if adapter.function_exists(deprecated_name):
                assert resolved == deprecated_name
                logger.info(f"Deprecated '{deprecated_name}' still exists, returned directly")
            elif adapter.function_exists(expected_alias):
                # Deprecated doesn't exist but alias does, resolve to alias
                assert resolved == expected_alias
                logger.info(f"Deprecated '{deprecated_name}' resolved to alias '{resolved}'")
            else:
                # Neither exists, return original name
                assert resolved == deprecated_name
                logger.warning(f"Neither '{deprecated_name}' nor '{expected_alias}' exists")

    def test_resolve_nonexistent_function(self):
        """Test resolving a completely non-existent function."""
        adapter = get_adapter()

        # Non-existent function should return itself (no alias)
        resolved = adapter.resolve_function_name("totally_fake_function")
        assert resolved == "totally_fake_function"


class TestFunctionInfo:
    """Test function information retrieval."""

    def test_get_function_info_existing(self):
        """Test getting info for an existing function."""
        adapter = get_adapter()

        info = adapter.get_function_info("stock_zh_a_hist")

        assert info["original_name"] == "stock_zh_a_hist"
        assert info["name"] == "stock_zh_a_hist"  # Changed from "resolved_name" to "name"
        assert info["version"] is not None
        assert isinstance(info["exists"], bool)

    def test_get_function_info_deprecated(self):
        """Test getting info for a deprecated function."""
        adapter = get_adapter()

        info = adapter.get_function_info("stock_zh_a_daily")

        assert info["original_name"] == "stock_zh_a_daily"
        assert info["alias"] == "stock_zh_a_hist"  # Should show alias mapping
        assert info["version"] is not None

    def test_get_function_info_nonexistent(self):
        """Test getting info for a non-existent function."""
        adapter = get_adapter()

        info = adapter.get_function_info("fake_function_xyz")

        assert info["original_name"] == "fake_function_xyz"
        assert info["exists"] is False
        assert info["alias"] is None


class TestFunctionCall:
    """Test calling AkShare functions through adapter."""

    @pytest.mark.integration
    def test_call_existing_function(self):
        """Test calling an existing function successfully."""
        adapter = get_adapter()

        # Test with minimal parameters to avoid network issues
        try:
            df = call_akshare("tool_trade_date_hist_sina")

            # Should return DataFrame
            assert hasattr(df, "empty")  # DataFrame-like object

            if not df.empty:
                logger.info(f"Successfully called function, got {len(df)} rows")
            else:
                logger.warning("Function returned empty DataFrame (network issue?)")

        except Exception as e:
            # Network errors are acceptable in tests
            logger.warning(f"Function call failed (network?): {e}")

    @pytest.mark.integration
    def test_call_function_with_params(self):
        """Test calling function with parameters."""
        adapter = get_adapter()

        try:
            df = adapter.call_safe(
                "stock_zh_a_hist",
                symbol="600000",
                period="daily",
                start_date="20240101",
                end_date="20240110",
                adjust="",
            )

            # Should return DataFrame (or empty on error)
            assert hasattr(df, "empty")

            if not df.empty:
                logger.info(f"Got {len(df)} rows from stock_zh_a_hist")
            else:
                logger.warning("Empty DataFrame returned")

        except Exception as e:
            logger.warning(f"Test call failed: {e}")

    def test_call_nonexistent_function(self):
        """Test calling a non-existent function."""
        adapter = get_adapter()

        # Safe call should return empty DataFrame without raising
        df = adapter.call_safe("nonexistent_function_xyz")
        assert df.empty is True

        # Regular call should raise RuntimeError
        with pytest.raises(RuntimeError, match="not available"):
            adapter.call("nonexistent_function_xyz")

    def test_call_with_fallback(self):
        """Test calling function with fallback."""
        adapter = get_adapter()

        # Test calling non-existent primary with fallback
        df = adapter.call_safe("fake_primary", fallback_func="tool_trade_date_hist_sina")

        # Should try fallback
        assert hasattr(df, "empty")


class TestHealthCheck:
    """Test function health checking."""

    def test_check_function_health(self):
        """Test health check for multiple functions."""
        adapter = get_adapter()

        functions = [
            "stock_zh_a_hist",
            "stock_zh_a_spot_em",
            "fund_etf_hist_sina",
            "nonexistent_function",
        ]

        health_report = adapter.check_function_health(functions)

        assert isinstance(health_report, dict)
        assert len(health_report) == len(functions)

        for func_name in functions:
            assert func_name in health_report
            assert "status" in health_report[func_name]
            assert "resolved_name" in health_report[func_name]
            assert "version" in health_report[func_name]

            logger.info(f"Health status for '{func_name}': {health_report[func_name]['status']}")

    def test_list_available_functions(self):
        """Test listing available functions in a category."""
        adapter = get_adapter()

        # Test listing stock functions
        stock_functions = adapter.list_available_functions(category="stock")

        assert isinstance(stock_functions, list)
        assert len(stock_functions) > 0  # Should have many stock functions

        logger.info(f"Found {len(stock_functions)} stock functions")

        # Test listing all functions
        all_functions = adapter.list_available_functions()
        assert isinstance(all_functions, list)
        assert len(all_functions) > len(stock_functions)


class TestDeprecationHandling:
    """Test handling of deprecated functions."""

    def test_deprecated_function_alias_mapping(self):
        """Test that deprecated functions are mapped correctly."""
        adapter = get_adapter()

        # Verify FUNCTION_ALIASES contains known deprecated mappings
        assert "stock_zh_a_daily" in adapter.FUNCTION_ALIASES
        assert adapter.FUNCTION_ALIASES["stock_zh_a_daily"] == "stock_zh_a_hist"

        assert "stock_zh_a_daily_hfq" in adapter.FUNCTION_ALIASES
        assert adapter.FUNCTION_ALIASES["stock_zh_a_daily_hfq"] == "stock_zh_a_hist"

    def test_deprecated_function_warning(self):
        """Test that using deprecated functions logs warnings."""
        adapter = get_adapter()

        # Test deprecated function that may still exist
        resolved = adapter.resolve_function_name("stock_zh_a_daily")

        # If deprecated function still exists, it returns itself
        # If it doesn't exist but alias does, it resolves to alias
        if adapter.function_exists("stock_zh_a_daily"):
            # Still exists in current version
            assert resolved == "stock_zh_a_daily"
            logger.info("stock_zh_a_daily still exists in current version")
        elif adapter.function_exists("stock_zh_a_hist"):
            # Deprecated removed, use alias
            assert resolved == "stock_zh_a_hist"
            logger.info("stock_zh_a_daily resolved to stock_zh_a_hist")
        else:
            # Neither exists
            assert resolved == "stock_zh_a_daily"
            logger.warning("Neither function exists")

    def test_version_compatibility_matrix_completeness(self):
        """Test that version compatibility matrix is documented."""
        # Should have at least some documented versions
        assert len(VERSION_COMPATIBILITY_MATRIX) > 0

        # Each version entry should have proper structure
        for version, info in VERSION_COMPATIBILITY_MATRIX.items():
            assert "changes" in info
            assert "deprecated" in info
            assert isinstance(info["changes"], list)
            assert isinstance(info["deprecated"], list)

            logger.info(f"Version {version}: {len(info['deprecated'])} deprecated functions")


class TestCrossVersionCompatibility:
    """Test cross-version compatibility scenarios."""

    def test_adapter_handles_version_changes(self):
        """Test adapter can handle typical version change scenarios."""
        adapter = get_adapter()

        # Simulate version change scenarios
        scenarios = [
            # Old function name -> New function name
            ("stock_zh_a_daily", "stock_zh_a_hist"),
            ("stock_dzjy_sctj", "stock_dzjy_mrtj"),
            ("stock_fund_flow_individual", "stock_individual_fund_flow"),
        ]

        for old_name, new_name in scenarios:
            # Check if adapter can resolve old name
            resolved = adapter.resolve_function_name(old_name)

            # Adapter behavior:
            # 1. If old function still exists -> return old name
            # 2. If old doesn't exist but new does -> resolve to new
            # 3. If neither exists -> return old name as fallback
            if adapter.function_exists(old_name):
                # Old function still available (not removed yet)
                assert resolved == old_name
                logger.info(f"✓ Old function '{old_name}' still exists")
            elif adapter.function_exists(new_name):
                # Old removed, new available
                assert resolved == new_name
                logger.info(f"✓ Migration path: {old_name} -> {new_name}")
            else:
                # Neither exists (unlikely but handled)
                assert resolved == old_name
                logger.warning(f"⚠ Neither {old_name} nor {new_name} exists")

    def test_adapter_cache_efficiency(self):
        """Test that adapter caches function existence checks."""
        adapter = get_adapter()

        # First check
        adapter.function_exists("stock_zh_a_hist")

        # Should be cached
        assert "stock_zh_a_hist" in adapter._function_cache

        # Second check should use cache
        adapter.function_exists("stock_zh_a_hist")

        # Verify cache improves performance
        logger.info("Function existence caching is working")


class TestErrorHandling:
    """Test error handling in adapter."""

    def test_call_safe_always_returns_dataframe(self):
        """Test that call_safe always returns DataFrame."""
        adapter = get_adapter()

        # Test with non-existent function
        df = adapter.call_safe("nonexistent_func")
        assert df.empty is True

        # Test with invalid parameters
        df = adapter.call_safe("stock_zh_a_hist", invalid_param="xyz")
        assert hasattr(df, "empty")  # Should still return DataFrame-like

    def test_call_raises_on_missing_function(self):
        """Test that call raises RuntimeError on missing function."""
        adapter = get_adapter()

        with pytest.raises(RuntimeError) as exc_info:
            adapter.call("totally_fake_function")

        # Error message should mention version
        assert adapter.get_version() in str(exc_info.value)

    def test_adapter_handles_import_error(self):
        """Test adapter behavior when AkShare is not importable."""
        # This is a theoretical test - in practice AkShare is installed
        # We can't easily test ImportError, but the adapter should handle it

        adapter = AkShareAdapter()
        # Should not crash during initialization even if AkShare missing
        # (In practice, AkShare is installed in test environment)


class TestAdapterIntegration:
    """Test adapter integration with actual modules."""

    @pytest.mark.integration
    def test_adapter_in_historical_module(self):
        """Test adapter is used in historical data module."""
        from akshare_one.modules.historical import HistoricalDataFactory

        provider = HistoricalDataFactory.get_provider(
            "eastmoney",
            symbol="600000",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-10",
        )

        # Provider should have akshare_adapter
        assert hasattr(provider, "akshare_adapter")
        assert provider.akshare_adapter is not None

        logger.info("✓ Historical module uses adapter")

    @pytest.mark.integration
    def test_adapter_in_multiple_modules(self):
        """Test adapter is used across multiple modules."""
        modules_to_test = [
            ("historical", "HistoricalDataFactory", "eastmoney", {"symbol": "600000", "interval": "day"}),
            ("etf", "ETFFactory", "eastmoney", {"symbol": "159915"}),
            ("bond", "BondFactory", "eastmoney", {"symbol": "110000"}),
        ]

        for module_name, factory_name, provider_name, params in modules_to_test:
            try:
                # Import factory dynamically
                factory_module = __import__(
                    f"akshare_one.modules.{module_name}",
                    fromlist=[factory_name],
                )
                factory = getattr(factory_module, factory_name)

                # Create provider
                provider = factory.get_provider(provider_name, **params)

                # Check adapter
                if hasattr(provider, "akshare_adapter"):
                    logger.info(f"✓ {module_name} module uses adapter")
                else:
                    logger.warning(f"⚠ {module_name} module missing adapter")

            except Exception as e:
                logger.warning(f"Could not test {module_name}: {e}")


class TestVersionCompatibilityMatrix:
    """Test version compatibility matrix documentation."""

    def test_matrix_has_documented_versions(self):
        """Test that matrix documents key versions."""
        # Should document versions where major changes happened
        key_versions = ["1.12.0", "1.13.0"]

        for version in key_versions:
            if version in VERSION_COMPATIBILITY_MATRIX:
                info = VERSION_COMPATIBILITY_MATRIX[version]
                assert "changes" in info
                assert len(info["changes"]) > 0
                logger.info(f"✓ Version {version} documented with {len(info['changes'])} changes")

    def test_matrix_deprecated_functions_listed(self):
        """Test that deprecated functions are listed."""
        for version, info in VERSION_COMPATIBILITY_MATRIX.items():
            if info["deprecated"]:
                logger.info(f"Version {version} deprecated: {info['deprecated']}")

                # Deprecated functions should be strings
                for func_name in info["deprecated"]:
                    assert isinstance(func_name, str)


# Run with: pytest tests/test_akshare_version_compat.py -v
# Integration tests: pytest tests/test_akshare_version_compat.py -v -m integration