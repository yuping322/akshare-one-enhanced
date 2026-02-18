"""
Base provider class for all market data providers.

This module provides the foundation for implementing market data providers
with built-in JSON compatibility, parameter validation, and metadata support.
"""

import contextlib
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from ..logging_config import get_logger, log_api_request, log_data_quality
from .field_naming import FieldAliasManager, FieldMapper, FieldStandardizer, FieldType, NamingRules
from .field_naming.models import FIELD_EQUIVALENTS
from .field_naming.unit_converter import UnitConverter


class BaseProvider(ABC):
    """
    Abstract base class for all market data providers.

    Provides common functionality for:
    - Parameter validation (dates, symbols)
    - JSON compatibility (handling NaN/Infinity)
    - Metadata properties for data sources
    - Data standardization utilities
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the provider with configuration parameters.

        Args:
            **kwargs: Provider-specific configuration parameters
                     - enable_deprecation_warnings: Enable/disable deprecation warnings (default: True)
        """
        self.kwargs = kwargs

        # Initialize logger
        self.logger = get_logger(self.__class__.__module__)

        # Initialize standardization components
        self.field_standardizer = FieldStandardizer(NamingRules())
        self.field_mapper = FieldMapper(self._get_mapping_config_path())
        self.unit_converter = UnitConverter()
        self.alias_manager = FieldAliasManager(
            self._get_alias_config(),
            enable_warnings=kwargs.get("enable_deprecation_warnings", True),
        )

    def _get_mapping_config_path(self) -> str | None:
        """
        Get the path to the field mapping configuration.

        Subclasses can override this to provide custom mapping configurations.

        Returns:
            Path to mapping config directory, or None to use default
        """
        return None

    def _get_alias_config(self) -> dict[str, str]:
        """
        Get the field alias configuration.

        Subclasses can override this to provide custom alias configurations.

        Returns:
            Dictionary mapping old field names to new field names
        """
        return {}

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Return metadata about the data source.

        Returns:
            dict: Metadata including source, data_type, update_frequency, delay_minutes
        """
        return {
            "source": self.get_source_name(),
            "data_type": self.get_data_type(),
            "update_frequency": self.get_update_frequency(),
            "delay_minutes": self.get_delay_minutes(),
        }

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the data source (e.g., 'eastmoney', 'official')"""
        pass

    @abstractmethod
    def get_data_type(self) -> str:
        """Return the type of data (e.g., 'fundflow', 'disclosure', 'northbound')"""
        pass

    def get_update_frequency(self) -> str:
        """
        Return the update frequency of the data.

        Returns:
            str: One of 'realtime', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
        """
        return "daily"

    def get_delay_minutes(self) -> int:
        """
        Return the data delay in minutes.

        Returns:
            int: Delay in minutes (0 for realtime)
        """
        return 0

    # Parameter Validation Methods

    @staticmethod
    def validate_symbol(symbol: str) -> None:
        """
        Validate stock symbol format.

        Args:
            symbol: Stock symbol (e.g., '600000', '000001')

        Raises:
            ValueError: If symbol format is invalid
        """
        if not symbol:
            raise ValueError("Symbol cannot be empty")

        # Chinese A-share symbols are 6 digits
        if not re.match(r"^\d{6}$", symbol):
            raise ValueError(
                f"Invalid symbol format: {symbol}. Expected 6-digit stock code (e.g., '600000')"
            )

    @staticmethod
    def validate_date(date_str: str, param_name: str = "date") -> None:
        """
        Validate date format.

        Args:
            date_str: Date string in YYYY-MM-DD format
            param_name: Parameter name for error messages

        Raises:
            ValueError: If date format is invalid
        """
        if not date_str:
            raise ValueError(f"{param_name} cannot be empty")

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Invalid {param_name} format: {date_str}. Expected YYYY-MM-DD format. Error: {e}"
            ) from None

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> None:
        """
        Validate date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Raises:
            ValueError: If date range is invalid
        """
        BaseProvider.validate_date(start_date, "start_date")
        BaseProvider.validate_date(end_date, "end_date")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start > end:
            raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    @staticmethod
    def validate_symbol_optional(symbol: str | None) -> None:
        """
        Validate optional symbol parameter.

        Args:
            symbol: Stock symbol or None

        Raises:
            ValueError: If symbol format is invalid (when not None)
        """
        if symbol is not None:
            BaseProvider.validate_symbol(symbol)

    # JSON Compatibility Methods

    @staticmethod
    def ensure_json_compatible(df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure DataFrame is JSON-compatible by handling NaN/Infinity and data types.

        This method:
        1. Replaces NaN with None (JSON null)
        2. Replaces Infinity/-Infinity with None
        3. Converts datetime columns to string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        4. Ensures symbol columns are strings with leading zeros preserved

        Args:
            df: Input DataFrame

        Returns:
            pd.DataFrame: JSON-compatible DataFrame
        """
        if df.empty:
            return df

        df = df.copy()

        # 1. Handle NaN and Infinity in numeric columns
        for col in df.select_dtypes(include=["float64", "float32", "float16"]).columns:
            # Replace Infinity with NaN first
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            # Replace NaN with None using replace dict (this works correctly)
            df[col] = df[col].replace({np.nan: None})

        # 2. Convert datetime columns to strings
        for col in df.select_dtypes(include=["datetime64"]).columns:
            # Check if the datetime has non-zero time component
            has_time = (
                (df[col].dt.hour != 0).any()
                or (df[col].dt.minute != 0).any()
                or (df[col].dt.second != 0).any()
            )
            if has_time:
                # Has time component, use full format
                df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Date only, use date format
                df[col] = df[col].dt.strftime("%Y-%m-%d")

        # 3. Ensure symbol columns are strings with leading zeros
        symbol_columns = ["symbol", "stock_code", "code"]
        for col in symbol_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.zfill(6)

        return df

    @staticmethod
    def replace_nan_with_none(value: Any) -> Any:
        """
        Replace NaN/Infinity values with None for JSON compatibility.

        Args:
            value: Any value that might be NaN or Infinity

        Returns:
            Original value or None if it was NaN/Infinity
        """
        if pd.isna(value):
            return None
        if isinstance(value, float) and (np.isinf(value) or np.isnan(value)):
            return None
        return value

    @staticmethod
    def create_empty_dataframe(columns: list) -> pd.DataFrame:
        """
        Create an empty DataFrame with specified columns.

        This is useful for returning consistent structure even when no data is available.

        Args:
            columns: List of column names

        Returns:
            pd.DataFrame: Empty DataFrame with specified columns
        """
        return pd.DataFrame(columns=columns)

    # Data Standardization Methods

    @staticmethod
    def standardize_symbol(symbol: str) -> str:
        """
        Standardize symbol format (ensure 6 digits with leading zeros).

        Args:
            symbol: Stock symbol

        Returns:
            str: Standardized symbol (6 digits)
        """
        return str(symbol).zfill(6)

    @staticmethod
    def standardize_date(date_value: Any) -> str | None:
        """
        Standardize date to YYYY-MM-DD format.

        Args:
            date_value: Date value (string, datetime, or timestamp)

        Returns:
            str: Date in YYYY-MM-DD format, or None if invalid
        """
        if pd.isna(date_value):
            return None

        try:
            if isinstance(date_value, str):
                # Try to parse string date
                dt = pd.to_datetime(date_value)
            else:
                dt = pd.to_datetime(date_value)

            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    @staticmethod
    def standardize_numeric(value: Any, default: float | None = None) -> float | None:
        """
        Standardize numeric value, handling NaN and Infinity.

        Args:
            value: Numeric value
            default: Default value to return if conversion fails

        Returns:
            float or None: Standardized numeric value
        """
        try:
            num_value = float(value)
            if np.isnan(num_value) or np.isinf(num_value):
                return default
            return num_value
        except (ValueError, TypeError):
            return default

    # Field Naming Standardization Methods

    def standardize_field_names(
        self, df: pd.DataFrame, field_types: dict[str, FieldType]
    ) -> pd.DataFrame:
        """
        Standardize DataFrame field names according to naming conventions.

        Args:
            df: Original DataFrame
            field_types: Mapping of field names to their types

        Returns:
            DataFrame with standardized field names
        """
        return self.field_standardizer.standardize_dataframe(df, field_types)

    def map_source_fields(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        Map source data fields to standard fields.

        Args:
            df: Original DataFrame with source field names
            source: Data source name (e.g., 'eastmoney')

        Returns:
            DataFrame with mapped field names
        """
        # Get module name from class module path
        module_name = self.__class__.__module__.split(".")[-2]
        return self.field_mapper.map_fields(df, source, module_name)

    def convert_amount_units(self, df: pd.DataFrame, amount_fields: dict[str, str]) -> pd.DataFrame:
        """
        Convert amount field units to yuan (元).

        Args:
            df: DataFrame with amount fields
            amount_fields: Mapping of field names to their source units
                          e.g., {'balance': 'yi_yuan', 'amount': 'wan_yuan'}

        Returns:
            DataFrame with converted amount units (all in yuan)
        """
        return self.unit_converter.convert_dataframe_amounts(df, amount_fields)

    def add_field_aliases(self, df: pd.DataFrame, include_legacy: bool = True) -> pd.DataFrame:
        """
        Add field aliases for backward compatibility.

        Args:
            df: Standardized DataFrame
            include_legacy: Whether to include legacy field names as aliases

        Returns:
            DataFrame with alias fields added
        """
        if include_legacy:
            return self.alias_manager.add_aliases_to_dataframe(df)
        return df

    def standardize_date_field(self, series: pd.Series, format: str = "%Y-%m-%d") -> pd.Series:
        """
        Standardize date field format.

        Args:
            series: Date data series
            format: Target date format (default: YYYY-MM-DD)

        Returns:
            Formatted date series
        """
        return pd.to_datetime(series).dt.strftime(format)

    def standardize_timestamp_field(
        self, series: pd.Series, timezone: str = "Asia/Shanghai"
    ) -> pd.Series:
        """
        Standardize timestamp field with timezone awareness.

        Args:
            series: Timestamp data series
            timezone: Timezone to localize to (default: Asia/Shanghai)

        Returns:
            Timezone-aware timestamp series
        """
        return pd.to_datetime(series).dt.tz_localize(timezone)

    # Abstract Methods (to be implemented by subclasses)

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from the data source.

        Returns:
            pd.DataFrame: Raw data from the source
        """
        pass

    def fetch_data_with_logging(self) -> pd.DataFrame:
        """
        Fetch data with automatic logging and metrics collection.

        This method wraps fetch_data() to add:
        - Request timing
        - Structured logging
        - Error tracking

        Returns:
            pd.DataFrame: Raw data from the source

        Raises:
            Exception: Any exception from fetch_data()
        """
        start_time = time.time()
        source_name = self.get_source_name()
        data_type = self.get_data_type()

        self.logger.debug(
            f"Starting data fetch from {source_name}",
            extra={
                "context": {"source": source_name, "data_type": data_type, "action": "fetch_start"}
            },
        )

        try:
            df = self.fetch_data()

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source=source_name,
                endpoint=data_type,
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            if df.empty:
                log_data_quality(
                    logger=self.logger,
                    source=source_name,
                    data_type=data_type,
                    issue="empty_dataframe",
                    details={"message": "Returned empty DataFrame"},
                )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source=source_name,
                endpoint=data_type,
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(
                f"Data fetch failed from {source_name}",
                extra={
                    "context": {
                        "source": source_name,
                        "data_type": data_type,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "duration_ms": round(duration_ms, 2),
                    }
                },
                exc_info=True,
            )

            raise

    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize data format (field names, types, etc.).

        This method should be overridden by subclasses to implement
        specific standardization logic including field type mapping.

        Args:
            df: Raw DataFrame (after field mapping)

        Returns:
            pd.DataFrame: Standardized DataFrame
        """
        # Default implementation - subclasses should override with specific field types
        return df

    def apply_field_standardization(
        self, df: pd.DataFrame, field_types: dict[str, FieldType]
    ) -> pd.DataFrame:
        """
        Apply field name standardization based on field types.

        Args:
            df: DataFrame with standard field names
            field_types: Mapping of field names to their types for validation

        Returns:
            DataFrame with validated field names
        """
        return self.field_standardizer.standardize_dataframe(df, field_types)

    def apply_amount_conversion(
        self, df: pd.DataFrame, amount_fields: dict[str, str]
    ) -> pd.DataFrame:
        """
        Apply amount unit conversion.

        Args:
            df: DataFrame with amount fields
            amount_fields: Mapping of field names to their source units
                          e.g., {'balance': 'yi_yuan', 'amount': 'wan_yuan'}

        Returns:
            DataFrame with amounts converted to yuan
        """
        return self.unit_converter.convert_dataframe_amounts(df, amount_fields)

    def infer_field_types(self, df: pd.DataFrame) -> dict[str, FieldType]:
        """
        根据字段名称自动推断字段类型。

        优先从配置文件加载，如果没有配置则基于 FIELD_EQUIVALENTS 字典和字段命名规则推断类型。

        Args:
            df: DataFrame with field names

        Returns:
            Mapping of field names to their inferred types
        """
        from .config import get_field_mapping_config

        module_name = self.__class__.__module__.split(".")[-2]

        config_field_types = get_field_mapping_config().get_field_types(module_name)

        if config_field_types:
            return {k: v for k, v in config_field_types.items() if k in df.columns}

        field_types = {}

        for col in df.columns:
            col_lower = col.lower()
            inferred_type = None

            for standard_field, equivalents in FIELD_EQUIVALENTS.items():
                if col in equivalents or col_lower in [e.lower() for e in equivalents]:
                    inferred_type = self._get_field_type_from_standard_name(standard_field)
                    break

            if inferred_type is None:
                inferred_type = self._infer_type_from_name(col)

            if inferred_type is not None:
                field_types[col] = inferred_type

        return field_types

    def infer_amount_fields(self, df: pd.DataFrame) -> dict[str, str]:
        """
        根据字段名称自动推断金额字段的单位。

        优先从配置文件加载，如果没有配置则根据字段名称推断。

        Args:
            df: DataFrame with field names

        Returns:
            Mapping of field names to their source units
        """
        from .config import get_field_mapping_config

        module_name = self.__class__.__module__.split(".")[-2]

        config_amount_fields = get_field_mapping_config().get_amount_fields(module_name)

        if config_amount_fields:
            return {k: v for k, v in config_amount_fields.items() if k in df.columns}

        amount_fields = {}

        for col in df.columns:
            col_lower = col.lower()

            if any(
                kw in col_lower
                for kw in ["amount", "额", "金额", "value", "市值", "balance", "余额"]
            ):
                unit = self._infer_unit_from_name(col)
                if unit:
                    amount_fields[col] = unit

        return amount_fields

    def _get_field_type_from_standard_name(self, standard_name: str) -> FieldType | None:
        """根据标准字段名获取字段类型"""
        type_mapping = {
            "date": FieldType.DATE,
            "timestamp": FieldType.TIMESTAMP,
            "time": FieldType.TIME,
            "event_date": FieldType.EVENT_DATE,
            "duration": FieldType.DURATION,
            "amount": FieldType.AMOUNT,
            "balance": FieldType.BALANCE,
            "value": FieldType.VALUE,
            "market_cap": FieldType.VALUE,
            "float_market_cap": FieldType.VALUE,
            "net_flow": FieldType.NET_FLOW,
            "net_flow_rate": FieldType.RATE,
            "net_buy": FieldType.NET_FLOW,
            "buy_amount": FieldType.AMOUNT,
            "sell_amount": FieldType.AMOUNT,
            "holding_value": FieldType.VALUE,
            "close": FieldType.AMOUNT,
            "open": FieldType.AMOUNT,
            "high": FieldType.AMOUNT,
            "low": FieldType.AMOUNT,
            "limit_up": FieldType.AMOUNT,
            "limit_down": FieldType.AMOUNT,
            "avg_price": FieldType.AMOUNT,
            "issue_price": FieldType.AMOUNT,
            "change_pct": FieldType.RATE,
            "change_amount": FieldType.AMOUNT,
            "amplitude": FieldType.RATE,
            "rate": FieldType.RATE,
            "ratio": FieldType.RATIO,
            "pe_ratio": FieldType.RATIO,
            "pb_ratio": FieldType.RATIO,
            "turnover_rate": FieldType.RATE,
            "pledge_ratio": FieldType.RATE,
            "symbol": FieldType.SYMBOL,
            "name": FieldType.NAME,
            "code": FieldType.CODE,
            "market": FieldType.MARKET,
            "rank": FieldType.RANK,
            "industry": FieldType.TYPE,
            "count": FieldType.COUNT,
            "volume": FieldType.VOLUME,
            "shares": FieldType.SHARES,
            "total_shares": FieldType.SHARES,
            "pledge_shares": FieldType.SHARES,
            "boolean": FieldType.BOOLEAN,
            "type": FieldType.TYPE,
            "status": FieldType.TYPE,
        }
        return type_mapping.get(standard_name)

    def _infer_type_from_name(self, field_name: str) -> FieldType | None:
        """根据字段名称模式推断类型"""
        name_lower = field_name.lower()

        if any(kw in name_lower for kw in ["date", "日期", "时间", "time", "year", "month", "day"]):
            if "timestamp" in name_lower or "时间戳" in field_name:
                return FieldType.TIMESTAMP
            return FieldType.DATE

        if any(kw in name_lower for kw in ["symbol", "code", "代码", "编号"]):
            return FieldType.SYMBOL

        if any(kw in name_lower for kw in ["name", "名称", "标题", "title"]):
            return FieldType.NAME

        if any(kw in name_lower for kw in ["price", "价", "close", "open", "high", "low"]):
            return FieldType.AMOUNT

        if any(kw in name_lower for kw in ["rate", "ratio", "pct", "percent", "率", "比"]):
            return FieldType.RATE

        if any(
            kw in name_lower for kw in ["amount", "额", "金额", "value", "市值", "balance", "余额"]
        ):
            return FieldType.AMOUNT

        if any(kw in name_lower for kw in ["volume", "量", "shares", "股", "count", "数"]):
            return FieldType.VOLUME

        if any(kw in name_lower for kw in ["market", "市场", "exchange", "交易所"]):
            return FieldType.MARKET

        if any(kw in name_lower for kw in ["type", "类型", "status", "状态", "category"]):
            return FieldType.TYPE

        if any(kw in name_lower for kw in ["rank", "排名", "排序"]):
            return FieldType.RANK

        return None

    def _infer_unit_from_name(self, field_name: str) -> str | None:
        """根据字段名称推断金额单位"""
        name_lower = field_name.lower()

        if "亿" in field_name or "yi" in name_lower:
            return "yi_yuan"

        if "万" in field_name or "wan" in name_lower:
            return "wan_yuan"

        if "千" in field_name and "万" not in field_name:
            return "qian_yuan"

        return "yuan"

    def standardize_dataframe(
        self,
        df: pd.DataFrame,
        field_types: dict[str, FieldType] | None = None,
        amount_fields: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """
        对 DataFrame 应用完整的标准化流程。

        这是一个统一入口方法，自动推断字段类型和单位。

        Args:
            df: 原始 DataFrame
            field_types: 字段类型映射（可选，自动推断）
            amount_fields: 金额字段单位映射（可选，自动推断）

        Returns:
            标准化后的 DataFrame
        """
        if df.empty:
            return df

        if field_types is None:
            field_types = self.infer_field_types(df)

        if amount_fields is None:
            amount_fields = self.infer_amount_fields(df)

        if field_types:
            df = self.apply_field_standardization(df, field_types)

        if amount_fields:
            df = self.apply_amount_conversion(df, amount_fields)

        return df

    def get_data(self, apply_standardization: bool = True) -> pd.DataFrame:
        """
        Main method to fetch and standardize data with logging.

        This method orchestrates the data fetching and standardization process:
        1. Fetch raw data (with logging)
        2. Apply field mapping from source fields to standard fields
        3. Apply automatic field type inference and standardization
        4. Apply amount unit conversion
        5. Ensure JSON compatibility

        Args:
            apply_standardization: Whether to apply full standardization pipeline.
                                 Set to False to bypass standardization and return raw data.

        Returns:
            pd.DataFrame: Standardized, JSON-compatible data
        """
        raw_df = self.fetch_data_with_logging()

        if not apply_standardization:
            return self.ensure_json_compatible(raw_df)

        source_name = self.get_source_name()

        mapped_df = self.map_source_fields(raw_df, source_name)

        standardized_df = self.standardize_dataframe(mapped_df)

        standardized_df = self.standardize_data(standardized_df)

        return self.ensure_json_compatible(standardized_df)

    def apply_data_filter(
        self,
        df: pd.DataFrame,
        columns: list | None = None,
        row_filter: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """
        通用数据过滤方法（行列过滤），用于 LLM Skills 数据筛选。

        Args:
            df: 原始 DataFrame
            columns: 需要保留的列名列表，为 None 时保留所有列
            row_filter: 行过滤配置字典，支持：
                - top_n: 返回前 N 行，如 {"top_n": 10}
                - sample: 随机采样比例 (0-1)，如 {"sample": 0.3}
                - query: pandas query 表达式，如 {"query": "pct_change > 5"}
                - sort_by: 排序字段，如 {"sort_by": "pct_change"}
                - ascending: 是否升序排序，默认 False（降序），如 {"ascending": True}

        Returns:
            过滤后的 DataFrame

        Example:
            >>> df = provider.get_data()
            >>> # 列过滤：只保留核心字段
            >>> df = provider.apply_data_filter(df, columns=["date", "symbol", "close"])
            >>> # 行过滤：只看前10条
            >>> df = provider.apply_data_filter(df, row_filter={"top_n": 10})
            >>> # 排序后取前N条
            >>> df = provider.apply_data_filter(df, row_filter={"sort_by": "pct_change", "top_n": 10})
            >>> # 组合过滤
            >>> df = provider.apply_data_filter(
            ...     df,
            ...     columns=["date", "close"],
            ...     row_filter={"query": "close > 10", "top_n": 5}
            ... )
        """
        if df.empty:
            return df

        df = df.copy()

        # 行过滤（先执行排序，再执行其他过滤）
        if row_filter:
            # 排序（优先执行）
            if "sort_by" in row_filter:
                sort_col = row_filter["sort_by"]
                if sort_col in df.columns:
                    ascending = row_filter.get("ascending", False)
                    df = df.sort_values(by=sort_col, ascending=ascending).reset_index(drop=True)

            # 条件过滤
            if "query" in row_filter:
                with contextlib.suppress(Exception):
                    df = df.query(row_filter["query"]).reset_index(drop=True)

            # 采样
            if "sample" in row_filter:
                frac = row_filter["sample"]
                if 0 < frac <= 1:
                    df = df.sample(frac=frac, random_state=42).reset_index(drop=True)

            # 截取前N条（最后执行）
            if "top_n" in row_filter:
                df = df.head(row_filter["top_n"])

        # 列过滤（最后执行，减少数据量）
        if columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df

    def get_data_with_full_standardization(
        self,
        apply_field_validation: bool = True,
        field_types: dict[str, FieldType] | None = None,
        amount_fields: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """
        Enhanced method to fetch and apply full standardization pipeline.

        This method applies a complete standardization pipeline:
        1. Fetch raw data
        2. Apply field mapping from source fields to standard fields
        3. Apply field name standardization and validation (auto-inferred if not provided)
        4. Apply amount unit conversion (auto-inferred if not provided)
        5. Ensure JSON compatibility

        Args:
            apply_field_validation: Whether to apply field name validation
            field_types: Mapping of field names to their types for validation
                        (auto-inferred if None)
            amount_fields: Mapping of field names to their source units for conversion
                          e.g., {'balance': 'yi_yuan', 'amount': 'wan_yuan'}
                          (auto-inferred if None)

        Returns:
            pd.DataFrame: Fully standardized, JSON-compatible data
        """
        raw_df = self.fetch_data()

        source_name = self.get_source_name()

        mapped_df = self.map_source_fields(raw_df, source_name)

        if apply_field_validation:
            if field_types is None:
                field_types = self.infer_field_types(mapped_df)
            validated_df = self.apply_field_standardization(mapped_df, field_types)
        else:
            validated_df = mapped_df

        if amount_fields is None:
            amount_fields = self.infer_amount_fields(validated_df)

        if amount_fields:
            converted_df = self.apply_amount_conversion(validated_df, amount_fields)
        else:
            converted_df = validated_df

        final_df = self.standardize_data(converted_df)

        return self.ensure_json_compatible(final_df)
