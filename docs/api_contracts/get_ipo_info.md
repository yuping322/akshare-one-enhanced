# API Contract: get_ipo_info

## Overview

**API Function**: `get_ipo_info`

**Purpose**: Get detailed IPO information including upcoming and recent IPOs.

**Module**: `akshare_one.modules.ipo`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `某某股份` |
| `ipo_status` | string | - | IPO status | `已上市` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `listing_date` | datetime | - | Expected/actual listing date | Most sources |
| `ipo_price` | float | yuan | IPO offering price | Most sources |
| `subscription_date` | datetime | - | Subscription date | Some sources |
| `issue_amount` | float | shares | Shares to be issued | Some sources |
| `pe_ratio` | float | ratio | IPO PE ratio | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare IPO info API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `上市状态` → `ipo_status`
- `上市日期` → `listing_date`
- `发行价` → `ipo_price`
- `申购日期` → `subscription_date`
- `发行量` → `issue_amount`
- `发行市盈率` → `pe_ratio`

**Field Transformations**:
- Dates converted to datetime
- Standard field names

## Update Frequency

- **Daily**: Updated with IPO progress
- Tracks IPO lifecycle

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_ipo_info

# Get IPO information
df = get_ipo_info()

# With column filtering
df = get_ipo_info(
    columns=['symbol', 'name', 'ipo_status', 'listing_date', 'ipo_price']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name ipo_status listing_date  ipo_price subscription_date  issue_amount  pe_ratio
0  600000  某某股份       已上市   2024-01-15      10.0        2024-01-10   100000000.0      20.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `ipo_status`
2. **Type Validation**:
   - Dates: datetime
   - Monetary values: float
   - `pe_ratio`: float, positive

## Error Handling

- **Empty DataFrame**: No IPO data or API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_new_stocks`: Get newly listed stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestIPOContract`

## Notes

- IPO statuses: 已上市, 待上市, 申购中, 已过会, etc.
- Tracks full IPO process from approval to listing
- Subscription date for retail investors
- PE ratio shows valuation at offering
- Useful for tracking upcoming IPOs
- Compare PE with industry average