# API Contract: get_dividend_data

## Overview

**API Function**: `get_dividend_data`

**Purpose**: Get dividend distribution data for stocks.

**Module**: `akshare_one.modules.disclosure`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `report_date` | datetime | - | Report period date | `2023-12-31` |
| `dividend_amount` | float | yuan | Dividend per share | `0.50` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `ex_dividend_date` | datetime | - | Ex-dividend date | Most sources |
| `pay_date` | datetime | - | Payment date | Some sources |
| `dividend_yield` | float | percent | Dividend yield | Some sources |
| `dividend_type` | string | - | Dividend type (现金/股票) | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare dividend API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `报告期` → `report_date`
- `分红金额` → `dividend_amount`
- `除权除息日` → `ex_dividend_date`
- `派息日` → `pay_date`
- `股息率` → `dividend_yield`

**Field Transformations**:
- Dates converted to datetime
- Dividend amount per share in yuan

## Update Frequency

- **Quarterly**: Updated with financial reports
- Annual dividend announcements

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
from akshare_one import get_dividend_data

# Get all dividend data
df = get_dividend_data()

# Get dividend data for specific stock
df = get_dividend_data(symbol="600000")

# Get dividends in date range
df = get_dividend_data(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_dividend_data(
    symbol="600000",
    columns=['symbol', 'name', 'dividend_amount', 'dividend_yield']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name report_date  dividend_amount ex_dividend_date   pay_date  dividend_yield
0  600000  浦发银行  2023-12-31             0.50       2024-06-15  2024-06-20            5.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `report_date`, `dividend_amount`
2. **Type Validation**:
   - Dates: datetime
   - `dividend_amount`: float, positive
   - `dividend_yield`: float, 0-100

## Error Handling

- **Empty DataFrame**: No dividend data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_disclosure_news`: Get disclosure announcements
- `get_repurchase_data`: Get repurchase data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDisclosureContract`

## Notes

- dividend_amount = dividend per share
- dividend_yield = annual dividend / stock price
- Higher yield may indicate undervaluation
- Ex-dividend date important for traders
- Must own stock before ex-dividend date
- Compare dividend history for consistency
- Important for income investors