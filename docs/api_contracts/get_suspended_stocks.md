# API Contract: get_suspended_stocks

## Overview

**API Function**: `get_suspended_stocks`

**Purpose**: Get list of suspended/halted stocks (停牌股票).

**Module**: `akshare_one.modules.suspended`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |
| `suspend_date` | datetime | - | Suspension start date | `2024-01-15` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `suspend_reason` | string | - | Suspension reason | Most sources |
| `expected_resume_date` | datetime | - | Expected resume date | Some sources |
| `suspend_type` | string | - | Suspension type | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare suspended stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `停牌日期` → `suspend_date`
- `停牌原因` → `suspend_reason`
- `预计复牌日期` → `expected_resume_date`

**Field Transformations**:
- Dates converted to datetime
- Standard field names

## Update Frequency

- **Daily**: Updated daily
- Real-time suspension status

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_suspended_stocks

# Get suspended stocks list
df = get_suspended_stocks()

# With column filtering
df = get_suspended_stocks(
    columns=['symbol', 'name', 'suspend_date', 'suspend_reason']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name suspend_date          suspend_reason expected_resume_date
0  600000  浦发银行   2024-01-15      重大事项未公告               2024-01-20
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `suspend_date`
2. **Type Validation**:
   - `symbol`: string, 6-digit
   - `suspend_date`: datetime
   - Dates in YYYY-MM-DD format

## Error Handling

- **Empty DataFrame**: No suspended stocks or API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_st_stocks`: Get ST stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestSuspendedContract`

## Notes

- Stocks suspended for various reasons
- Common reasons: 重大事项, 资产重组, 异常波动
- Expected resume date may be estimated
- Suspended stocks cannot be traded
- Check before placing orders