# API Contract: get_limit_up_pool

## Overview

**API Function**: `get_limit_up_pool`

**Purpose**: Get pool of stocks that hit daily limit up (涨停板).

**Module**: `akshare_one.modules.limitup`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |
| `close` | float | yuan | Closing price (limit up price) | `11.00` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `limit_up_time` | datetime | - | Time when limit up reached | Most sources |
| `limit_up_count` | float | - | Consecutive limit up days | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `amount` | float | yuan | Trading amount | Some sources |
| `limit_up_reason` | string | - | Reason for limit up | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare limit up pool API):
- `代码` → `symbol`
- `名称` → `name`
- `收盘价` → `close`
- `涨停时间` → `limit_up_time`
- `连板数` → `limit_up_count`
- `成交量` → `volume`
- `成交额` → `amount`
- `涨停原因` → `limit_up_reason`

**Field Transformations**:
- Time converted to datetime
- Standard field names

## Update Frequency

- **Daily**: Updated after market close
- Intraday updates during trading hours

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | no | None | Query date (YYYY-MM-DD), None for latest |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_limit_up_pool

# Get latest limit up pool
df = get_limit_up_pool()

# Get limit up pool for specific date
df = get_limit_up_pool(date="2024-01-15")

# With column filtering
df = get_limit_up_pool(
    date="2024-01-15",
    columns=['symbol', 'name', 'close', 'limit_up_count']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name   close      limit_up_time  limit_up_count     volume       amount
0  600000  浦发银行   11.00  2024-01-15 10:30:00            2.0  1000000.0  11000000.0
1  000001  平安银行   12.10  2024-01-15 14:00:00            1.0   800000.0   9680000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `close`
2. **Type Validation**:
   - `close`: float, positive
   - `limit_up_count`: float, positive integer
3. **Limit Up Rules**:
   - Price increased 10% (or 20% for CYB/KCB)
   - Cannot trade higher after limit up

## Error Handling

- **Empty DataFrame**: No limit up stocks on that date
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_limit_down_pool`: Get limit down pool
- `get_limit_up_stats`: Get limit up statistics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestLimitUpDownContract`

## Notes

- Limit up = 涨停 (price hit daily max)
- Most stocks: ±10%, ST stocks: ±5%
- CYB/KCB: ±20%
- limit_up_count shows consecutive limit ups
- Early limit up (涨停时间) often stronger
- Volume/amount show trading activity
- High consecutive limit ups = strong momentum
- Limit up stocks attract attention