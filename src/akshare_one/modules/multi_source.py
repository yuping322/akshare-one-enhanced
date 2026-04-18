"""Multi-source data provider with automatic failover.

This module provides a router that automatically tries multiple data sources
and falls back to the next one if the current source fails.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)

T = TypeVar("T")


class EmptyDataPolicy(Enum):
    """空数据处理策略"""

    STRICT = "strict"  # 空结果视为失败（默认）
    RELAXED = "relaxed"  # 空结果视为合法，直接返回
    BEST_EFFORT = "best_effort"  # 尝试所有源，返回第一个非空或合并结果


@dataclass
class ExecutionResult:
    """结果包装类，用于跟踪执行过程"""

    success: bool
    data: pd.DataFrame | None
    source: str | None
    error: str | None
    attempts: int
    error_details: list[tuple[str, str]] | None = None  # [(source, error_msg), ...]
    is_empty: bool = False  # 标记是否为空但合法的结果
    sources_tried: list[dict[str, Any]] = field(default_factory=list)  # 记录每个源的详细状态

    def __post_init__(self) -> None:
        if self.error_details is None:
            self.error_details = []
        if self.sources_tried is None:
            self.sources_tried = []


class MultiSourceRouter:
    """Router that tries multiple data sources with automatic failover.

    Enhanced with:
    - Detailed error tracking and logging
    - Result validation with required columns checking
    - Execution statistics
    - Support for source health status

    Example:
        router = MultiSourceRouter([
            ("eastmoney_direct", eastmoney_provider),
            ("eastmoney", eastmoney_backup_provider),
            ("sina", sina_provider),
        ])
        df = router.execute("get_hist_data")
    """

    def __init__(
        self,
        providers: list[tuple[str, Any]],
        enable_logging: bool = True,
        required_columns: list[str] | None = None,
        min_rows: int = 0,
        empty_data_policy: EmptyDataPolicy = EmptyDataPolicy.STRICT,
    ) -> None:
        """Initialize the router with a list of providers.

        Args:
            providers: List of (name, provider_instance) tuples, in priority order
            enable_logging: Whether to log failover events
            required_columns: List of required columns in result DataFrame
            min_rows: Minimum number of rows required for valid result
            empty_data_policy: Policy for handling empty DataFrame results
        """
        self.providers = providers
        self.enable_logging = enable_logging
        self.required_columns = required_columns or []
        self.min_rows = min_rows
        self.empty_data_policy = empty_data_policy
        self.execution_stats: dict[str, dict[str, int]] = {}  # Track success/failure per source

    def _validate_result(self, result: Any, is_empty_allowed: bool = False) -> bool:
        """Validate if result meets quality requirements.

        Args:
            result: Result to validate
            is_empty_allowed: Whether empty DataFrame is considered valid

        Returns:
            bool: True if result is valid, False otherwise
        """
        if result is None:
            return False

        if not isinstance(result, pd.DataFrame):
            return False

        # Handle empty DataFrame based on policy
        if result.empty:
            if is_empty_allowed:
                return True  # Empty but allowed by policy
            return False  # Empty and not allowed

        # Check minimum rows
        if len(result) < self.min_rows:
            return False

        # Check required columns
        if self.required_columns:
            missing_columns = set(self.required_columns) - set(result.columns)
            if missing_columns:
                logger.warning(f"Missing required columns: {missing_columns}")
                return False

        return True

    def _update_stats(self, source: str, success: bool, duration_ms: float = 0.0) -> None:
        """Update execution statistics for a source.

        Args:
            source: Source name
            success: Whether execution was successful
            duration_ms: Duration of the request in milliseconds
        """
        if source not in self.execution_stats:
            self.execution_stats[source] = {"success": 0, "failure": 0}

        if success:
            self.execution_stats[source]["success"] += 1
        else:
            self.execution_stats[source]["failure"] += 1

        # Integrate with global StatsCollector
        try:
            from ..metrics import get_stats_collector

            stats_collector = get_stats_collector()
            stats_collector.record_request(source, duration_ms, success)
        except (ImportError, AttributeError):
            pass

    def get_stats(self) -> dict[str, dict[str, int]]:
        """Get execution statistics.

        Returns:
            dict: Statistics for each source
        """
        return self.execution_stats.copy()

    def execute(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Execute a method across providers with automatic failover.

        Args:
            method_name: Name of the method to call on providers
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            pd.DataFrame: Result from the first successful provider

        Raises:
            ValueError: If all providers fail (in STRICT mode)
                       If all providers fail and no non-empty result (in BEST_EFFORT mode)
        """
        error_details: list[tuple[str, str]] = []
        import time

        # Track results for BEST_EFFORT mode
        best_result: pd.DataFrame | None = None
        best_source: str | None = None

        for name, provider in self.providers:
            start_time = time.time()
            try:
                method = getattr(provider, method_name)
                result = method(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Check if result is a DataFrame
                if not isinstance(result, pd.DataFrame):
                    self._update_stats(name, False, duration_ms)
                    error_details.append((name, "Result is not a DataFrame"))
                    continue

                # Handle empty DataFrame based on policy
                if result.empty:
                    if self.empty_data_policy == EmptyDataPolicy.RELAXED:
                        # RELAXED: Empty result is valid, return immediately
                        self._update_stats(name, True, duration_ms)
                        result.attrs["source"] = name  # Set source attribution
                        if self.enable_logging:
                            logger.info(f"Provider '{name}' returned empty DataFrame (RELAXED policy)")
                        return result

                    elif self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT:
                        # BEST_EFFORT: Track empty result, continue trying other sources
                        if best_result is None:
                            best_result = result
                            best_source = name
                        self._update_stats(name, True, duration_ms)
                        if self.enable_logging:
                            logger.info(f"Provider '{name}' returned empty DataFrame, continuing to next source")
                        continue

                    else:  # STRICT (default)
                        # STRICT: Empty result is invalid, try next source
                        self._update_stats(name, False, duration_ms)
                        error_details.append((name, "Empty DataFrame (STRICT policy)"))
                        if self.enable_logging:
                            logger.warning(f"Provider '{name}' returned empty DataFrame for '{method_name}'")
                        continue

                # Non-empty DataFrame - validate it
                if self._validate_result(result, is_empty_allowed=False):
                    self._update_stats(name, True, duration_ms)
                    result.attrs["source"] = name  # Set source attribution
                    if self.enable_logging and error_details:
                        logger.info(
                            f"Successfully fetched data from '{name}' after {len(error_details)} failed attempt(s)"
                        )
                    return result

                # Non-empty but invalid (missing columns or min_rows)
                self._update_stats(name, False, duration_ms)
                error_details.append((name, "Invalid result (missing required columns or min_rows)"))
                if self.enable_logging:
                    logger.warning(
                        f"Provider '{name}' returned invalid result for '{method_name}' "
                        f"(missing required columns or insufficient rows)"
                    )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self._update_stats(name, False, duration_ms)
                error_details.append((name, str(e)))

        # All providers processed - handle based on policy
        if self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT and best_result is not None:
            # Return best available result (even if empty)
            best_result.attrs["source"] = best_source  # Set source attribution
            if self.enable_logging:
                logger.info(f"Returning best available result from '{best_source}' (BEST_EFFORT policy)")
            return best_result

        # All providers failed or no valid result
        error_summary = "\n".join([f"  {source}: {error}" for source, error in error_details])
        raise ValueError(f"All data sources failed for '{method_name}':\n{error_summary}")

    def execute_with_fallback(
        self,
        primary_method: str,
        fallback_method: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Execute with optional different fallback method.

        Some providers may have different method names for similar functionality.

        Args:
            primary_method: Primary method name to try
            fallback_method: Fallback method name if different from primary
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            pd.DataFrame: Result from the first successful provider

        Raises:
            ValueError: If all providers fail (in STRICT mode)
                       If all providers fail and no non-empty result (in BEST_EFFORT mode)
        """
        error_details: list[tuple[str, str]] = []

        # Track results for BEST_EFFORT mode
        best_result: pd.DataFrame | None = None
        best_source: str | None = None

        for name, provider in self.providers:
            try:
                # Try primary method name first
                if hasattr(provider, primary_method):
                    method = primary_method
                elif fallback_method and hasattr(provider, fallback_method):
                    method = fallback_method
                    if self.enable_logging:
                        logger.info(
                            f"Provider '{name}' doesn't have '{primary_method}', "
                            f"using fallback method '{fallback_method}'"
                        )
                else:
                    error_msg = f"Provider has neither '{primary_method}' nor '{fallback_method}'"
                    error_details.append((name, error_msg))
                    self._update_stats(name, False)
                    raise AttributeError(error_msg)

                method_func = getattr(provider, method)
                result = method_func(*args, **kwargs)

                # Check if result is a DataFrame
                if not isinstance(result, pd.DataFrame):
                    error_msg = "Result is not a DataFrame"
                    error_details.append((name, error_msg))
                    self._update_stats(name, False)
                    continue

                # Handle empty DataFrame based on policy
                if result.empty:
                    if self.empty_data_policy == EmptyDataPolicy.RELAXED:
                        # RELAXED: Empty result is valid, return immediately
                        self._update_stats(name, True)
                        if self.enable_logging:
                            logger.info(f"Provider '{name}' returned empty DataFrame (RELAXED policy)")
                        return result

                    elif self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT:
                        # BEST_EFFORT: Track empty result, continue trying other sources
                        if best_result is None:
                            best_result = result
                            best_source = name
                        self._update_stats(name, True)
                        if self.enable_logging:
                            logger.info(f"Provider '{name}' returned empty DataFrame, continuing to next source")
                        continue

                    else:  # STRICT (default)
                        # STRICT: Empty result is invalid, try next source
                        error_msg = "Empty DataFrame (STRICT policy)"
                        error_details.append((name, error_msg))
                        self._update_stats(name, False)
                        if self.enable_logging:
                            logger.warning(f"Provider '{name}' returned empty DataFrame (STRICT policy)")
                        continue

                # Non-empty DataFrame - validate it
                if self._validate_result(result, is_empty_allowed=False):
                    self._update_stats(name, True)
                    return result

                error_msg = "Invalid result (missing required columns or min_rows)"
                error_details.append((name, error_msg))
                self._update_stats(name, False)
                if self.enable_logging:
                    logger.warning(f"Provider '{name}' returned invalid result")

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                error_details.append((name, error_msg))
                self._update_stats(name, False)
                if self.enable_logging:
                    logger.warning(f"Provider '{name}' failed: {error_msg}")
                continue

        # All providers processed - handle based on policy
        if self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT and best_result is not None:
            # Return best available result (even if empty)
            if self.enable_logging:
                logger.info(f"Returning best available result from '{best_source}' (BEST_EFFORT policy)")
            return best_result

        # All providers failed or no valid result
        error_summary = "\n".join([f"  {source}: {error}" for source, error in error_details])
        raise ValueError(f"All providers failed for '{primary_method}' (or '{fallback_method}'):\n{error_summary}")

    def execute_with_result(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute and return detailed result with execution statistics.

        Args:
            method_name: Name of the method to call on providers
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            ExecutionResult: Execution result with metadata

        Note:
            Unlike execute(), this method never raises an exception.
            Check ExecutionResult.success to determine if execution was successful.
            For BEST_EFFORT mode, check ExecutionResult.is_empty to see if result is empty.
        """
        error_details: list[tuple[str, str]] = []
        attempt = 0
        sources_tried: list[dict[str, Any]] = []

        # Track results for BEST_EFFORT mode
        best_result: pd.DataFrame | None = None
        best_source: str | None = None
        best_is_empty = False

        for name, provider in self.providers:
            attempt += 1
            try:
                method = getattr(provider, method_name)
                result = method(*args, **kwargs)

                # Check if result is a DataFrame
                if not isinstance(result, pd.DataFrame):
                    error_msg = "Result is not a DataFrame"
                    error_details.append((name, error_msg))
                    sources_tried.append({"source": name, "status": "error", "error": error_msg})
                    self._update_stats(name, False)
                    continue

                # Handle empty DataFrame based on policy
                if result.empty:
                    if self.empty_data_policy == EmptyDataPolicy.RELAXED:
                        # RELAXED: Empty result is valid, return immediately
                        self._update_stats(name, True)
                        return ExecutionResult(
                            success=True,
                            data=result,
                            source=name,
                            error=None,
                            attempts=attempt,
                            error_details=error_details,
                            is_empty=True,
                            sources_tried=sources_tried + [{"source": name, "status": "success", "is_empty": True}],
                        )

                    elif self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT:
                        # BEST_EFFORT: Track empty result, continue trying other sources
                        if best_result is None:
                            best_result = result
                            best_source = name
                            best_is_empty = True
                        sources_tried.append({"source": name, "status": "success", "is_empty": True})
                        self._update_stats(name, True)
                        continue

                    else:  # STRICT (default)
                        # STRICT: Empty result is invalid, try next source
                        error_msg = "Empty DataFrame (STRICT policy)"
                        error_details.append((name, error_msg))
                        sources_tried.append({"source": name, "status": "error", "error": error_msg, "is_empty": True})
                        self._update_stats(name, False)
                        continue

                # Non-empty DataFrame - validate it
                if self._validate_result(result, is_empty_allowed=False):
                    self._update_stats(name, True)
                    return ExecutionResult(
                        success=True,
                        data=result,
                        source=name,
                        error=None,
                        attempts=attempt,
                        error_details=error_details,
                        is_empty=False,
                        sources_tried=sources_tried + [{"source": name, "status": "success", "rows": len(result)}],
                    )

                # Non-empty but invalid (missing columns or min_rows)
                error_msg = "Invalid result (missing required columns or min_rows)"
                error_details.append((name, error_msg))
                sources_tried.append({"source": name, "status": "error", "error": error_msg, "rows": len(result)})
                self._update_stats(name, False)

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                error_details.append((name, error_msg))
                sources_tried.append({"source": name, "status": "error", "error": error_msg})
                self._update_stats(name, False)

        # All providers processed - handle based on policy
        if self.empty_data_policy == EmptyDataPolicy.BEST_EFFORT and best_result is not None:
            # Return best available result (even if empty)
            return ExecutionResult(
                success=True,
                data=best_result,
                source=best_source,
                error=None,
                attempts=attempt,
                error_details=error_details,
                is_empty=best_is_empty,
                sources_tried=sources_tried,
            )

        # All providers failed or no valid result
        error_summary = "\n".join([f"  {source}: {error}" for source, error in error_details])
        return ExecutionResult(
            success=False,
            data=None,
            source=None,
            error=error_summary,
            attempts=attempt,
            error_details=error_details,
            is_empty=False,
            sources_tried=sources_tried,
        )


_FACTORY_DEFAULTS: dict[Any, tuple[list[str], list[str] | None]] = {}


def _register_factory_defaults(factory_class: Any, sources: list[str], columns: list[str] | None) -> None:
    """Register default sources and columns for a factory class."""
    _FACTORY_DEFAULTS[factory_class] = (sources, columns)


def _get_default_sources(factory_class: Any) -> list[str]:
    """Get default sources for a factory class."""
    if factory_class in _FACTORY_DEFAULTS:
        return _FACTORY_DEFAULTS[factory_class][0]
    return ["sina", "eastmoney"]


def _get_default_columns(factory_class: Any) -> list[str] | None:
    """Get default required columns for a factory class."""
    if factory_class in _FACTORY_DEFAULTS:
        return _FACTORY_DEFAULTS[factory_class][1]
    return None


def _create_provider_instance(factory_class: Any, source: str, **kwargs: Any) -> Any:
    """Create a provider instance from a factory class."""
    return factory_class.get_provider(source, **kwargs)


def create_router(
    factory_class: Any,
    method_name: str,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
    **kwargs: Any,
) -> MultiSourceRouter:
    """Generic router creation with consistent pattern.

    Args:
        factory_class: The factory class to use for creating providers
        method_name: The method name to call on providers
        sources: List of source names to try
        required_columns: Required columns in result
        min_rows: Minimum rows required for valid result
        **kwargs: Additional parameters passed to provider constructors

    Returns:
        MultiSourceRouter: Configured router
    """
    if sources is None:
        sources = _get_default_sources(factory_class)
    if required_columns is None:
        required_columns = _get_default_columns(factory_class)

    providers = []
    for source in sources:
        try:
            provider = _create_provider_instance(factory_class, source, **kwargs)
            providers.append((source, provider))
        except Exception as e:
            logger.warning(f"Failed to initialize provider '{source}': {e}")

    return MultiSourceRouter(
        providers,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_historical_router(
    symbol: str,
    interval: str = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: str = "none",
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for historical data with multiple sources."""
    from .historical import HistoricalDataFactory

    _register_factory_defaults(
        HistoricalDataFactory,
        ["sina", "lixinger", "eastmoney_direct", "eastmoney", "tencent", "netease"],
        ["timestamp", "open", "high", "low", "close", "volume"],
    )

    return create_router(
        HistoricalDataFactory,
        "get_hist_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )


def create_realtime_router(
    symbol: str | None = None,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for real-time data with multiple sources."""
    from .realtime import RealtimeDataFactory

    _register_factory_defaults(
        RealtimeDataFactory,
        ["sina", "eastmoney_direct", "eastmoney", "xueqiu"],
        ["symbol", "price", "timestamp"],
    )

    return create_router(
        RealtimeDataFactory,
        "get_realtime_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
        symbol=symbol,
    )


def create_financial_router(
    symbol: str,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for financial data with multiple sources."""
    from .financial import FinancialDataFactory

    _register_factory_defaults(
        FinancialDataFactory,
        ["sina", "eastmoney_direct", "lixinger"],
        None,
    )

    return create_router(
        FinancialDataFactory,
        "get_financial_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
        symbol=symbol,
    )


def create_northbound_router(
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for northbound capital data with multiple sources."""
    from .northbound import NorthboundFactory

    _register_factory_defaults(
        NorthboundFactory,
        ["sina", "eastmoney"],
        None,
    )

    return create_router(
        NorthboundFactory,
        "get_northbound_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_fundflow_router(
    symbol: str | None = None,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for fund flow data with multiple sources."""
    from .fundflow import FundFlowFactory

    _register_factory_defaults(
        FundFlowFactory,
        ["sina", "eastmoney"],
        None,
    )

    return create_router(
        FundFlowFactory,
        "get_fundflow_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
        symbol=symbol,
    )


def create_dragon_tiger_router(
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for dragon tiger list data with multiple sources."""
    from .lhb import DragonTigerFactory

    _register_factory_defaults(
        DragonTigerFactory,
        ["sina", "eastmoney"],
        None,
    )

    return create_router(
        DragonTigerFactory,
        "get_dragon_tiger_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_limit_up_down_router(
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for limit up/down data with multiple sources."""
    from .limitup import LimitUpDownFactory

    _register_factory_defaults(
        LimitUpDownFactory,
        ["sina", "eastmoney"],
        None,
    )

    return create_router(
        LimitUpDownFactory,
        "get_limit_up_down_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_block_deal_router(
    symbol: str | None = None,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for block deal data with multiple sources."""
    from .blockdeal import BlockDealFactory

    _register_factory_defaults(
        BlockDealFactory,
        ["sina", "eastmoney"],
        None,
    )

    return create_router(
        BlockDealFactory,
        "get_block_deal_data",
        sources=sources,
        required_columns=required_columns,
        min_rows=min_rows,
        symbol=symbol,
    )
