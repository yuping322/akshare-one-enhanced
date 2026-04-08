# API Contract: get_cyb_stocks

## Overview

**API Function**: `get_cyb_stocks`

**Purpose**: Get list of stocks listed on ChiNext (创业板/CYB).

**Module**: `akshare_one.modules.board`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit, starts with 300) | `300001` |
| `name` | string | - | Stock name | `特锐德` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `price` | float | yuan | Latest price | Most sources |
| `change_pct` | float | percent | Price change % | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `listing_date` | datetime | - | Listing date | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare CYB stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `change_pct`
- `成交量` → `volume`
- `上市日期` → `listing_date`

**Field Transformations**:
- Symbol starts with 300 (CYB prefix)
- Standard field names

## Update Frequency

- **Daily**: Updated daily
- Complete ChiNext coverage

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_cyb_stocks

# Get ChiNext stocks
df = get_cyb_stocks()

# With column filtering
df = get_cyb_stocks(
    columns=['symbol', 'name', 'price', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name    price  change_pct      volume listing_date
0  300001    特锐德    20.0         5.0   200000.0   2009-10-30
1  300002    神州泰岳    15.0         3.0   100000.0   2009-10-30
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, starts with 300
   - `price`: float, positive

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_kcb_stocks`: Get STAR Market stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestBoardContract`

## Notes

- CYB = 创业板 (ChiNext)
- Stock symbols start with 300
- Focus on growth and innovation companies
- Started in October 2009
- Higher growth potential, higher risk
- Important for growth stock analysis
- Many tech and biotech companies listed here