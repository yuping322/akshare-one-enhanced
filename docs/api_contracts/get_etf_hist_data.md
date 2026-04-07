# API Contract: get_etf_hist_data

## Overview

**API Function**: `get_etf_hist_data`

**Purpose**: Get historical price data for Exchange-Traded Funds (ETFs), including OHLCV data.

**Module**: `akshare_one.modules.etf`

**Data Sources**: `eastmoney`, `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `symbol` | string | - | ETF symbol (6-digit code) | `510050` |
| `open` | float | yuan | Opening price | `2.850` |
| `high` | float | yuan | Highest price | `2.920` |
| `low` | float | yuan | Lowest price | `2.830` |
| `close` | float | yuan | Closing price | `2.880` |
| `volume` | float | hands | Trading volume | `12345678` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format
- `string`: ETF symbol in 6-digit format
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元) - price unit
- `hands`: Trading hands (手, 1 hand = 100 shares)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `amount` | float | yuan | Trading amount (成交额) | Most sources |
| `pct_change` | float | percent | Price change percentage | Most sources |
| `change` | float | yuan | Price change amount | Some sources |
| `turnover` | float | percent | Turnover rate | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `fund_etf_hist_em`):
- `日期` → `date`
- `开盘` → `open`
- `收盘` → `close`
- `最高` → `high`
- `最低` → `low`
- `成交量` → `volume`
- `成交额` → `amount`
- `涨跌幅` → `pct_change`
- `涨跌额` → `change`
- `换手率` → `turnover`

**Field Transformations**:
- Volume is reported in hands (手)
- Prices are in yuan (元)
- Symbol is added as a column for consistency

### Source: `sina`

**Original Fields**:
- Field names standardized to match eastmoney format

## Update Frequency

- **Daily data**: Updated daily after market close (15:00+)
- **Weekly data**: Aggregated from daily data, available weekly
- **Monthly data**: Aggregated from daily data, available monthly

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | ETF symbol (6-digit code) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `interval` | string | no | `daily` | Data interval: `daily`, `weekly`, `monthly` |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_etf_hist_data

# Basic usage - get daily data for 50ETF
df = get_etf_hist_data(symbol="510050")

# Get data for a specific date range
df = get_etf_hist_data(
    symbol="510300",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# Get weekly data
df = get_etf_hist_data(
    symbol="510050",
    interval="weekly"
)

# With column filtering
df = get_etf_hist_data(
    symbol="510050",
    columns=['date', 'close', 'volume']
)
```

## Example Response

```python
# Example DataFrame structure (daily data)
      date     symbol    open    high     low   close     volume      amount  pct_change
0  2024-01-15   510050   2.850   2.920   2.830   2.880  12345678  351234500        1.05
1  2024-01-16   510050   2.880   2.900   2.860   2.895   9876543  285432100        0.52
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`date`, `symbol`, `open`, `high`, `low`, `close`, `volume`)
2. **Type Validation**:
   - `date`: datetime or string in YYYY-MM-DD format
   - `symbol`: string, 6-digit format
   - Price fields: numeric, positive
   - Volume: numeric, non-negative

3. **Value Ranges**:
   - All prices > 0
   - Volume >= 0
   - high >= low (consistency rule)
   - high >= open, high >= close
   - low <= open, low <= close

4. **Consistency Rules**:
   - High must be the maximum of {open, high, low, close}
   - Low must be the minimum of {open, high, low, close}
   - Amount should be roughly consistent with volume × avg_price

## Error Handling

- **Empty DataFrame**: Returned when ETF symbol is invalid or no data available
- **Exception Handling**: Network errors and API failures are caught and logged
- **Symbol Validation**: 6-digit format required

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_etf_realtime_data`: Get realtime ETF quotes
- `get_etf_list`: Get list of available ETFs
- `get_index_hist_data`: Get index historical data

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestETFHistDataContract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- OHLCV consistency rules

## Notes

- ETF symbols are 6-digit codes (e.g., 510050 for 50ETF, 510300 for 300ETF)
- Volume unit is hands (手), where 1 hand = 100 shares
- Unlike stocks, ETFs don't have adjustment for corporate actions
- Some ETFs may have limited historical data availability