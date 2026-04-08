# API Contract: get_sector_fund_flow

## Overview

**API Function**: `get_sector_fund_flow`

**Purpose**: Get fund flow data for industry and concept sectors.

**Module**: `akshare_one.modules.fundflow`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `sector_code` | string | - | Sector code | `BK0001` |
| `sector_name` | string | - | Sector name | `人工智能` |
| `main_net_inflow` | float | yuan | Main force net inflow | `500000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `main_net_inflow_ratio` | float | percent | Main force net inflow % | Most sources |
| `huge_net_inflow` | float | yuan | Super large investor inflow | Most sources |
| `retail_net_inflow` | float | yuan | Retail investor inflow | Most sources |
| `change_pct` | float | percent | Sector index change % | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare sector fund flow API):
- `日期` → `date`
- `板块代码` → `sector_code`
- `板块名称` → `sector_name`
- `主力净流入` → `main_net_inflow`
- `主力净占比` → `main_net_inflow_ratio`

**Field Transformations**:
- Date converted to datetime
- All amounts in yuan

## Update Frequency

- **Daily**: Updated daily after market close
- Historical sector fund flow available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sector_type` | string | yes | - | Sector type ('industry' or 'concept') |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_sector_fund_flow

# Get industry sector fund flow
df = get_sector_fund_flow(sector_type="industry")

# Get concept sector fund flow
df = get_sector_fund_flow(sector_type="concept")

# Get specific date range
df = get_sector_fund_flow(
    sector_type="industry",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_sector_fund_flow(
    sector_type="industry",
    columns=['date', 'sector_name', 'main_net_inflow', 'main_net_inflow_ratio']
)
```

## Example Response

```python
# Example DataFrame structure
         date sector_code sector_name  main_net_inflow  main_net_inflow_ratio
0  2024-01-15      BK0001      人工智能      500000000.0                   5.0
1  2024-01-15      BK0002        新能源      300000000.0                   3.5
```

## Validation Rules

1. **Required Fields**: `date`, `sector_code`, `sector_name`, `main_net_inflow`
2. **Type Validation**:
   - `date`: datetime
   - `main_net_inflow`: float
   - Percentages: float

## Error Handling

- **Empty DataFrame**: No data for period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_stock_fund_flow`: Get individual stock fund flow
- `get_main_fund_flow_rank`: Get main fund flow ranking

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestFundFlowContract`

## Notes

- sector_type: 'industry' for industry sectors, 'concept' for concept sectors
- Positive inflow = capital flowing into sector
- Useful for sector rotation analysis
- Compare inflows across sectors for allocation
- Main force = institutional investors