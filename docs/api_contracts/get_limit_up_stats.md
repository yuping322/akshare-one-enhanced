# API Contract: get_limit_up_stats

## Overview

**API Function**: `get_limit_up_stats`

**Purpose**: Get statistics on limit up and limit down stocks.

**Module**: `akshare_one.modules.limitup`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `limit_up_count` | float | - | Number of limit up stocks | `50` |
| `limit_down_count` | float | - | Number of limit down stocks | `10` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `total_count` | float | - | Total number of stocks | Most sources |
| `limit_up_ratio` | float | percent | Limit up ratio | Most sources |
| `limit_down_ratio` | float | percent | Limit down ratio | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare limit up stats API):
- `日期` → `date`
- `涨停数` → `limit_up_count`
- `跌停数` → `limit_down_count`
- `总股票数` → `total_count`
- `涨停占比` → `limit_up_ratio`
- `跌停占比` → `limit_down_ratio`

**Field Transformations**:
- Date converted to datetime
- Ratios as percentages

## Update Frequency

- **Daily**: Updated after market close
- Historical statistics available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_limit_up_stats

# Get limit up/down statistics
df = get_limit_up_stats()

# Get statistics for date range
df = get_limit_up_stats(
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_limit_up_stats(
    start_date="2024-01-01",
    end_date="2024-01-31",
    columns=['date', 'limit_up_count', 'limit_down_count']
)
```

## Example Response

```python
# Example DataFrame structure
         date  limit_up_count  limit_down_count  total_count  limit_up_ratio  limit_down_ratio
0  2024-01-15            50.0              10.0       4000.0            1.25              0.25
1  2024-01-16            60.0               8.0       4000.0            1.50              0.20
```

## Validation Rules

1. **Required Fields**: `date`, `limit_up_count`, `limit_down_count`
2. **Type Validation**:
   - `date`: datetime
   - Counts: float, positive
   - Ratios: float, 0-100

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_limit_up_pool`: Get limit up stocks
- `get_limit_down_pool`: Get limit down stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestLimitUpDownContract`

## Notes

- Market sentiment indicator
- High limit up count = bullish market
- High limit down count = bearish market
- Ratio = count / total stocks
- Useful for market timing
- Compare with historical averages
- Extreme readings may signal reversal
- Part of market breadth analysis