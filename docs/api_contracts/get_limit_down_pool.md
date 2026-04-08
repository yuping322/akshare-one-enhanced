# API Contract: get_limit_down_pool

## Overview

**API Function**: `get_limit_down_pool`

**Purpose**: Get pool of stocks that hit daily limit down (跌停板).

**Module**: `akshare_one.modules.limitup`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `某某股份` |
| `close` | float | yuan | Closing price (limit down price) | `9.00` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `limit_down_time` | datetime | - | Time when limit down reached | Most sources |
| `limit_down_count` | float | - | Consecutive limit down days | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `amount` | float | yuan | Trading amount | Some sources |
| `limit_down_reason` | string | - | Reason for limit down | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare limit down pool API):
- `代码` → `symbol`
- `名称` → `name`
- `收盘价` → `close`
- `跌停时间` → `limit_down_time`
- `连板数` → `limit_down_count`
- `成交量` → `volume`
- `成交额` → `amount`
- `跌停原因` → `limit_down_reason`

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
from akshare_one import get_limit_down_pool

# Get latest limit down pool
df = get_limit_down_pool()

# Get limit down pool for specific date
df = get_limit_down_pool(date="2024-01-15")

# With column filtering
df = get_limit_down_pool(
    date="2024-01-15",
    columns=['symbol', 'name', 'close', 'limit_down_count']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name  close      limit_down_time  limit_down_count    volume       amount
0  600000  某某股份   9.00  2024-01-15 10:30:00             1.0  500000.0   4500000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `close`
2. **Type Validation**:
   - `close`: float, positive
   - `limit_down_count`: float, positive integer
3. **Limit Down Rules**:
   - Price decreased 10% (or 20% for CYB/KCB)
   - Cannot trade lower after limit down

## Error Handling

- **Empty DataFrame**: No limit down stocks on that date
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_limit_up_pool`: Get limit up pool
- `get_limit_up_stats`: Get limit up/down statistics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestLimitUpDownContract`

## Notes

- Limit down = 跌停 (price hit daily min)
- Most stocks: ±10%, ST stocks: ±5%
- CYB/KCB: ±20%
- limit_down_count shows consecutive limit downs
- Consecutive limit downs = strong sell-off
- Avoid stocks with multiple limit downs
- May indicate bad news or panic selling
- Hard to sell when at limit down
- Risk management important