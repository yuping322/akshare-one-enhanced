# API Contract: [API_NAME]

## Overview

**API Function**: `[function_name]`

**Purpose**: [Brief description of what this API does]

**Module**: `[module_path]`

**Data Sources**: [List supported data sources]

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response. These are the contract fields that consumers can rely on.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `[field1]` | `[type]` | `[unit]` | `[description]` | `[example_value]` |
| `[field2]` | `[type]` | `[unit]` | `[description]` | `[example_value]` |

### Field Types

- `string`: Text/string data
- `float`: Floating-point numeric data
- `int`: Integer numeric data
- `datetime`: Date/time in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `boolean`: True/false values

### Units

- `yuan`: Chinese Yuan (元)
- `shares`: Number of shares (股)
- `hands`: Trading hands (手, 1 hand = 100 shares)
- `percent`: Percentage (%)
- `ratio`: Ratio (0-1 range)
- `timestamp`: Unix timestamp or datetime string

## Optional Fields

The following fields MAY be present depending on the data source or parameters.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `[field]` | `[type]` | `[unit]` | `[description]` | `[source/condition]` |

## Data Source Mapping

### Source: `[source_name]`

**Original Fields** (from upstream API):
- `[original_field1]` → `[standardized_field1]`
- `[original_field2]` → `[standardized_field2]`

**Field Transformations**:
- `[description of any transformations, unit conversions, etc.]`

## Update Frequency

- **Realtime**: [If applicable, describe realtime update frequency]
- **Historical**: [Describe historical data availability]
- **Delayed**: [If applicable, describe delay]

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `[param]` | `[type]` | `[yes/no]` | `[default]` | `[description]` |

## Example Usage

```python
from akshare_one import [function_name]

# Basic usage
df = [function_name]([required_params])

# With optional parameters
df = [function_name](
    [required_params],
    [optional_param]=[value]
)

# With column filtering
df = [function_name](
    [required_params],
    columns=['[field1]', '[field2]']
)
```

## Example Response

```python
# Example DataFrame structure
   [field1]   [field2]  [field3]  ...
0  [value1]   [value2]  [value3]  ...
1  [value1]   [value2]  [value3]  ...
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present
2. **Type Validation**: Fields MUST match their declared types
3. **Value Ranges**:
   - `[field]`: [valid range or constraints]
   - `[field]`: [valid range or constraints]

4. **Consistency Rules**:
   - [Any consistency rules between fields, e.g., high >= low]

## Error Handling

- **Empty DataFrame**: Returned when no data is available
- **Exception Handling**: [Describe how errors are handled]
- **Fallback Behavior**: [Describe any fallback mechanisms]

## Contract Stability

**Stability Level**: `[stable/experimental/deprecated]`

**Version**: `[version if applicable]`

**Breaking Changes**:
- [List any breaking changes or migration notes]

## Related APIs

- `[related_api1]`: [relationship description]
- `[related_api2]`: [relationship description]

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::Test[APIName]Contract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- Cross-source schema consistency

## Notes

[Any additional notes, caveats, or important information]