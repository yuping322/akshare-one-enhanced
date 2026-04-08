# API Contract: get_repurchase_data

## Overview

**API Function**: `get_repurchase_data`

**Purpose**: Get stock repurchase (回购) data for companies.

**Module**: `akshare_one.modules.disclosure`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `repurchase_amount` | float | yuan | Planned repurchase amount | `100000000` |
| `announcement_date` | datetime | - | Announcement date | `2024-01-15` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `executed_amount` | float | yuan | Executed repurchase amount | Most sources |
| `executed_shares` | float | shares | Shares repurchased | Some sources |
| `repurpose_price_high` | float | yuan | High repurchase price | Some sources |
| `repurpose_price_low` | float | yuan | Low repurchase price | Some sources |
| `progress` | string | - | Repurchase progress | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare repurchase API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `计划回购金额` → `repurchase_amount`
- `已回购金额` → `executed_amount`
- `已回购股数` → `executed_shares`
- `公告日期` → `announcement_date`
- `回购价格上限` → `repurpose_price_high`
- `回购价格下限` → `repurpose_price_low`

**Field Transformations**:
- All monetary values in yuan
- Date converted to datetime

## Update Frequency

- **Daily**: Updated with announcements
- Historical repurchase data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Stock symbol (if None, returns all) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_repurchase_data

# Get all repurchase data
df = get_repurchase_data()

# Get repurchase data for specific stock
df = get_repurchase_data(symbol="600000")

# Get recent repurchases
df = get_repurchase_data(
    start_date="2024-01-01"
)

# With column filtering
df = get_repurchase_data(
    symbol="600000",
    columns=['symbol', 'name', 'repurchase_amount', 'executed_amount']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name  repurchase_amount  executed_amount  executed_shares announcement_date  progress
0  600000  浦发银行       100000000.0      50000000.0       5000000.0        2024-01-15    实施中
```

## Validation Rules

1. **Required Fields**: `symbol`, `repurchase_amount`, `announcement_date`
2. **Type Validation**:
   - Monetary values: float
   - `announcement_date`: datetime
   - Share counts: float, positive

## Error Handling

- **Empty DataFrame**: No repurchase data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_dividend_data`: Get dividend data
- `get_disclosure_news`: Get disclosure news

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDisclosureContract`

## Notes

- Repurchase = company buying own shares
- Usually bullish signal
- Shows management confidence
- Compare planned vs executed amounts
- Progress indicates implementation
- Price range shows execution price target
- Useful for identifying undervalued stocks
- Track execution rate for credibility