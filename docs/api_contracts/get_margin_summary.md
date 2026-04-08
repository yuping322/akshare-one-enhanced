# API Contract: get_margin_summary

## Overview

**API Function**: `get_margin_summary`

**Purpose**: Get market-wide margin financing summary data.

**Module**: `akshare_one.modules.margin`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `market` | string | - | Market identifier | `all` |
| `total_financing_balance` | float | yuan | Total financing balance | `100000000000` |
| `total_margin_balance` | float | yuan | Total margin balance | `50000000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `total_financing_buy` | float | yuan | Total financing buy | Most sources |
| `total_margin_sell` | float | yuan | Total margin sell | Most sources |
| `total_balance` | float | yuan | Total balance (融资融券余额) | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare margin summary API):
- `交易日期` → `date`
- `市场` → `market`
- `融资余额` → `total_financing_balance`
- `融券余额` → `total_margin_balance`
- `融资买入额` → `total_financing_buy`
- `融券卖出额` → `total_margin_sell`
- `融资融券余额` → `total_balance`

**Field Transformations**:
- Date converted to datetime
- All amounts in yuan
- Market parameter filters by exchange

## Update Frequency

- **Daily**: Updated after market close
- Historical summary data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `market` | string | no | `all` | Market filter ('sh', 'sz', 'all') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_margin_summary

# Get margin summary for all markets
df = get_margin_summary()

# Get margin summary for Shanghai market
df = get_margin_summary(market="sh")

# Get margin summary in date range
df = get_margin_summary(
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_margin_summary(
    columns=['date', 'total_financing_balance', 'total_margin_balance', 'total_balance']
)
```

## Example Response

```python
# Example DataFrame structure
         date market  total_financing_balance  total_margin_balance   total_balance
0  2024-01-15    all            100000000000.0          50000000000.0  150000000000.0
```

## Validation Rules

1. **Required Fields**: `date`, `market`, `total_financing_balance`, `total_margin_balance`
2. **Type Validation**:
   - `date`: datetime
   - All balances: float, positive

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_margin_data`: Get individual stock margin data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMarginContract`

## Notes

- Market-wide margin statistics
- Total balance = financing + margin balance
- High total balance = high market leverage
- Rising balance = increasing risk appetite
- market='sh' for Shanghai, 'sz' for Shenzhen
- Monitor for extreme leverage levels
- Important market sentiment indicator
- Compare with historical levels