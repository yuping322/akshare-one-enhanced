# API Contract: get_shareholder_changes

## Overview

**API Function**: `get_shareholder_changes`

**Purpose**: Get shareholder change data (增减持) showing stock holdings changes by major shareholders.

**Module**: `akshare_one.modules.shareholder`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `holder_name` | string | - | Shareholder name | `张三` |
| `change_date` | datetime | - | Change date | `2024-01-15` |
| `change_shares` | float | shares | Number of shares changed | `100000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `position` | string | - | Holder position/title | Most sources |
| `reason` | string | - | Change reason | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_share_hold_change_sse`):
- `公司代码` → `symbol`
- `公司名称` → `name`
- `姓名` → `holder_name`
- `职务` → `position`
- `变动数` → `change_shares`
- `变动原因` → `reason`
- `变动日期` → `change_date`

**Field Transformations**:
- change_date converted to datetime
- change_shares positive for increase, negative for decrease

## Update Frequency

- **Daily**: Updated when shareholder changes reported
- Historical data available

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
from akshare_one import get_shareholder_changes

# Get all shareholder changes
df = get_shareholder_changes()

# Get changes for specific stock
df = get_shareholder_changes(symbol="600000")

# Get changes in date range
df = get_shareholder_changes(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_shareholder_changes(
    symbol="600000",
    columns=['symbol', 'holder_name', 'change_shares', 'change_date']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name holder_name     position  change_shares     reason change_date
0  600000  浦发银行      张三        董事长         100000    增持计划  2024-01-15
1  600000  浦发银行      李四          董事        -50000    个人资金需求  2024-01-20
```

## Validation Rules

1. **Required Fields**: `symbol`, `holder_name`, `change_date`, `change_shares`
2. **Type Validation**:
   - `change_date`: datetime
   - `change_shares`: float, can be positive or negative
3. **Value Ranges**:
   - change_shares can be any integer

## Error Handling

- **Empty DataFrame**: No changes in period or invalid symbol
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_top_shareholders`: Get top shareholders list
- `get_institution_holdings`: Get institution holdings

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestShareholderContract`

## Notes

- Positive change_shares = increase (增持)
- Negative change_shares = decrease (减持)
- Important for monitoring insider trading activity
- Changes may indicate management confidence