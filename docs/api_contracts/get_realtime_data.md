# API Contract: get_realtime_data

## Overview

**API Function**: `get_realtime_data`

**Purpose**: Get real-time market quotes for stocks, including current price, change, volume, and intraday OHLC data.

**Module**: `akshare_one.modules.realtime`

**Data Sources**: `eastmoney`, `eastmoney_direct`, `xueqiu`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit code) | `600000` |
| `price` | float | yuan | Latest/current price | `10.50` |
| `timestamp` | datetime | - | Quote timestamp | `2024-01-15 14:30:00` |
| `volume` | float | hands | Trading volume (手) | `1234567` |
| `amount` | float | yuan | Trading amount (成交额) | `132500000` |

### Field Types

- `string`: Stock symbol in 6-digit format
- `float`: Floating-point numeric data
- `datetime`: Timestamp in YYYY-MM-DD HH:MM:SS format
- `yuan`: Chinese Yuan (元)
- `hands`: Trading hands (手, 1 hand = 100 shares)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `change` | float | yuan | Price change amount (涨跌额) | Most sources |
| `pct_change` | float | percent | Price change percentage (涨跌幅) | Most sources |
| `open` | float | yuan | Today's opening price (今开) | Most sources |
| `high` | float | yuan | Today's highest price (最高) | Most sources |
| `low` | float | yuan | Today's lowest price (最低) | Most sources |
| `prev_close` | float | yuan | Previous closing price (昨收) | Most sources |
| `name` | string | - | Stock name | Some sources |
| `turnover` | float | percent | Turnover rate | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_zh_a_spot_em`):
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `pct_change`
- `涨跌额` → `change`
- `成交量` → `volume`
- `成交额` → `amount`
- `今开` → `open`
- `最高` → `high`
- `最低` → `low`
- `昨收` → `prev_close`

**Field Transformations**:
- Volume is reported in hands (手)
- All monetary values in yuan (元)
- Percentages as numeric values (not strings)

### Source: `eastmoney_direct`

Direct API call, similar field mapping.

### Source: `xueqiu`

**Original Fields** (from akshare):
- Field names mapped to standard format

## Update Frequency

- **Realtime**: Updated continuously during trading hours (9:30-11:30, 13:00-15:00)
- **Refresh Rate**: Depending on data source, typically every 3-10 seconds
- **After Hours**: Last quote remains available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Stock symbol. If None, returns all stocks |
| `source` | string | no | `eastmoney_direct` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_realtime_data

# Get realtime data for a specific stock
df = get_realtime_data(symbol="600000")

# Get all stocks realtime data
df = get_realtime_data()

# With column filtering
df = get_realtime_data(
    symbol="600000",
    columns=['symbol', 'price', 'pct_change', 'volume']
)

# With specific data source
df = get_realtime_data(symbol="600000", source="xueqiu")
```

## Example Response

```python
# Example DataFrame structure (single stock)
  symbol    price  change  pct_change           timestamp    volume      amount     open     high      low  prev_close
0  600000   10.50    0.30        2.86  2024-01-15 14:30:00  1234567  132500000    10.20   10.80    10.10        10.20

# Example DataFrame structure (all stocks, abbreviated)
  symbol    name    price  pct_change    volume
0  600000  浦发银行   10.50        2.86  1234567
1  000001  平安银行   12.30        1.50   987654
...
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`symbol`, `price`, `timestamp`, `volume`, `amount`)
2. **Type Validation**:
   - `symbol`: string, 6-digit format
   - Price fields: numeric, positive
   - Volume, amount: numeric, non-negative

3. **Value Ranges**:
   - `price` > 0
   - `volume` >= 0
   - `amount` >= 0
   - `pct_change` can be negative (price dropped)

4. **Consistency Rules**:
   - If intraday OHLC provided: high >= low, high >= open, high >= price, low <= open, low <= price
   - Volume and amount should be consistent (amount ≈ avg_price × volume × 100)

## Error Handling

- **Empty DataFrame**: Returned when stock symbol is invalid or no data available
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version (`get_realtime_data_multi_source`) automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_hist_data`: Get historical OHLCV data
- `get_basic_info`: Get stock basic information and market cap
- `get_realtime_data_multi_source`: Multi-source version with auto-failover

## Testing

Contract tests for this API are located in:
- `tests/test_api_contract.py::TestRealtimeDataContract`
- `tests/test_api_field_contracts.py::TestRealtimeDataContract`

Test coverage includes:
- Required field presence
- Field type validation (symbol format, numeric types)
- Value range validation (positive prices, non-negative volume)
- Symbol format validation (6-digit codes)

## Notes

- Realtime data is only available during trading hours
- After market close, data reflects last trading session
- Volume unit is hands (手), where 1 hand = 100 shares
- All prices in yuan (元)
- Some fields may be None/NaN for newly listed stocks or suspended stocks