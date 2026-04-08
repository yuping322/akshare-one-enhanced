# API Contract: get_northbound_top_stocks

## Overview

**API Function**: `get_northbound_top_stocks`

**Purpose**: Get ranking of stocks by northbound capital holdings.

**Module**: `akshare_one.modules.northbound`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `rank` | float | - | Ranking position | `1` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `northbound_net_buy` | float | yuan | Recent net buy amount | Most sources |
| `holdings_shares` | float | shares | Shares held by northbound | Most sources |
| `holdings_ratio` | float | percent | Holdings % of float shares | Most sources |
| `date` | datetime | - | Query date | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_hsgt_hold_stock_em`):
- `代码` → `symbol`
- `名称` → `name`
- `今日持股-市值` → used for ranking
- `今日持股-股数` → `holdings_shares`
- `今日持股-占流通股比` → `holdings_ratio`

**Field Transformations**:
- Ranked by holdings value
- Standard field names

## Update Frequency

- **Daily**: Updated daily
- Latest ranking based on current holdings

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | no | None | Query date (YYYY-MM-DD), None for latest |
| `market` | string | no | `all` | Market filter ('sh', 'sz', 'all') |
| `top_n` | int | no | `100` | Number of top stocks to return |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_northbound_top_stocks

# Get top stocks by northbound holdings
df = get_northbound_top_stocks(date="2024-01-15")

# Get top 50 stocks for Shanghai market
df = get_northbound_top_stocks(
    date="2024-01-15",
    market="sh",
    top_n=50
)

# Get latest top stocks (current data)
df = get_northbound_top_stocks()

# With column filtering
df = get_northbound_top_stocks(
    date="2024-01-15",
    columns=['rank', 'symbol', 'name', 'holdings_ratio']
)
```

## Example Response

```python
# Example DataFrame structure
   rank  symbol     name  northbound_net_buy  holdings_shares  holdings_ratio        date
0   1.0  600000  浦发银行       100000000.0      500000000.0             5.0  2024-01-15
1   2.0  000001  平安银行        80000000.0      400000000.0             4.5  2024-01-15
```

## Validation Rules

1. **Required Fields**: `rank`, `symbol`, `name`
2. **Type Validation**:
   - `rank`: float, positive
   - `holdings_shares`: float, positive
   - `holdings_ratio`: float, 0-100

## Error Handling

- **Empty DataFrame**: Invalid date or no data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_northbound_holdings`: Get detailed holdings
- `get_northbound_flow`: Get capital flow

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestNorthboundContract`

## Notes

- Ranking by holdings value
- Top stocks favored by foreign investors
- Useful for identifying quality stocks
- Compare ranking changes over time
- Market parameter filters by exchange
- northbound_net_buy shows recent activity