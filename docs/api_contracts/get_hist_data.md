# API Contract: get_hist_data

## Overview

**API Function**: `get_hist_data`

**Purpose**: Get historical market data for stocks, including OHLCV (Open, High, Low, Close, Volume) data with optional adjustment for corporate actions.

**Module**: `akshare_one.modules.historical`

**Data Sources**: `eastmoney`, `eastmoney_direct`, `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `timestamp` | datetime | - | Trading timestamp/date | `2024-01-15` or `2024-01-15 09:30:00` |
| `open` | float | yuan | Opening price | `10.50` |
| `high` | float | yuan | Highest price | `11.20` |
| `low` | float | yuan | Lowest price | `10.30` |
| `close` | float | yuan | Closing price | `10.80` |
| `volume` | float | hands | Trading volume | `1234567` |

### Field Types

- `datetime`: Date/time in ISO 8601 format (YYYY-MM-DD for daily, YYYY-MM-DD HH:MM:SS for minute/hour)
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元) - price unit
- `hands`: Trading hands (手, 1 hand = 100 shares)

## Optional Fields

The following fields MAY be present depending on the data source or interval.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `amount` | float | yuan | Trading amount (成交额) | Most sources |
| `pct_change` | float | percent | Price change percentage | Most sources |
| `change` | float | yuan | Price change amount | Most sources |
| `turnover` | float | percent | Turnover rate | Most sources |
| `amplitude` | float | percent | Price amplitude | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_zh_a_hist`):
- `日期` → `timestamp`
- `开盘` → `open`
- `收盘` → `close`
- `最高` → `high`
- `最低` → `low`
- `成交量` → `volume`
- `成交额` → `amount`
- `振幅` → `amplitude`
- `涨跌幅` → `pct_change`
- `涨跌额` → `change`
- `换手率` → `turnover`

**Field Transformations**:
- Volume is reported in hands (手)
- Prices are in yuan (元)

### Source: `eastmoney_direct`

**Direct API call to eastmoney**, similar field mapping to `eastmoney` source.

### Source: `sina`

**Original Fields** (from akshare):
- Field names are standardized to match eastmoney format

## Update Frequency

- **Minute data**: Realtime during trading hours, historical available
- **Hour data**: Available after each hour completes
- **Daily data**: Updated daily after market close (15:00+)
- **Weekly/Monthly**: Aggregated from daily data

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit code) |
| `interval` | string | no | `day` | Time interval: `minute`, `hour`, `day`, `week`, `month`, `year` |
| `interval_multiplier` | int | no | `1` | Interval multiplier (e.g., 5 for 5-minute bars) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `adjust` | string | no | `none` | Price adjustment: `none`, `qfq` (前复权), `hfq` (后复权) |
| `source` | string | no | `eastmoney_direct` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_hist_data

# Basic usage - get daily data
df = get_hist_data(symbol="600000")

# Get minute-level data (5-minute bars)
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5
)

# Get data with forward adjustment (qfq)
df = get_hist_data(
    symbol="600000",
    adjust="qfq",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_hist_data(
    symbol="600000",
    columns=['timestamp', 'close', 'volume']
)
```

## Example Response

```python
# Example DataFrame structure (daily data)
   timestamp     open   high    low   close    volume    amount  pct_change
0  2024-01-15   10.50  11.20  10.30   10.80  1234567  13250000        2.86
1  2024-01-16   10.80  11.00  10.60   10.90   987654  10800000        0.93
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`timestamp`, `open`, `high`, `low`, `close`, `volume`)
2. **Type Validation**:
   - `timestamp`: datetime or string in YYYY-MM-DD format
   - Price fields (`open`, `high`, `low`, `close`): numeric, positive
   - `volume`: numeric, non-negative

3. **Value Ranges**:
   - All prices > 0
   - Volume >= 0
   - high >= low (consistency rule)
   - high >= open, high >= close
   - low <= open, low <= close

4. **Consistency Rules**:
   - High must be the maximum of {open, high, low, close}
   - Low must be the minimum of {open, high, low, close}

## Error Handling

- **Empty DataFrame**: Returned when no data is available for the specified period
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version (`get_hist_data_multi_source`) automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_realtime_data`: Get current realtime quotes
- `get_basic_info`: Get stock basic information
- `get_hist_data_multi_source`: Multi-source version with auto-failover

## Testing

Contract tests for this API are located in:
- `tests/test_api_contract.py::TestHistoricalDataContract`
- `tests/test_api_field_contracts.py::TestHistDataContract`

Test coverage includes:
- Required field presence (`timestamp`, `open`, `high`, `low`, `close`, `volume`)
- Field type validation (numeric types for prices and volume)
- Value range validation (positive prices, non-negative volume)
- Cross-source schema consistency
- OHLCV consistency rules (high >= low, etc.)

## Notes

- For minute/hour intervals, `timestamp` includes time component
- Volume unit is hands (手), where 1 hand = 100 shares
- Price adjustment (`qfq`, `hfq`) affects historical prices for dividend/split events
- Some sources may have limited historical data availability for certain intervals