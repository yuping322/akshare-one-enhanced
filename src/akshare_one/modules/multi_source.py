"""Multi-source data provider with automatic failover.

This module provides a router that automatically tries multiple data sources
and falls back to the next one if the current source fails.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ExecutionResult:
    """结果包装类，用于跟踪执行过程"""

    success: bool
    data: pd.DataFrame | None
    source: str | None
    error: str | None
    attempts: int
    error_details: list[tuple[str, str]] = None  # [(source, error_msg), ...]

    def __post_init__(self) -> None:
        if self.error_details is None:
            self.error_details = []


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
    ) -> None:
        """Initialize the router with a list of providers.

        Args:
            providers: List of (name, provider_instance) tuples, in priority order
            enable_logging: Whether to log failover events
            required_columns: List of required columns in result DataFrame
            min_rows: Minimum number of rows required for valid result
        """
        self.providers = providers
        self.enable_logging = enable_logging
        self.required_columns = required_columns or []
        self.min_rows = min_rows
        self.execution_stats: dict[str, dict[str, int]] = {}  # Track success/failure per source

    def _validate_result(self, result: Any) -> bool:
        """Validate if result meets quality requirements.

        Args:
            result: Result to validate

        Returns:
            bool: True if result is valid, False otherwise
        """
        if result is None:
            return False

        if not isinstance(result, pd.DataFrame):
            return False

        if result.empty:
            return False

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

    def _update_stats(self, source: str, success: bool) -> None:
        """Update execution statistics for a source.

        Args:
            source: Source name
            success: Whether execution was successful
        """
        if source not in self.execution_stats:
            self.execution_stats[source] = {"success": 0, "failure": 0}

        if success:
            self.execution_stats[source]["success"] += 1
        else:
            self.execution_stats[source]["failure"] += 1

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
            ValueError: If all providers fail
        """
        error_details: list[tuple[str, str]] = []
        successful_source = None

        for name, provider in self.providers:
            try:
                method = getattr(provider, method_name)
                result = method(*args, **kwargs)

                # Validate result
                if self._validate_result(result):
                    self._update_stats(name, True)
                    if self.enable_logging and error_details:
                        logger.info(
                            f"Successfully fetched data from '{name}' after "
                            f"{len(error_details)} failed attempt(s)"
                        )
                    successful_source = name
                    return result

                if self.enable_logging:
                    logger.warning(
                        f"Provider '{name}' returned invalid result for '{method_name}' "
                        f"(empty or missing required columns)"
                    )
                error_details.append((name, "Invalid result (empty or missing columns)"))
                self._update_stats(name, False)

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                error_details.append((name, error_msg))
                self._update_stats(name, False)
                if self.enable_logging:
                    logger.warning(
                        f"Provider '{name}' failed for '{method_name}': {error_msg}"
                    )
                continue

        # All providers failed
        error_summary = "\n".join(
            [f"  {source}: {error}" for source, error in error_details]
        )
        raise ValueError(
            f"All data sources failed for '{method_name}':\n{error_summary}"
        )

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
            ValueError: If all providers fail
        """
        error_details: list[tuple[str, str]] = []

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
                    error_msg = (
                        f"Provider has neither '{primary_method}' nor '{fallback_method}'"
                    )
                    error_details.append((name, error_msg))
                    self._update_stats(name, False)
                    raise AttributeError(error_msg)

                method_func = getattr(provider, method)
                result = method_func(*args, **kwargs)

                if self._validate_result(result):
                    self._update_stats(name, True)
                    return result

                error_msg = "Invalid result (empty or missing columns)"
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

        # All providers failed
        error_summary = "\n".join(
            [f"  {source}: {error}" for source, error in error_details]
        )
        raise ValueError(
            f"All providers failed for '{primary_method}' (or '{fallback_method}'):\n{error_summary}"
        )

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
        """
        error_details: list[tuple[str, str]] = []
        attempt = 0

        for name, provider in self.providers:
            attempt += 1
            try:
                method = getattr(provider, method_name)
                result = method(*args, **kwargs)

                if self._validate_result(result):
                    self._update_stats(name, True)
                    return ExecutionResult(
                        success=True,
                        data=result,
                        source=name,
                        error=None,
                        attempts=attempt,
                        error_details=error_details,
                    )

                error_msg = "Invalid result (empty or missing columns)"
                error_details.append((name, error_msg))
                self._update_stats(name, False)

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                error_details.append((name, error_msg))
                self._update_stats(name, False)

        # All providers failed
        error_summary = "\n".join(
            [f"  {source}: {error}" for source, error in error_details]
        )
        return ExecutionResult(
            success=False,
            data=None,
            source=None,
            error=error_summary,
            attempts=attempt,
            error_details=error_details,
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
    """Create a router for historical data with multiple sources.

    Args:
        symbol: Stock symbol
        interval: Time interval
        interval_multiplier: Interval multiplier
        start_date: Start date
        end_date: End date
        adjust: Adjustment type
        sources: List of source names to try (default: ["eastmoney_direct", "eastmoney", "sina"])
        required_columns: Required columns in result
        min_rows: Minimum rows required for valid result

    Returns:
        MultiSourceRouter: Configured router
    """
    from .historical.factory import HistoricalDataFactory

    if sources is None:
        sources = ["eastmoney_direct", "eastmoney", "sina", "tencent", "netease"]

    if required_columns is None:
        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]

    providers = []
    kwargs = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }

    for source in sources:
        try:
            provider = HistoricalDataFactory.get_provider(source, **kwargs)
            providers.append((source, provider))
        except Exception as e:
            logger.warning(f"Failed to initialize provider '{source}': {e}")

    return MultiSourceRouter(
        providers,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_realtime_router(
    symbol: str | None = None,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for real-time data with multiple sources.

    Args:
        symbol: Stock symbol
        sources: List of source names to try (default: ["eastmoney_direct", "eastmoney", "xueqiu"])
        required_columns: Required columns in result
        min_rows: Minimum rows required for valid result

    Returns:
        MultiSourceRouter: Configured router
    """
    from .realtime.factory import RealtimeDataFactory

    if sources is None:
        sources = ["eastmoney_direct", "eastmoney", "xueqiu"]

    if required_columns is None:
        required_columns = ["symbol", "price", "timestamp"]

    providers = []

    for source in sources:
        try:
            provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logger.warning(f"Failed to initialize provider '{source}': {e}")

    return MultiSourceRouter(
        providers,
        required_columns=required_columns,
        min_rows=min_rows,
    )


def create_financial_router(
    symbol: str,
    sources: list[str] | None = None,
    required_columns: list[str] | None = None,
    min_rows: int = 1,
) -> MultiSourceRouter:
    """Create a router for financial data with multiple sources.

    Args:
        symbol: Stock symbol
        sources: List of source names to try (default: ["eastmoney_direct", "sina"])
        required_columns: Required columns in result
        min_rows: Minimum rows required for valid result

    Returns:
        MultiSourceRouter: Configured router
    """
    from .financial.factory import FinancialDataFactory

    if sources is None:
        sources = ["eastmoney_direct", "sina"]

    providers = []

    for source in sources:
        try:
            provider = FinancialDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logger.warning(f"Failed to initialize provider '{source}': {e}")

    return MultiSourceRouter(
        providers,
        required_columns=required_columns,
        min_rows=min_rows,
    )
