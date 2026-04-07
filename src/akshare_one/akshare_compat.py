"""
AkShare Compatibility Layer - Handles function name drift across versions.

This module provides a compatibility layer to handle AkShare function name changes
across different versions, preventing hard failures when functions are renamed or removed.

Key features:
- Runtime function existence detection
- Version-specific function mapping
- Graceful degradation with fallback functions
- Clear error messages for missing functions
"""

import logging
from typing import Any, Callable

import pandas as pd

logger = logging.getLogger(__name__)


class AkShareAdapter:
    """
    Adapter class for AkShare API compatibility.

    Handles function name drift across AkShare versions by:
    1. Detecting function existence at runtime
    2. Mapping deprecated function names to current names
    3. Providing fallback alternatives when functions are unavailable
    4. Logging warnings for deprecated function usage

    Example:
        >>> adapter = AkShareAdapter()
        >>> df = adapter.call("stock_zh_a_hist", symbol="600000", period="daily")
        >>> # Automatically handles function renaming across versions
    """

    # Version-specific function mappings
    # Maps old/deprecated function names to current names
    FUNCTION_ALIASES = {
        # Stock historical data
        "stock_zh_a_hist_min_em": "stock_zh_a_hist_min_em",  # Current
        "stock_zh_a_hist": "stock_zh_a_hist",  # Current
        "stock_zh_a_daily": "stock_zh_a_hist",  # Deprecated in 1.12+ -> Current
        "stock_zh_a_daily_hfq": "stock_zh_a_hist",  # Deprecated in 1.12+ -> Current

        # ETF data
        "fund_etf_hist_sina": "fund_etf_hist_sina",  # Current
        "fund_etf_fund_daily_em": "fund_etf_hist_sina",  # Fallback

        # Block deal (大宗交易)
        "stock_dzjy_mrtj": "stock_dzjy_mrtj",  # Current (daily statistics)
        "stock_dzjy_mrmx": "stock_dzjy_mrmx",  # Current (transaction details)
        "stock_dzjy_sctj": "stock_dzjy_mrtj",  # Deprecated in 1.13+ -> Current

        # Fund flow (资金流)
        "stock_individual_fund_flow": "stock_individual_fund_flow",  # Current
        "stock_individual_fund_flow_rank": "stock_individual_fund_flow_rank",  # Current
        "stock_sector_fund_flow_rank": "stock_sector_fund_flow_rank",  # Current
        "stock_fund_flow_individual": "stock_individual_fund_flow",  # Deprecated in 1.13+ -> Current

        # Board/Industry/Concept (板块)
        "stock_board_industry_name_em": "stock_board_industry_name_em",  # Current
        "stock_board_industry_cons_em": "stock_board_industry_cons_em",  # Current
        "stock_board_concept_name_em": "stock_board_concept_name_em",  # Current
        "stock_board_concept_cons_em": "stock_board_concept_cons_em",  # Current

        # KCB/CYB Board (科创板/创业板)
        "stock_kcb_spot_em": "stock_kcb_spot_em",  # Current
        "stock_kcb_spot": "stock_kcb_spot_em",  # Fallback alias
        "stock_cyb_spot_em": "stock_cyb_spot_em",  # Current
        "stock_cyb_spot": "stock_cyb_spot_em",  # Fallback alias

        # Real-time data
        "stock_zh_a_spot_em": "stock_zh_a_spot_em",  # Current
        "stock_zh_a_spot": "stock_zh_a_spot_em",  # Fallback

        # Macro data
        "macro_china_gdp": "macro_china_gdp",  # Current
        "macro_china_cpi": "macro_china_cpi",  # Current
        "macro_china_ppi": "macro_china_ppi",  # Current

        # Northbound资金
        "stock_hsgt_north_net_flow_in_em": "stock_hsgt_hist_em",  # Fallback to historical data
        "stock_hsgt_north_acc_flow_in_em": "stock_hsgt_hist_em",  # Fallback to historical data
        "stock_hsgt_hist_em": "stock_hsgt_hist_em",  # Current
        "stock_hsgt_hold_stock_em": "stock_hsgt_hold_stock_em",  # Current
        "stock_em_hsgt_north_net_flow_in": "stock_hsgt_hist_em",  # Deprecated in 1.18+ -> Fallback
        "stock_em_hsgt_north_acc_flow_in": "stock_hsgt_hist_em",  # Deprecated in 1.18+ -> Fallback

        # Financial reports
        "stock_financial_report_sina": "stock_financial_report_sina",  # Current

        # Margin trading
        "stock_margin_detail_szse": "stock_margin_detail_szse",  # Current
        "stock_margin_detail_sse": "stock_margin_detail_sse",  # Current

        # Pledge data
        "stock_gpzy_pledge_ratio_em": "stock_gpzy_pledge_ratio_em",  # Current
        "stock_gpzy_pledge_ratio_detail_em": "stock_gpzy_pledge_ratio_detail_em",  # Current

        # Dragon-Tiger List (龙虎榜)
        "stock_lhb_detail_em": "stock_lhb_detail_em",  # Current
        "stock_lhb_stock_statistic_em": "stock_lhb_stock_statistic_em",  # Current
        "stock_lhb_traderstatistic_em": "stock_lhb_traderstatistic_em",  # Current

        # Limit Up (涨停)
        "stock_zt_pool_em": "stock_zt_pool_em",  # Current
        "stock_zt_pool_previous_em": "stock_zt_pool_previous_em",  # Current

        # Disclosure
        "stock_notice_report": "stock_notice_report",  # Current

        # ESG
        "stock_esg_rate_sina": "stock_esg_rate_sina",  # Current

        # Futures
        "futures_zh_minute_sina": "futures_zh_minute_sina",  # Current
        "futures_zh_daily_sina": "futures_zh_daily_sina",  # Current
        "futures_zh_realtime": "futures_zh_realtime",  # Current
        "futures_zh_spot": "futures_zh_spot",  # Current

        # Options
        "option_current_em": "option_current_em",  # Current
        "option_sse_daily_sina": "option_sse_daily_sina",  # Current

        # Index
        "index_stock_info": "index_stock_info",  # Current
        "index_zh_a_hist": "index_zh_a_hist",  # Current

        # Bond
        "bond_cb_jsl": "bond_cb_jsl",  # Current

        # Utility
        "tool_trade_date_hist_sina": "tool_trade_date_hist_sina",  # Current
    }

    # Version-specific degradation paths
    # Maps version ranges to specific function fallback chains
    VERSION_FALLBACK_CHAINS = {
        # Versions < 1.12.0: Use old stock_zh_a_daily functions
        "<1.12.0": {
            "stock_zh_a_hist": ["stock_zh_a_daily", "stock_zh_a_daily_hfq"],
        },
        # Versions 1.12.0 - 1.13.0: stock_zh_a_hist available, but some old names deprecated
        "1.12.0-1.13.0": {
            "stock_zh_a_hist": ["stock_zh_a_hist"],  # Primary function
            "stock_dzjy_mrtj": ["stock_dzjy_sctj"],  # Old name still works
        },
        # Versions 1.13.0 - 1.18.0: More function renames
        "1.13.0-1.18.0": {
            "stock_individual_fund_flow": ["stock_fund_flow_individual"],
        },
        # Versions >= 1.18.0: Northbound function naming change
        ">=1.18.0": {
            "stock_hsgt_north_net_flow_in_em": ["stock_hsgt_north_net_flow_in_em"],
            "stock_em_hsgt_north_net_flow_in": ["stock_hsgt_north_net_flow_in_em"],
        },
    }

    # Function availability cache (to avoid repeated checks)
    _function_cache: dict[str, bool] = {}

    # AkShare version (detected at runtime)
    _akshare_version: str | None = None

    def __init__(self):
        """Initialize the adapter and detect AkShare version."""
        self._detect_version()

    def _detect_version(self) -> None:
        """Detect current AkShare version."""
        try:
            import akshare

            self._akshare_version = getattr(akshare, "__version__", "unknown")
            logger.info(f"Detected AkShare version: {self._akshare_version}")

            # Validate version against supported range
            self._validate_version()

        except ImportError:
            logger.error("AkShare is not installed")
            self._akshare_version = None

    def _validate_version(self) -> None:
        """Validate that AkShare version is supported."""
        if not self._akshare_version or self._akshare_version == "unknown":
            logger.warning("Could not detect AkShare version, proceeding with defaults")
            return

        # Parse version (format: X.Y.Z or X.Y.ZZ)
        try:
            version_parts = self._akshare_version.split(".")
            if len(version_parts) >= 2:
                major = int(version_parts[0])
                minor = int(version_parts[1])

                # Check minimum version (1.17.80)
                if major == 1 and minor < 17:
                    logger.warning(
                        f"AkShare version {self._akshare_version} is below minimum supported version 1.17.80. "
                        f"Some functions may not be available. Consider upgrading to 1.18.23."
                    )
                elif major == 1 and minor >= 17:
                    logger.info(f"AkShare version {self._akshare_version} is supported")
                else:
                    logger.warning(f"AkShare version {self._akshare_version} is unknown, proceed with caution")

        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse version {self._akshare_version}: {e}")

    def get_version(self) -> str | None:
        """Get detected AkShare version."""
        return self._akshare_version

    def function_exists(self, func_name: str) -> bool:
        """
        Check if an AkShare function exists.

        Args:
            func_name: Function name to check

        Returns:
            True if function exists, False otherwise
        """
        # Check cache first
        if func_name in self._function_cache:
            return self._function_cache[func_name]

        try:
            import akshare as ak

            exists = hasattr(ak, func_name) and callable(getattr(ak, func_name))
            self._function_cache[func_name] = exists

            if not exists:
                logger.warning(
                    f"AkShare function '{func_name}' not found in version {self._akshare_version}"
                )

            return exists

        except ImportError:
            logger.error("AkShare is not installed")
            return False

    def resolve_function_name(self, func_name: str) -> str:
        """
        Resolve a function name to its current valid name.

        If the requested function doesn't exist, tries to find an alias
        from the FUNCTION_ALIASES mapping. Also checks version-specific
        fallback chains.

        Args:
            func_name: Original function name

        Returns:
            Resolved function name (may be different if aliased)
        """
        # If function exists directly, use it
        if self.function_exists(func_name):
            return func_name

        # Try to find an alias from FUNCTION_ALIASES
        if func_name in self.FUNCTION_ALIASES:
            alias = self.FUNCTION_ALIASES[func_name]
            if self.function_exists(alias):
                logger.warning(
                    f"Function '{func_name}' not found, using alias '{alias}' instead. "
                    f"Consider updating your code to use '{alias}' directly."
                )
                return alias

        # Try version-specific fallback chains
        fallback_name = self._try_version_specific_fallback(func_name)
        if fallback_name and self.function_exists(fallback_name):
            logger.warning(
                f"Using version-specific fallback for '{func_name}': '{fallback_name}' "
                f"(version: {self._akshare_version})"
            )
            return fallback_name

        # No valid function found
        logger.error(
            f"No valid function found for '{func_name}'. "
            f"Checked aliases: {self.FUNCTION_ALIASES.get(func_name, 'none')}"
        )
        return func_name

    def _try_version_specific_fallback(self, func_name: str) -> str | None:
        """
        Try to find a version-specific fallback for a function.

        Args:
            func_name: Function name to find fallback for

        Returns:
            Fallback function name if found, None otherwise
        """
        if not self._akshare_version:
            return None

        # Parse version
        try:
            version_parts = self._akshare_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0

            # Check each version range
            for version_range, fallbacks in self.VERSION_FALLBACK_CHAINS.items():
                if self._version_matches_range(major, minor, version_range):
                    if func_name in fallbacks:
                        # Return first available fallback
                        for fallback in fallbacks[func_name]:
                            if self.function_exists(fallback):
                                return fallback

        except (ValueError, IndexError):
            pass

        return None

    def _version_matches_range(self, major: int, minor: int, version_range: str) -> bool:
        """
        Check if version matches a version range specification.

        Args:
            major: Major version number
            minor: Minor version number
            version_range: Range specification (e.g., "<1.12.0", ">=1.18.0", "1.12.0-1.13.0")

        Returns:
            True if version matches range
        """
        # Parse range specification
        if version_range.startswith("<"):
            # Less than (e.g., "<1.12.0")
            target = version_range[1:].split(".")
            target_major = int(target[0])
            target_minor = int(target[1]) if len(target) > 1 else 0
            return major < target_major or (major == target_major and minor < target_minor)

        elif version_range.startswith(">="):
            # Greater or equal (e.g., ">=1.18.0")
            target = version_range[2:].split(".")
            target_major = int(target[0])
            target_minor = int(target[1]) if len(target) > 1 else 0
            return major > target_major or (major == target_major and minor >= target_minor)

        elif "-" in version_range:
            # Range (e.g., "1.12.0-1.13.0")
            start, end = version_range.split("-")
            start_parts = start.split(".")
            end_parts = end.split(".")

            start_major = int(start_parts[0])
            start_minor = int(start_parts[1]) if len(start_parts) > 1 else 0

            end_major = int(end_parts[0])
            end_minor = int(end_parts[1]) if len(end_parts) > 1 else 0

            # Check if version is in range
            return (major >= start_major and minor >= start_minor) and (
                major <= end_major and minor <= end_minor
            )

        return False

    def get_function(self, func_name: str) -> Callable | None:
        """
        Get an AkShare function by name with automatic alias resolution.

        Args:
            func_name: Function name to retrieve

        Returns:
            Callable function if found, None otherwise
        """
        resolved_name = self.resolve_function_name(func_name)

        if not self.function_exists(resolved_name):
            return None

        try:
            import akshare as ak

            return getattr(ak, resolved_name)
        except Exception as e:
            logger.error(f"Failed to get function '{resolved_name}': {e}")
            return None

    def call(
        self,
        func_name: str,
        *args,
        fallback_func: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Call an AkShare function with automatic error handling and fallback.

        This method:
        1. Resolves the function name (handling aliases)
        2. Checks if the function exists
        3. Calls the function with provided arguments
        4. Falls back to alternative function if primary fails
        5. Returns empty DataFrame if all attempts fail

        Args:
            func_name: Primary function name to call
            *args: Positional arguments for the function
            fallback_func: Alternative function name to try if primary fails
            **kwargs: Keyword arguments for the function

        Returns:
            DataFrame with results, or empty DataFrame on failure

        Raises:
            RuntimeError: If function call fails and no fallback is available

        Example:
            >>> adapter = AkShareAdapter()
            >>> df = adapter.call(
            ...     "stock_zh_a_hist",
            ...     symbol="600000",
            ...     period="daily",
            ...     fallback_func="fund_etf_hist_sina"
            ... )
        """
        # Try primary function
        func = self.get_function(func_name)

        if func is not None:
            try:
                logger.debug(
                    f"Calling AkShare function '{func_name}' with args: {args}, kwargs: {kwargs}"
                )
                result = func(*args, **kwargs)

                # Ensure result is a DataFrame
                if isinstance(result, pd.DataFrame):
                    return result
                elif isinstance(result, dict):
                    # Some functions return dict, convert to DataFrame
                    return pd.DataFrame(result)
                else:
                    logger.warning(
                        f"Function '{func_name}' returned unexpected type: {type(result)}"
                    )
                    return pd.DataFrame()

            except Exception as e:
                logger.error(
                    f"Failed to call function '{func_name}' with args {kwargs}: {e}",
                    exc_info=True,
                )

                # Try fallback if available
                if fallback_func:
                    logger.info(f"Attempting fallback function '{fallback_func}'")
                    return self.call(fallback_func, *args, **kwargs)

                # No fallback, return empty DataFrame
                return pd.DataFrame()

        # Primary function not found, try fallback
        if fallback_func:
            logger.warning(
                f"Primary function '{func_name}' not available, "
                f"trying fallback '{fallback_func}'"
            )
            return self.call(fallback_func, *args, **kwargs)

        # No function available
        error_msg = (
            f"AkShare function '{func_name}' is not available in version {self._akshare_version}. "
            f"This may be due to function renaming or removal in a newer AkShare version. "
            f"Please check AkShare documentation or update the function mapping in akshare_compat.py."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def call_safe(self, func_name: str, *args, **kwargs) -> pd.DataFrame:
        """
        Safely call an AkShare function, returning empty DataFrame on failure.

        This is a non-throwing version of call() that always returns a DataFrame,
        even if the function call fails.

        Args:
            func_name: Function name to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            DataFrame with results, or empty DataFrame on any failure
        """
        try:
            return self.call(func_name, *args, **kwargs)
        except Exception as e:
            logger.warning(f"Safe call failed for '{func_name}': {e}")
            return pd.DataFrame()

    def get_function_info(self, func_name: str) -> dict[str, Any]:
        """
        Get information about an AkShare function.

        Args:
            func_name: Function name to query

        Returns:
            Dict with function information:
            - name: Resolved function name
            - exists: Whether function exists
            - alias: Alias mapping (if applicable)
            - version: AkShare version
        """
        resolved_name = self.resolve_function_name(func_name)
        exists = self.function_exists(resolved_name)
        alias = None

        if func_name in self.FUNCTION_ALIASES:
            alias = self.FUNCTION_ALIASES[func_name]

        return {
            "name": resolved_name,
            "exists": exists,
            "original_name": func_name,
            "alias": alias,
            "version": self._akshare_version,
        }

    def list_available_functions(self, category: str | None = None) -> list[str]:
        """
        List all available AkShare functions in a category.

        Args:
            category: Optional category filter (e.g., 'stock', 'fund', 'macro')

        Returns:
            List of available function names
        """
        import akshare as ak

        all_functions = [name for name in dir(ak) if not name.startswith("_")]

        if category:
            # Filter by category prefix
            category_prefix = f"{category}_"
            all_functions = [f for f in all_functions if f.startswith(category_prefix)]

        # Verify each function exists and is callable
        available = []
        for func_name in all_functions:
            if self.function_exists(func_name):
                available.append(func_name)

        return available

    def check_function_health(self, func_names: list[str]) -> dict[str, dict[str, Any]]:
        """
        Check health status of multiple AkShare functions.

        Args:
            func_names: List of function names to check

        Returns:
            Dict mapping function names to their health status
        """
        health_report = {}

        for func_name in func_names:
            info = self.get_function_info(func_name)
            health_report[func_name] = {
                "status": "available" if info["exists"] else "unavailable",
                "resolved_name": info["name"],
                "alias": info["alias"],
                "version": info["version"],
            }

        return health_report


# Global adapter instance (singleton pattern)
_global_adapter: AkShareAdapter | None = None


def get_adapter() -> AkShareAdapter:
    """
    Get the global AkShare adapter instance.

    Returns:
        AkShareAdapter singleton instance
    """
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = AkShareAdapter()
    return _global_adapter


def call_akshare(func_name: str, *args, fallback_func: str | None = None, **kwargs) -> pd.DataFrame:
    """
    Convenience function to call AkShare with automatic compatibility handling.

    Args:
        func_name: AkShare function name
        *args: Positional arguments
        fallback_func: Fallback function name if primary fails
        **kwargs: Keyword arguments

    Returns:
        DataFrame with results
    """
    adapter = get_adapter()
    return adapter.call(func_name, *args, fallback_func=fallback_func, **kwargs)


def check_akshare_function(func_name: str) -> bool:
    """
    Check if an AkShare function exists.

    Args:
        func_name: Function name to check

    Returns:
        True if function exists
    """
    adapter = get_adapter()
    return adapter.function_exists(func_name)


# Version compatibility matrix
# Documents known function changes across AkShare versions
VERSION_COMPATIBILITY_MATRIX = {
    "1.12.0": {
        "changes": [
            "stock_zh_a_daily renamed to stock_zh_a_hist",
            "stock_zh_a_daily_hfq merged into stock_zh_a_hist with adjust parameter",
            "New adjust parameter: '' (no adjust), 'hfq' (前复权), 'qfq' (后复权)",
        ],
        "deprecated": ["stock_zh_a_daily", "stock_zh_a_daily_hfq"],
        "impact": "High - affects all historical stock data retrieval",
    },
    "1.13.0": {
        "changes": [
            "stock_dzjy_sctj renamed to stock_dzjy_mrtj (block deal statistics)",
            "stock_fund_flow_individual renamed to stock_individual_fund_flow",
            "Improved parameter naming consistency",
        ],
        "deprecated": ["stock_dzjy_sctj", "stock_fund_flow_individual"],
        "impact": "Medium - affects block deal and fund flow modules",
    },
    "1.18.0": {
        "changes": [
            "stock_em_hsgt_north_net_flow_in renamed to stock_hsgt_north_net_flow_in_em",
            "stock_em_hsgt_north_acc_flow_in renamed to stock_hsgt_north_acc_flow_in_em",
            "Naming convention standardization for northbound capital functions",
        ],
        "deprecated": ["stock_em_hsgt_north_net_flow_in", "stock_em_hsgt_north_acc_flow_in"],
        "impact": "Low - only affects northbound capital module",
    },
    "1.17.80": {
        "changes": [
            "Minimum supported version for akshare-one",
            "All deprecated functions from 1.12-1.13 removed",
            "Stable API for all major modules",
        ],
        "deprecated": [],
        "impact": "Baseline - all functions work as expected",
    },
    "1.18.10": {
        "changes": [
            "Minor bug fixes",
            "Improved error handling",
            "Enhanced data validation",
        ],
        "deprecated": [],
        "impact": "Low - stability improvements",
    },
    "1.18.23": {
        "changes": [
            "Current recommended version",
            "Best stability and performance",
            "All tested functions verified",
        ],
        "deprecated": [],
        "impact": "Recommended for production use",
    },
}


def get_version_compatibility_info(version: str) -> dict[str, Any] | None:
    """
    Get compatibility information for a specific AkShare version.

    Args:
        version: AkShare version string

    Returns:
        Compatibility info dict or None if version not documented
    """
    return VERSION_COMPATIBILITY_MATRIX.get(version)