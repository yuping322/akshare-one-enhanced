# API Contract: get_options_realtime

## Overview

**API Function**: `get_options_realtime`

**Purpose**: Get realtime options quote data for a specific option or all options under an underlying asset.

**Module**: `akshare_one.modules.options`

**Data Sources**: `sina` (uses eastmoney APIs)

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Option symbol (8-digit code) | `10004005` |
| `underlying` | string | - | Underlying asset symbol | `510300` |
| `price` | float | yuan | Latest price | `0.1234` |
| `timestamp` | datetime | - | Quote timestamp | `2024-01-15 14:30:00` |
| `volume` | float | hands | Trading volume | `12345` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `change` | float | yuan | Price change amount | Most sources |
| `pct_change` | float | percent | Price change percentage | Most sources |
| `open_interest` | float | hands | Open interest (持仓量) | Most sources |
| `iv` | float | percent | Implied volatility | Some sources |

## Data Source Mapping

### Source: `sina`

**Original Fields** (from akshare `option_current_em`):
- `代码` → `symbol`
- `最新价` → `price`
- `涨跌额` → `change`
- `涨跌幅` → `pct_change`
- `成交量` → `volume`
- `持仓量` → `open_interest`

**Field Transformations**:
- Underlying symbol parsed from option name
- Timestamp added as current time
- IV field set to None (placeholder)

## Update Frequency

- **Realtime**: Updated continuously during trading hours
- **Refresh Rate**: Every 3-10 seconds depending on source

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Option symbol (8-digit) |
| `underlying_symbol` | string | no | None | Underlying asset symbol |
| `source` | string | no | `sina` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_options_realtime

# Get specific option realtime quote
df = get_options_realtime(symbol="10004005")

# Get all options for an underlying
df = get_options_realtime(underlying_symbol="510300")

# With column filtering
df = get_options_realtime(
    symbol="10004005",
    columns=['symbol', 'price', 'volume', 'open_interest']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol underlying    price  change  pct_change           timestamp  volume  open_interest    iv
0  10004005   510300   0.1234   0.005        4.05  2024-01-15 14:30:00   12345          5678  None
```

## Validation Rules

1. **Required Fields**: `symbol`, `underlying`, `price`, `timestamp`, `volume`
2. **Type Validation**:
   - `symbol`: string, 8-digit format
   - `price`: float, positive
   - `volume`: float, non-negative
3. **Value Ranges**:
   - `price` > 0
   - `volume` >= 0

## Error Handling

- **Empty DataFrame**: Invalid symbol or underlying
- **Exception Handling**: Network/API errors caught and logged
- **Raises ValueError**: When both or neither symbol/underlying_symbol provided

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_options_chain`: Get full options chain with details
- `get_options_expirations`: Get available expiration dates
- `get_options_hist`: Get historical options data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestOptionsContract`

## Notes

- Must specify either `symbol` OR `underlying_symbol`, not both
- Options data only available during trading hours
- IV (implied volatility) may be None for some sources