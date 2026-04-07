# API Contract: get_stock_fund_flow

## Overview

**API Function**: `get_stock_fund_flow`

**Purpose**: Get fund flow data for individual stocks showing capital flow from different investor categories (main force, large/medium/small investors).

**Module**: `akshare_one.modules.fundflow`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `main_net_inflow` | float | yuan | Main force net inflow (主力净流入) | `1234567890` |
| `main_net_inflow_ratio` | float | percent | Main force net inflow ratio (主力净占比) | `5.23` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format
- `string`: Stock symbol in 6-digit format
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元)
- `percent`: Percentage value (can be negative)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `huge_net_inflow` | float | yuan | Super large investor net inflow (超大单净流入) | Most sources |
| `large_net_inflow` | float | yuan | Large investor net inflow (大单净流入) | Most sources |
| `medium_net_inflow` | float | yuan | Medium investor net inflow (中单净流入) | Most sources |
| `small_net_inflow` | float | yuan | Small investor net inflow (小单净流入) | Most sources |
| `retail_net_inflow` | float | yuan | Retail investor net inflow (散户净流入) | Some sources |
| `huge_net_inflow_ratio` | float | percent | Super large investor net inflow ratio | Most sources |
| `large_net_inflow_ratio` | float | percent | Large investor net inflow ratio | Most sources |
| `medium_net_inflow_ratio` | float | percent | Medium investor net inflow ratio | Most sources |
| `small_net_inflow_ratio` | float | percent | Small investor net inflow ratio | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_individual_fund_flow`):
- `日期` → `date`
- `股票代码` → `symbol`
- `主力净流入-净流入` → `main_net_inflow`
- `主力净流入-净占比` → `main_net_inflow_ratio`
- `超大单净流入-净流入` → `huge_net_inflow`
- `超大单净流入-净占比` → `huge_net_inflow_ratio`
- `大单净流入-净流入` → `large_net_inflow`
- `大单净流入-净占比` → `large_net_inflow_ratio`
- `中单净流入-净流入` → `medium_net_inflow`
- `中单净流入-净占比` → `medium_net_inflow_ratio`
- `小单净流入-净流入` → `small_net_inflow`
- `小单净流入-净占比` → `small_net_inflow_ratio`

**Field Transformations**:
- All amounts in yuan (元)
- Ratios as percentages (can be negative)
- Symbol standardized to 6-digit format

## Update Frequency

- **Daily data**: Updated daily after market close
- Historical data available for past trading days

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit code) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_stock_fund_flow

# Basic usage - get fund flow for a stock
df = get_stock_fund_flow(symbol="600000")

# Get data for specific date range
df = get_stock_fund_flow(
    symbol="600000",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering (focus on main force)
df = get_stock_fund_flow(
    symbol="600000",
    columns=['date', 'main_net_inflow', 'main_net_inflow_ratio']
)

# Multi-source version
from akshare_one import get_stock_fund_flow_multi_source
df = get_stock_fund_flow_multi_source(symbol="600000")
```

## Example Response

```python
# Example DataFrame structure
         date  symbol  main_net_inflow  main_net_inflow_ratio  huge_net_inflow  large_net_inflow
0  2024-01-15  600000      1234567890.0                   5.23     800000000.0      434567890.0
1  2024-01-16  600000      -500000000.0                  -2.10    -200000000.0     -300000000.0
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`date`, `symbol`, `main_net_inflow`, `main_net_inflow_ratio`)
2. **Type Validation**:
   - `date`: datetime or string in YYYY-MM-DD format
   - `symbol`: string, 6-digit format
   - Inflow amounts: numeric (float)
   - Ratios: numeric (float, percentage)

3. **Value Ranges**:
   - Net inflow amounts can be positive (inflow) or negative (outflow)
   - Ratios can be positive or negative percentages
   - All amounts in yuan (元)

4. **Consistency Rules**:
   - `main_net_inflow` ≈ `huge_net_inflow` + `large_net_inflow` (if those fields present)
   - Total net inflow should balance across investor categories

## Error Handling

- **Empty DataFrame**: Returned when stock symbol is invalid or no data available
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_sector_fund_flow`: Get fund flow for industry/concept sectors
- `get_main_fund_flow_rank`: Get ranking by main fund flow
- `get_stock_fund_flow_multi_source`: Multi-source version

## Testing

Contract tests for this API are located in:
- `tests/test_api_contract.py::TestFundFlowContract`
- `tests/test_api_field_contracts.py::TestFundFlowContract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- Date/symbol format validation

## Notes

- Main force (主力) = Super large + Large investors (超大单 + 大单)
- Retail (散户) = Medium + Small investors (中单 + 小单)
- Positive net inflow indicates capital inflow, negative indicates outflow
- Net inflow ratio shows percentage relative to total trading amount
- Fund flow data helps track institutional vs retail investor activity
- Data reflects estimated flows based on transaction size classification