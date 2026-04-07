# API Contract: get_bond_hist_data

## Overview

**API Function**: `get_bond_hist_data`

**Purpose**: Get historical price data for convertible bonds (可转债), including OHLCV data.

**Module**: `akshare_one.modules.bond`

**Data Sources**: `eastmoney`, `jsl`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `symbol` | string | - | Bond symbol (6-digit code) | `110001` |
| `open` | float | yuan | Opening price | `120.50` |
| `high` | float | yuan | Highest price | `122.30` |
| `low` | float | yuan | Lowest price | `119.80` |
| `close` | float | yuan | Closing price | `121.20` |
| `volume` | float | hands | Trading volume | `54321` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format
- `string`: Bond symbol in 6-digit format (110xxx for Shanghai, 123xxx for Shenzhen)
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元) - price unit
- `hands`: Trading hands (手, 1 hand = 10 bonds for convertible bonds)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `amount` | float | yuan | Trading amount | Most sources |
| `pct_change` | float | percent | Price change percentage | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `bond_cb_hist_em`):
- `日期` → `date`
- `开盘` → `open`
- `收盘` → `close`
- `最高` → `high`
- `最低` → `low`
- `成交量` → `volume`
- `成交额` → `amount`

**Field Transformations**:
- Volume is in hands (手), 1 hand = 10 bonds
- Prices in yuan (元), typically 100+ for convertible bonds

### Source: `jsl`

**Original Fields** (from akshare/jsl):
- Field names standardized to eastmoney format

## Update Frequency

- **Daily data**: Updated daily after market close (15:00+)
- Historical data available from bond listing date

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Bond symbol (6-digit code) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_bond_hist_data

# Basic usage - get historical data for a convertible bond
df = get_bond_hist_data(symbol="110001")

# Get data for a specific date range
df = get_bond_hist_data(
    symbol="123456",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_bond_hist_data(
    symbol="110001",
    columns=['date', 'close', 'volume']
)
```

## Example Response

```python
# Example DataFrame structure (daily data)
      date     symbol    open    high     low   close   volume     amount
0  2024-01-15   110001   120.50  122.30  119.80  121.20   54321  6543210
1  2024-01-16   110001   121.20  123.00  120.50  122.50   43210  5320980
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`date`, `symbol`, `open`, `high`, `low`, `close`, `volume`)
2. **Type Validation**:
   - `date`: datetime or string in YYYY-MM-DD format
   - `symbol`: string, 6-digit format (110xxx or 123xxx)
   - Price fields: numeric, positive (typically > 100)
   - Volume: numeric, non-negative

3. **Value Ranges**:
   - All prices > 0 (convertible bonds typically > 100 yuan)
   - Volume >= 0
   - high >= low (consistency rule)
   - high >= open, high >= close
   - low <= open, low <= close

4. **Symbol Format**:
   - Shanghai bonds: 110xxx, 113xxx, 118xxx
   - Shenzhen bonds: 123xxx, 127xxx, 128xxx

## Error Handling

- **Empty DataFrame**: Returned when bond symbol is invalid or bond has expired/delisted
- **Exception Handling**: Network errors and API failures are caught and logged
- **Symbol Validation**: 6-digit format required

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_bond_realtime_data`: Get realtime bond quotes
- `get_bond_list`: Get list of available convertible bonds

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestBondHistDataContract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- OHLCV consistency rules
- Symbol format validation

## Notes

- Convertible bond symbols: 110xxx/113xxx/118xxx (Shanghai), 123xxx/127xxx/128xxx (Shenzhen)
- Volume unit: 1 hand = 10 bonds (not 100 like stocks)
- Bond prices typically range from 80-150+ yuan
- Some bonds may have limited trading activity (low volume)
- Expired/delisted bonds return empty DataFrame