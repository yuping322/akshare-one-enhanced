# API Contract: get_st_delist_data

## Overview

**API Function**: `get_st_delist_data`

**Purpose**: Get ST (Special Treatment) and delisting risk data.

**Module**: `akshare_one.modules.disclosure`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `ST某某` |
| `risk_type` | string | - | Risk type | `ST` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `risk_reason` | string | - | Reason for risk status | Most sources |
| `announcement_date` | datetime | - | Announcement date | Most sources |
| `delist_date` | datetime | - | Delisting date (if applicable) | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare ST/delist API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `风险类型` → `risk_type`
- `风险原因` → `risk_reason`
- `公告日期` → `announcement_date`
- `退市日期` → `delist_date`

**Field Transformations**:
- Dates converted to datetime
- Standard field names

## Update Frequency

- **Daily**: Updated with status changes
- Real-time risk status tracking

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Stock symbol (if None, returns all) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_st_delist_data

# Get all ST/delist risk data
df = get_st_delist_data()

# Get risk data for specific stock
df = get_st_delist_data(symbol="600000")

# With column filtering
df = get_st_delist_data(
    columns=['symbol', 'name', 'risk_type', 'risk_reason']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name risk_type        risk_reason announcement_date
0  600000  ST某某        ST      连续两年亏损       2024-01-15
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `risk_type`
2. **Type Validation**:
   - `risk_type`: string (ST/*ST/退市整理/终止上市)
   - Dates: datetime

## Error Handling

- **Empty DataFrame**: No ST/delist stocks or invalid symbol
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_st_stocks`: Get ST stocks list

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDisclosureContract`

## Notes

- risk_type values: ST, *ST, 退市整理, 终止上市
- *ST = higher risk than ST
- 退市整理 = delisting process
- 终止上市 = delisted
- Avoid high-risk stocks
- Monitor for risk removal
- Important for risk management
- Check before investing