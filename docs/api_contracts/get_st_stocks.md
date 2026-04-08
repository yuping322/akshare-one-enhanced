# API Contract: get_st_stocks

## Overview

**API Function**: `get_st_stocks`

**Purpose**: Get list of ST (Special Treatment) stocks - stocks with special risk warnings.

**Module**: `akshare_one.modules.st`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name (includes ST prefix) | `ST某某` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `st_type` | string | - | ST type (ST/*ST/ST*) | Most sources |
| `st_reason` | string | - | Reason for ST status | Most sources |
| `price` | float | yuan | Latest price | Some sources |
| `change_pct` | float | percent | Price change % | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare ST stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `ST类型` → `st_type`
- `ST原因` → `st_reason`

**Field Transformations**:
- Name includes ST prefix (ST, *ST)
- Standard field names

## Update Frequency

- **Daily**: Updated daily
- ST status changes announced publicly

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_st_stocks

# Get ST stocks list
df = get_st_stocks()

# With column filtering
df = get_st_stocks(
    columns=['symbol', 'name', 'st_type', 'st_reason']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name st_type      st_reason
0  600000  ST某某      ST     连续两年亏损
1  000001  *ST某某     *ST     财务异常
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, 6-digit
   - Name contains ST prefix
   - `st_type`: string (ST/*ST/ST*)

## Error Handling

- **Empty DataFrame**: No ST stocks or API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_suspended_stocks`: Get suspended stocks
- `get_st_delist_data`: Get ST/delist risk data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestSTContract`

## Notes

- ST = Special Treatment (风险警示)
- *ST = more severe risk
- Reasons: 连续亏损, 财务异常, 其他风险
- ST stocks have trading restrictions
- Daily price movement limited to ±5%
- High risk, avoid if possible
- Monitor for removal from ST status