# API Contract: get_options_expirations

## Overview

**API Function**: `get_options_expirations`

**Purpose**: Get available expiration dates for options on an underlying asset.

**Module**: `akshare_one.modules.options`

**Data Sources**: `sina` (uses eastmoney APIs)

## Minimum Field Set (Required Fields)

This API returns a list of strings, not a DataFrame.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| (return value) | list[str] | - | Available expiration dates | `['2月', '3月', '6月']` |

## Data Source Mapping

### Source: `sina`

**Process**:
- Fetches all options via `option_current_em`
- Filters by underlying symbol pattern
- Extracts expiration from option names (e.g., '300ETF沽2月4288A' → '2月')
- Returns unique sorted expirations

## Update Frequency

- **On-demand**: Calculated when requested
- Based on currently listed options

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `underlying_symbol` | string | yes | - | Underlying asset symbol (e.g., '510300') |
| `source` | string | no | `sina` | Data source |

## Example Usage

```python
from akshare_one import get_options_expirations

# Get available expirations for 300ETF options
expirations = get_options_expirations(underlying_symbol="510300")

# Returns list like: ['2月', '3月', '6月', '9月', '12月']
print(expirations)
```

## Example Response

```python
['2月', '3月', '6月', '12月']
```

## Validation Rules

1. **Return Type**: Must be list of strings
2. **Format**: Expiration strings in Chinese month format ('X月')
3. **Non-empty**: Should return at least one expiration if underlying has options

## Error Handling

- **Raises ValueError**: If no options found for underlying
- **Empty list**: If underlying symbol invalid

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_options_chain`: Get full options chain
- `get_options_realtime`: Get realtime quotes

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestOptionsContract`

## Notes

- Expiration format depends on underlying (ETF vs index)
- Common patterns: '2月', '3月', '6月', '9月', '12月'
- Useful for filtering options by expiration date