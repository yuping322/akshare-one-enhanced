# API Contract: get_dragon_tiger_broker_stats

## Overview

**API Function**: `get_dragon_tiger_broker_stats`

**Purpose**: Get broker (营业部) statistics from dragon tiger list.

**Module**: `akshare_one.modules.lhb`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `broker` | string | - | Broker/branch name | `中信证券营业部` |
| `total_buy` | float | yuan | Total buy amount | `1000000000` |
| `total_sell` | float | yuan | Total sell amount | `800000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `net_buy` | float | yuan | Net buy amount | Most sources |
| `trade_count` | float | - | Number of trades | Most sources |
| `win_rate` | float | percent | Win rate percentage | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare broker stats API):
- `营业部` → `broker`
- `总买入额` → `total_buy`
- `总卖出额` → `total_sell`
- `净买入额` → `net_buy`
- `交易次数` → `trade_count`

**Field Transformations**:
- All amounts in yuan
- Standard field names

## Update Frequency

- **Daily**: Updated with dragon tiger data
- Statistics calculated from trade records

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `top_n` | int | no | `100` | Number of top brokers to return |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_dragon_tiger_broker_stats

# Get top broker statistics
df = get_dragon_tiger_broker_stats(
    start_date="2024-01-01",
    end_date="2024-03-31",
    top_n=100
)

# With column filtering
df = get_dragon_tiger_broker_stats(
    start_date="2024-01-01",
    end_date="2024-01-31",
    columns=['broker', 'total_buy', 'total_sell', 'net_buy', 'trade_count']
)
```

## Example Response

```python
# Example DataFrame structure
             broker    total_buy   total_sell      net_buy  trade_count
0      中信证券营业部  2000000000.0  1500000000.0  500000000.0        150.0
1      华泰证券营业部  1500000000.0  1200000000.0  300000000.0        120.0
```

## Validation Rules

1. **Required Fields**: `broker`, `total_buy`, `total_sell`
2. **Type Validation**:
   - Amounts: float
   - `trade_count`: float, positive

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_dragon_tiger_list`: Get detailed dragon tiger data
- `get_dragon_tiger_summary`: Get summary statistics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDragonTigerContract`

## Notes

- Brokers are securities firm branches
- Top brokers = most active institutional traders
- Net buy indicates bullish activity
- Trade count shows activity level
- Useful for tracking hot money
- Some brokers have good track records
- High activity may indicate market trends