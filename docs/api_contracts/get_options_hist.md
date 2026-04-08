# API Contract: get_options_hist

## Overview

**API Function**: `get_options_hist`

**Purpose**: Get historical OHLCV data for a specific option contract.

**Module**: `akshare_one.modules.options`

**Data Sources**: `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `timestamp` | datetime | - | Trading date/time | `2024-01-15` |
| `symbol` | string | - | Option symbol | `10004005` |
| `close` | float | yuan | Closing price | `0.1234` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `open` | float | yuan | Opening price | Most sources |
| `high` | float | yuan | Highest price | Most sources |
| `low` | float | yuan | Lowest price | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `open_interest` | float | hands | Open interest | Some sources |
| `settlement` | float | yuan | Settlement price | Some sources |

## Data Source Mapping

### Source: `sina`

**Original Fields** (from akshare `option_sse_daily_sina`):
- `日期` → `timestamp`
- `开盘` → `open`
- `收盘` → `close`
- `最高` → `high`
- `最低` → `low`
- `成交量` → `volume`

**Field Transformations**:
- Timestamp converted to datetime with timezone
- Symbol added from parameter
- open_interest and settlement set to None if missing

## Update Frequency

- **Daily**: Updated after market close
- Historical data available for listed options

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Option symbol (8-digit) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `sina` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_options_hist

# Get historical data for an option
df = get_options_hist(symbol="10004005")

# Get specific date range
df = get_options_hist(
    symbol="10004005",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# With column filtering
df = get_options_hist(
    symbol="10004005",
    columns=['timestamp', 'close', 'volume']
)
```

## Example Response

```python
# Example DataFrame structure
    timestamp    symbol     open     high      low    close  volume  open_interest  settlement
0  2024-01-15  10004005   0.1200   0.1250   0.1180   0.1234   12345           None        None
1  2024-01-16  10004005   0.1234   0.1270   0.1220   0.1250    9876           None        None
```

## Validation Rules

1. **Required Fields**: `timestamp`, `symbol`, `close`
2. **Type Validation**:
   - `timestamp`: datetime
   - Price fields: float, positive
   - `volume`: float, non-negative
3. **Value Ranges**:
   - Prices > 0
   - Volume >= 0

## Error Handling

- **Empty DataFrame**: Invalid symbol or no data in range
- **Exception Handling**: API errors caught and logged

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_options_realtime`: Get realtime quotes
- `get_options_chain`: Get full options chain
- `get_hist_data`: Get stock historical data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestOptionsContract`

## Notes

- Historical data availability varies by option
- Delisted/expired options may have limited history
- Settlement price may not be available for all sources