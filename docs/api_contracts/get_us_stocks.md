# API Contract: get_us_stocks

## Overview

**API Function**: `get_us_stocks`

**Purpose**: Get list of US stocks listed on major US exchanges (NYSE, NASDAQ).

**Module**: `akshare_one.modules.hkus`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | US stock symbol (ticker) | `AAPL` |
| `name` | string | - | Company name | `Apple Inc` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `price` | float | USD | Latest price | Most sources |
| `change_pct` | float | percent | Price change % | Most sources |
| `volume` | float | shares | Trading volume | Most sources |
| `market_cap` | float | USD | Market capitalization | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare US stock API):
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `change_pct`
- `成交量` → `volume`
- `总市值` → `market_cap`

**Field Transformations**:
- US ticker format (e.g., AAPL, MSFT)
- Prices in USD

## Update Frequency

- **Daily**: Updated daily
- Coverage of major US stocks

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_us_stocks

# Get US stock list
df = get_us_stocks()

# With column filtering
df = get_us_stocks(
    columns=['symbol', 'name', 'price', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
  symbol          name    price  change_pct      volume      market_cap
0   AAPL    Apple Inc   180.0         2.5  50000000.0  2800000000000.0
1   MSFT  Microsoft    400.0         1.8  30000000.0  2900000000000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, US ticker format
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

- `get_hk_stocks`: Get HK stock list

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestHKUSContract`

## Notes

- US tickers are 1-5 letters (AAPL, MSFT)
- Prices in US Dollars (USD)
- Volume in shares (not hands)
- Coverage may focus on popular stocks
- Use for cross-market comparison