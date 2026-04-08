# API Contract: get_new_stocks

## Overview

**API Function**: `get_new_stocks`

**Purpose**: Get list of newly listed stocks (新股) - recent IPO listings.

**Module**: `akshare_one.modules.ipo`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `某某股份` |
| `listing_date` | datetime | - | Listing date | `2024-01-15` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `ipo_price` | float | yuan | IPO offering price | Most sources |
| `issue_amount` | float | shares | Shares issued | Most sources |
| `raise_amount` | float | yuan | Total raised capital | Most sources |
| `industry` | string | - | Industry classification | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare new stocks API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `上市日期` → `listing_date`
- `发行价` → `ipo_price`
- `发行量` → `issue_amount`
- `募集资金` → `raise_amount`
- `行业` → `industry`

**Field Transformations**:
- Listing date converted to datetime
- All monetary values in yuan
- Issue amount in shares

## Update Frequency

- **Daily**: Updated with new listings
- Historical IPO data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_new_stocks

# Get newly listed stocks
df = get_new_stocks()

# With column filtering
df = get_new_stocks(
    columns=['symbol', 'name', 'listing_date', 'ipo_price']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name listing_date  ipo_price  issue_amount    raise_amount     industry
0  600000  某某股份   2024-01-15      10.0   100000000.0  1000000000.0      科技行业
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `listing_date`
2. **Type Validation**:
   - `listing_date`: datetime
   - `ipo_price`: float, positive
   - Issue/raise amounts: float, positive

## Error Handling

- **Empty DataFrame**: No recent IPOs or API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_ipo_info`: Get detailed IPO information

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestIPOContract`

## Notes

- Shows recent/new listings
- IPO price may differ from opening price
- New stocks may have special trading rules
- First few days: no price limits in some cases
- Monitor listing date for trading opportunities
- Issue amount shows offering size