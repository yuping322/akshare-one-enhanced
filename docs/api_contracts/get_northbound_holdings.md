# API Contract: get_northbound_holdings

## Overview

**API Function**: `get_northbound_holdings`

**Purpose**: Get northbound capital holdings details for stocks - showing foreign investor positions.

**Module**: `akshare_one.modules.northbound`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `date` | datetime | - | Holdings date | `2024-01-15` |
| `holdings_shares` | float | shares | Number of shares held | `500000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `holdings_value` | float | yuan | Value of holdings | Most sources |
| `holdings_ratio` | float | percent | Holdings % of total shares | Most sources |
| `holdings_change` | float | shares | Change in holdings | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_hsgt_individual_em`):
- `代码` → `symbol`
- `日期` / `持股日期` → `date`
- `持股数量` / `持股数量(股)` → `holdings_shares`
- `持股市值` / `持股市值(元)` → `holdings_value`
- `持股占比` / `持股占比(%)` → `holdings_ratio`
- `持股变化` / `持股数量增减` → `holdings_change`

**Field Transformations**:
- Symbol standardized to 6-digit
- Holdings values in yuan
- Holdings ratio as percentage

## Update Frequency

- **Daily**: Updated daily after market close
- Historical holdings available

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
from akshare_one import get_northbound_holdings

# Get northbound holdings for a stock
df = get_northbound_holdings(symbol="600000")

# Get holdings for all stocks
df = get_northbound_holdings()

# Get holdings in date range
df = get_northbound_holdings(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_northbound_holdings(
    symbol="600000",
    columns=['symbol', 'date', 'holdings_shares', 'holdings_ratio']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol        date  holdings_shares  holdings_value  holdings_ratio  holdings_change
0  600000  2024-01-15      500000000.0     5000000000.0             5.0       10000000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `date`, `holdings_shares`
2. **Type Validation**:
   - `date`: datetime
   - `holdings_shares`: float, positive
   - `holdings_ratio`: float, 0-100

## Error Handling

- **Empty DataFrame**: Invalid symbol or no data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_northbound_flow`: Get northbound capital flow
- `get_northbound_top_stocks`: Get top stocks by holdings

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestNorthboundContract`

## Notes

- Northbound capital = foreign investors via HK-SH/SZ connect
- Holdings show foreign investor positions
- Changes indicate foreign investor sentiment
- Important for tracking smart money
- Large holdings may indicate quality stocks
- Compare with historical holdings for trends