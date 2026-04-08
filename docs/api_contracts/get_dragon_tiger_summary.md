# API Contract: get_dragon_tiger_summary

## Overview

**API Function**: `get_dragon_tiger_summary`

**Purpose**: Get dragon tiger list summary statistics aggregated by date, stock, or broker.

**Module**: `akshare_one.modules.lhb`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `total_buy` | float | yuan | Total buy amount | `1000000000` |
| `total_sell` | float | yuan | Total sell amount | `800000000` |
| `net_buy` | float | yuan | Net buy amount | `200000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `stock_count` | float | - | Number of stocks on list | Most sources |
| `symbol` | string | - | Stock symbol (if grouped by stock) | Some queries |
| `broker` | string | - | Broker name (if grouped by broker) | Some queries |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare dragon tiger summary API):
- `日期` → `date`
- `总买入额` → `total_buy`
- `总卖出额` → `total_sell`
- `净买入额` → `net_buy`
- `上榜股票数` → `stock_count`

**Field Transformations**:
- Date converted to datetime
- All amounts in yuan

## Update Frequency

- **Daily**: Updated after market close
- Historical summaries available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `group_by` | string | no | `date` | Grouping ('date', 'stock', 'broker') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_dragon_tiger_summary

# Get daily summary
df = get_dragon_tiger_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="date"
)

# Get summary by stock
df = get_dragon_tiger_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="stock"
)

# Get summary by broker
df = get_dragon_tiger_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="broker"
)

# With column filtering
df = get_dragon_tiger_summary(
    start_date="2024-01-01",
    end_date="2024-01-31",
    columns=['date', 'total_buy', 'total_sell', 'net_buy']
)
```

## Example Response

```python
# Example DataFrame structure (grouped by date)
         date    total_buy   total_sell      net_buy  stock_count
0  2024-01-15  1000000000.0  800000000.0  200000000.0         50.0
1  2024-01-16  1200000000.0  900000000.0  300000000.0         55.0
```

## Validation Rules

1. **Required Fields**: `date`, `total_buy`, `total_sell`, `net_buy`
2. **Type Validation**:
   - `date`: datetime
   - Amounts: float
3. **Consistency**: net_buy = total_buy - total_sell

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_dragon_tiger_list`: Get detailed dragon tiger data
- `get_dragon_tiger_broker_stats`: Get broker statistics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDragonTigerContract`

## Notes

- group_by='date': Daily market summary
- group_by='stock': Summary per stock
- group_by='broker': Summary per broker
- Dragon tiger list shows major trades
- Useful for tracking institutional activity
- High net buy = bullish institutional activity