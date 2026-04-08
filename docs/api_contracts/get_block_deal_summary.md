# API Contract: get_block_deal_summary

## Overview

**API Function**: `get_block_deal_summary`

**Purpose**: Get block deal summary statistics aggregated by date, stock, or broker.

**Module**: `akshare_one.modules.blockdeal`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `total_deals` | float | - | Total number of deals | `100` |
| `total_amount` | float | yuan | Total transaction amount | `10000000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `date` | datetime | - | Summary date (if grouped by date) | Most sources |
| `symbol` | string | - | Stock symbol (if grouped by stock) | Some queries |
| `broker` | string | - | Broker name (if grouped by broker) | Some queries |
| `avg_premium_rate` | float | percent | Average premium rate | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare block deal summary API):
- `交易次数` → `total_deals`
- `成交总额` → `total_amount`
- `平均溢价率` → `avg_premium_rate`

**Field Transformations**:
- Aggregated statistics
- Amount in yuan

## Update Frequency

- **Daily**: Updated after market close
- Historical summaries available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `group_by` | string | no | `date` | Grouping dimension ('date', 'stock', 'broker') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_block_deal_summary

# Get daily summary
df = get_block_deal_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="date"
)

# Get summary by stock
df = get_block_deal_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="stock"
)

# Get summary by broker
df = get_block_deal_summary(
    start_date="2024-01-01",
    end_date="2024-03-31",
    group_by="broker"
)

# With column filtering
df = get_block_deal_summary(
    start_date="2024-01-01",
    end_date="2024-01-31",
    columns=['date', 'total_deals', 'total_amount']
)
```

## Example Response

```python
# Example DataFrame structure (grouped by date)
         date  total_deals   total_amount
0  2024-01-15        100.0  10000000000.0
1  2024-01-16        120.0  12000000000.0
```

## Validation Rules

1. **Required Fields**: `total_deals`, `total_amount`
2. **Type Validation**:
   - Counts: float, positive
   - Amounts: float, positive

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_block_deal`: Get detailed block deal transactions

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestBlockDealContract`

## Notes

- group_by='date': Daily market summary
- group_by='stock': Summary per stock
- group_by='broker': Summary per broker
- Useful for market-level analysis
- High deal count = active block trading
- Large amounts = significant institutional moves
- Compare across periods for trends