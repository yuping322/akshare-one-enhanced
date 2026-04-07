# API Contract: get_futures_hist_data

## Overview

**API Function**: `get_futures_hist_data`

**Purpose**: Get historical price data for futures contracts, including OHLCV data plus open interest and settlement prices.

**Module**: `akshare_one.modules.futures`

**Data Sources**: `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `timestamp` | datetime | - | Trading timestamp/date | `2024-01-15` |
| `symbol` | string | - | Futures symbol (品种代码) | `AU0` |
| `contract` | string | - | Contract code (合约代码) | `2406` |
| `open` | float | yuan | Opening price | `480.50` |
| `high` | float | yuan | Highest price | `485.20` |
| `low` | float | yuan | Lowest price | `478.30` |
| `close` | float | yuan | Closing price | `482.80` |
| `volume` | float | hands | Trading volume (手) | `123456` |
| `open_interest` | float | hands | Open interest (持仓量) | `54321` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format (daily) or with time for minute/hour data
- `string`: Futures symbol and contract codes
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元) - price unit
- `hands`: Trading hands (手, unit varies by futures type)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `settlement` | float | yuan | Settlement price (结算价) | Most sources |
| `amount` | float | yuan | Trading amount | Some sources |
| `pct_change` | float | percent | Price change percentage | Some sources |
| `change` | float | yuan | Price change amount | Some sources |

## Data Source Mapping

### Source: `sina`

**Original Fields** (from akshare `futures_main_sina` or similar):
- `日期` → `timestamp`
- `合约代码` → `contract`
- `开盘价` → `open`
- `最高价` → `high`
- `最低价` → `low`
- `收盘价` → `close`
- `成交量` → `volume`
- `持仓量` → `open_interest`
- `结算价` → `settlement` (if available)

**Field Transformations**:
- Symbol added to identify futures type (AU, AG, CU, etc.)
- Volume and open interest in hands (手)
- Prices in yuan (元) per unit (varies by futures type)

## Update Frequency

- **Daily data**: Updated daily after trading session
- **Minute/Hour data**: Available with shorter intervals
- Historical data varies by contract (typically months to years)

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Futures symbol (品种, e.g., `AU0` for gold) |
| `contract` | string | no | `main` | Contract code (e.g., `2406`, or `main` for main contract) |
| `interval` | string | no | `day` | Time interval: `minute`, `hour`, `day`, `week`, `month` |
| `interval_multiplier` | int | no | `1` | Interval multiplier (e.g., 5 for 5-minute bars) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `sina` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_futures_hist_data

# Basic usage - get historical data for gold futures main contract
df = get_futures_hist_data(symbol="AU0")

# Get data for specific contract
df = get_futures_hist_data(
    symbol="AU0",
    contract="2406"  # June 2024 contract
)

# Get minute-level data
df = get_futures_hist_data(
    symbol="CU0",  # Copper
    interval="minute",
    interval_multiplier=5  # 5-minute bars
)

# Get data for specific date range
df = get_futures_hist_data(
    symbol="AU0",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_futures_hist_data(
    symbol="AU0",
    columns=['timestamp', 'close', 'volume', 'open_interest']
)
```

## Example Response

```python
# Example DataFrame structure (daily data)
   timestamp  symbol contract    open    high     low   close   volume  open_interest  settlement
0  2024-01-15    AU0     2406   480.50  485.20  478.30  482.80  123456         54321      481.50
1  2024-01-16    AU0     2406   482.80  488.00  480.50  486.20   98765         52109      485.00
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`timestamp`, `symbol`, `contract`, `open`, `high`, `low`, `close`, `volume`, `open_interest`)
2. **Type Validation**:
   - `timestamp`: datetime or string
   - `symbol`, `contract`: strings
   - Price fields: numeric, positive
   - Volume, open_interest: numeric, non-negative

3. **Value Ranges**:
   - All prices > 0
   - Volume >= 0
   - Open_interest >= 0
   - high >= low (consistency rule)
   - Settlement price typically close to close price

4. **Futures Types**:
   - Common symbols: AU0 (gold), AG0 (silver), CU0 (copper), RB0 (rebar), I0 (iron ore), etc.
   - Contract codes: YYMM format (year-month, e.g., 2406 = June 2024)
   - `main` refers to the most active contract

## Error Handling

- **Empty DataFrame**: Returned when futures symbol/contract is invalid or expired
- **Exception Handling**: Network errors and API failures are caught and logged
- **Contract Validation**: Expired contracts return empty DataFrame

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_futures_realtime_data`: Get realtime futures quotes
- `get_futures_main_contracts`: Get list of main contracts for each futures type

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestFuturesHistDataContract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- OHLCV consistency rules
- Open interest validation

## Notes

- Futures symbols: AU0 (黄金), AG0 (白银), CU0 (铜), RB0 (螺纹钢), I0 (铁矿石), etc.
- Contract codes in YYMM format (2406 = June 2024 delivery)
- `main` contract = most active/nearby delivery contract
- Open interest (持仓量) shows total outstanding contracts
- Settlement price (结算价) used for margin calculations
- Different futures have different trading units and price units
- Expired contracts have no data (empty DataFrame returned)
- Volume and open interest units vary by futures type (手 may represent different quantities)