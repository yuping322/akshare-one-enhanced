# API Contract: get_hk_stocks

## Overview

**API Function**: `get_hk_stocks`

**Purpose**: Get list of Hong Kong stocks listed on HKEX.

**Module**: `akshare_one.modules.hkus`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | HK stock symbol (5-digit) | `00700` |
| `name` | string | - | Stock name | `腾讯控股` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `price` | float | HKD | Latest price | Most sources |
| `change_pct` | float | percent | Price change % | Most sources |
| `volume` | float | hands | Trading volume | Most sources |
| `market_cap` | float | HKD | Market capitalization | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare HK stock API):
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `change_pct`
- `成交量` → `volume`
- `总市值` → `market_cap`

**Field Transformations**:
- Symbol in 5-digit HK format (with leading zeros)
- Prices in HKD

## Update Frequency

- **Daily**: Updated daily
- Complete HK market coverage

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_hk_stocks

# Get HK stock list
df = get_hk_stocks()

# With column filtering
df = get_hk_stocks(
    columns=['symbol', 'name', 'price', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
  symbol       name    price  change_pct      volume      market_cap
0  00700     腾讯控股   380.0         2.5  10000000.0  3600000000000.0
1  09988     阿里巴巴   100.0         1.8   5000000.0  2000000000000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, 5-digit HK format
   - `price`: float, positive
   - `volume`: float, positive

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_us_stocks`: Get US stock list

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestHKUSContract`

## Notes

- HK stock symbols are 5-digit
- Leading zeros important (00700 not 700)
- Prices in Hong Kong Dollars (HKD)
- Includes mainland companies (H-shares)
- Use for cross-market analysis