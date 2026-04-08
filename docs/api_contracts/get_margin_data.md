# API Contract: get_margin_data

## Overview

**API Function**: `get_margin_data`

**Purpose**: Get margin financing data (融资融券) for stocks.

**Module**: `akshare_one.modules.margin`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `financing_balance` | float | yuan | Financing balance (融资余额) | `1000000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `financing_buy` | float | yuan | Financing buy amount (融资买入) | Most sources |
| `financing_repay` | float | yuan | Financing repay amount (融资偿还) | Most sources |
| `margin_balance` | float | yuan | Margin balance (融券余额) | Most sources |
| `margin_sell` | float | shares | Margin sell volume (融券卖出) | Some sources |
| `margin_repay` | float | shares | Margin repay volume (融券偿还) | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare margin data API):
- `交易日期` → `date`
- `证券代码` → `symbol`
- `融资余额` → `financing_balance`
- `融资买入额` → `financing_buy`
- `融资偿还额` → `financing_repay`
- `融券余额` → `margin_balance`
- `融券卖出量` → `margin_sell`
- `融券偿还量` → `margin_repay`

**Field Transformations**:
- Date converted to datetime
- All amounts in yuan
- Margin volumes in shares

## Update Frequency

- **Daily**: Updated after market close
- Historical margin data available

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
from akshare_one import get_margin_data

# Get all margin data
df = get_margin_data()

# Get margin data for specific stock
df = get_margin_data(symbol="600000")

# Get margin data in date range
df = get_margin_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_margin_data(
    symbol="600000",
    columns=['date', 'financing_balance', 'financing_buy', 'margin_balance']
)
```

## Example Response

```python
# Example DataFrame structure
         date  symbol  financing_balance  financing_buy  financing_repay  margin_balance
0  2024-01-15  600000       1000000000.0    50000000.0      30000000.0    100000000.0
```

## Validation Rules

1. **Required Fields**: `date`, `symbol`, `financing_balance`
2. **Type Validation**:
   - `date`: datetime
   - All balances: float, positive
   - Transaction amounts: float

## Error Handling

- **Empty DataFrame**: No margin data or invalid symbol
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_margin_summary`: Get market-wide margin summary

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMarginContract`

## Notes

- Margin financing = borrowing to buy stocks
- Margin balance = borrowed shares to sell short
- High financing balance = bullish sentiment
- High margin balance = bearish sentiment
- Track changes for sentiment shifts
- Important for leverage analysis
- Compare financing buy vs repay for flows
- Rising balance indicates increasing leverage