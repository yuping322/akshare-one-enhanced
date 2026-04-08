# API Contract: get_pmi_index

## Overview

**API Function**: `get_pmi_index`

**Purpose**: Get PMI (Purchasing Managers' Index) data.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Report date | `2024-01-31` |
| `pmi` | float | - | PMI index value | `50.5` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `production_index` | float | - | Production sub-index | Most sources |
| `new_orders_index` | float | - | New orders sub-index | Most sources |
| `employment_index` | float | - | Employment sub-index | Some sources |
| `inventory_index` | float | - | Inventory sub-index | Some sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from NBS official data):
- `月份` → `date`
- `PMI` → `pmi`
- `生产` → `production_index`
- `新订单` → `new_orders_index`
- `从业人员` → `employment_index`
- `产成品库存` → `inventory_index`

**Field Transformations**:
- Date converted to datetime (month-end)
- Index values as numeric

## Update Frequency

- **Monthly**: Released on last day of month
- Historical PMI data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `pmi_type` | string | no | `manufacturing` | PMI type ('manufacturing', 'non_manufacturing', 'caixin') |
| `source` | string | no | `official` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_pmi_index

# Get manufacturing PMI
df = get_pmi_index()

# Get non-manufacturing PMI
df = get_pmi_index(pmi_type="non_manufacturing")

# Get Caixin PMI
df = get_pmi_index(pmi_type="caixin")

# Get PMI for specific period
df = get_pmi_index(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_pmi_index(
    columns=['date', 'pmi', 'production_index', 'new_orders_index']
)
```

## Example Response

```python
# Example DataFrame structure
         date   pmi  production_index  new_orders_index
0  2024-01-31  50.5              52.0              51.0
```

## Validation Rules

1. **Required Fields**: `date`, `pmi`
2. **Type Validation**:
   - `date`: datetime
   - PMI values: float, typically 40-60 range
3. **PMI Interpretation**:
   - PMI > 50 = expansion
   - PMI < 50 = contraction
   - PMI = 50 = breakeven

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_cpi_data`: Get CPI data
- `get_ppi_data`: Get PPI data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- PMI = Purchasing Managers' Index
- manufacturing PMI = factory activity
- non_manufacturing PMI = service sector
- caixin PMI = private survey (different methodology)
- Key leading economic indicator
- Above 50 = economy expanding
- Below 50 = economy contracting
- Watch trends over time
- Sub-indices provide detailed insights