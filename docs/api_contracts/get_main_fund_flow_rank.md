# API Contract: get_main_fund_flow_rank

## Overview

**API Function**: `get_main_fund_flow_rank`

**Purpose**: Get ranking of stocks by main fund flow indicators.

**Module**: `akshare_one.modules.fundflow`

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
| `main_net_inflow` | float | yuan | Main force net inflow | Most sources |
| `main_net_inflow_ratio` | float | percent | Main force net inflow % | Most sources |
| `change_pct` | float | percent | Stock price change % | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare main fund flow rank API):
- `排名` → `rank`
- `代码` → `symbol`
- `名称` → `name`
- `主力净流入` → `main_net_inflow`
- `主力净占比` → `main_net_inflow_ratio`
- `涨跌幅` → `change_pct`

**Field Transformations**:
- Ranked by selected indicator
- Standard field names

## Update Frequency

- **Daily**: Updated after market close
- Ranking changes daily

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | yes | - | Query date (YYYY-MM-DD) |
| `indicator` | string | no | `main_net_inflow` | Ranking indicator ('main_net_inflow', 'main_net_inflow_ratio') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_main_fund_flow_rank

# Get stocks ranked by main net inflow
df = get_main_fund_flow_rank(date="2024-01-15")

# Get stocks ranked by inflow ratio
df = get_main_fund_flow_rank(
    date="2024-01-15",
    indicator="main_net_inflow_ratio"
)

# With column filtering
df = get_main_fund_flow_rank(
    date="2024-01-15",
    columns=['rank', 'symbol', 'name', 'main_net_inflow']
)
```

## Example Response

```python
# Example DataFrame structure
   rank  symbol     name  main_net_inflow  main_net_inflow_ratio  change_pct
0   1.0  600000  浦发银行     500000000.0                   10.0         5.0
1   2.0  000001  平安银行     300000000.0                    8.0         3.0
```

## Validation Rules

1. **Required Fields**: `rank`, `symbol`, `name`
2. **Type Validation**:
   - `rank`: float, positive
   - `main_net_inflow`: float
   - `main_net_inflow_ratio`: float

## Error Handling

- **Empty DataFrame**: Invalid date or no data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_stock_fund_flow`: Get individual stock fund flow
- `get_sector_fund_flow`: Get sector fund flow

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestFundFlowContract`

## Notes

- Indicator determines ranking criterion
- 'main_net_inflow' = rank by absolute amount
- 'main_net_inflow_ratio' = rank by percentage
- Top stocks indicate institutional interest
- Useful for identifying strong/weak stocks
- Combine with price performance analysis