# news 模块数据字典

## 概览

- 数据源: ['unknown']
- 字段数: 0

## 字段列表

| 字段名 | 数据类型 | 推断类型 | 金额单位 | 空值率 | 示例值 |
|--------|---------|---------|---------|-------|--------|

## 方法列表

| 方法名 | 签名 |
|--------|------|
| add_field_aliases | `(df: pandas.core.frame.DataFrame, include_legacy: bool = True) -> pandas.core.frame.DataFrame` |
| apply_amount_conversion | `(df: pandas.core.frame.DataFrame, amount_fields: dict[str, str]) -> pandas.core.frame.DataFrame` |
| apply_data_filter | `(df: pandas.core.frame.DataFrame, columns: list | None = None, row_filter: dict[str, typing.Any] | None = None) -> pandas.core.frame.DataFrame` |
| apply_field_standardization | `(df: pandas.core.frame.DataFrame, field_types: dict[str, akshare_one.modules.field_naming.models.FieldType]) -> pandas.core.frame.DataFrame` |
| convert_amount_units | `(df: pandas.core.frame.DataFrame, amount_fields: dict[str, str]) -> pandas.core.frame.DataFrame` |
| create_empty_dataframe | `(columns: list) -> pandas.core.frame.DataFrame` |
| ensure_json_compatible | `(df: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame` |
| fetch_data | `() -> pandas.core.frame.DataFrame` |
| get_analyst_rank | `() -> pandas.core.frame.DataFrame` |
| get_data | `(apply_standardization: bool = True) -> pandas.core.frame.DataFrame` |
| get_data_type | `() -> str` |
| get_data_with_full_standardization | `(apply_field_validation: bool = True, field_types: dict[str, akshare_one.modules.field_naming.models.FieldType] | None = None, amount_fields: dict[str, str] | None = None) -> pandas.core.frame.DataFrame` |
| get_delay_minutes | `() -> int` |
| get_research_report | `(symbol: str) -> pandas.core.frame.DataFrame` |
| get_source_name | `() -> str` |
| get_update_frequency | `() -> str` |
| infer_amount_fields | `(df: pandas.core.frame.DataFrame) -> dict[str, str]` |
| infer_field_types | `(df: pandas.core.frame.DataFrame) -> dict[str, akshare_one.modules.field_naming.models.FieldType]` |
| map_source_fields | `(df: pandas.core.frame.DataFrame, source: str) -> pandas.core.frame.DataFrame` |
| replace_nan_with_none | `(value: Any) -> Any` |
| standardize_data | `(df: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame` |
| standardize_dataframe | `(df: pandas.core.frame.DataFrame, field_types: dict[str, akshare_one.modules.field_naming.models.FieldType] | None = None, amount_fields: dict[str, str] | None = None) -> pandas.core.frame.DataFrame` |
| standardize_date | `(date_value: Any) -> str | None` |
| standardize_date_field | `(series: pandas.core.series.Series, format: str = '%Y-%m-%d') -> pandas.core.series.Series` |
| standardize_field_names | `(df: pandas.core.frame.DataFrame, field_types: dict[str, akshare_one.modules.field_naming.models.FieldType]) -> pandas.core.frame.DataFrame` |
| standardize_numeric | `(value: Any, default: float | None = None) -> float | None` |
| standardize_symbol | `(symbol: str) -> str` |
| standardize_timestamp_field | `(series: pandas.core.series.Series, timezone: str = 'Asia/Shanghai') -> pandas.core.series.Series` |
| validate_date | `(date_str: str, param_name: str = 'date') -> None` |
| validate_date_range | `(start_date: str, end_date: str) -> None` |
| validate_symbol | `(symbol: str) -> None` |
| validate_symbol_optional | `(symbol: str | None) -> None` |