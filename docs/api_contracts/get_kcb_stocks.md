# API Contract: get_kcb_stocks

## Overview

**API Function**: `get_kcb_stocks`

**Purpose**: Get list of stocks listed on Shanghai STAR Market (科创板/KCB).

**Module**: `akshare_one.modules.board`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit, starts with 688) | `688001` |
| `name` | string | - | Stock name | `华兴源创` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `price` | float | yuan | Latest price | Most sources |
| `change_pct` | float | percent | Price change % | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `listing_date` | datetime | - | Listing date | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare KCB stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `change_pct`
- `成交量` → `volume`
- `上市日期` → `listing_date`

**Field Transformations**:
- Symbol starts with 688 (KCB prefix)
- Standard field names

## Update Frequency

- **Daily**: Updated daily
- Complete STAR Market coverage

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_kcb_stocks

# Get STAR Market stocks
df = get_kcb_stocks()

# With column filtering
df = get_kcb_stocks(
    columns=['symbol', 'name', 'price', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name    price  change_pct      volume listing_date
0  688001  华兴源创    50.0         5.0   100000.0   2019-07-22
1  688002  神工股份    30.0         3.0    50000.0   2019-07-23
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, starts with 688
   - `price`: float, positive

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_cyb_stocks`: Get ChiNext stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestBoardContract`

## Notes

- KCB = 科创板 (STAR Market)
- Stock symbols start with 688
- Focus on tech and innovation companies
- Special trading rules (different price limits)
- Higher risk due to new market
- Started in July 2019
- Important for tech sector analysis