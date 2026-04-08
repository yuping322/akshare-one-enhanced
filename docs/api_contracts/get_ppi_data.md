# API Contract: get_ppi_data

## Overview

**API Function**: `get_ppi_data`

**Purpose**: Get PPI (Producer Price Index) data for industrial prices.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Report date | `2024-01-31` |
| `ppi_yoy` | float | percent | PPI year-over-year change | `-2.5` |
| `ppi_mom` | float | percent | PPI month-over-month change | `-0.3` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `production_material_ppi` | float | percent | Production material PPI | Most sources |
| `consumer_goods_ppi` | float | percent | Consumer goods PPI | Most sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from NBS official data):
- `月份` → `date`
- `当月同比` → `ppi_yoy`
- `环比` → `ppi_mom`
- `生产资料` → `production_material_ppi`
- `生活资料` → `consumer_goods_ppi`

**Field Transformations**:
- Date converted to datetime (month-end)
- All values as percentages

## Update Frequency

- **Monthly**: Released with CPI data
- Historical PPI data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `official` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_ppi_data

# Get PPI data
df = get_ppi_data()

# Get PPI for specific period
df = get_ppi_data(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_ppi_data(
    columns=['date', 'ppi_yoy', 'ppi_mom']
)
```

## Example Response

```python
# Example DataFrame structure
         date  ppi_yoy  ppi_mom  production_material_ppi  consumer_goods_ppi
0  2024-01-31     -2.5     -0.3                    -3.0                -1.0
```

## Validation Rules

1. **Required Fields**: `date`, `ppi_yoy`, `ppi_mom`
2. **Type Validation**:
   - `date`: datetime
   - All PPI values: float
   - Values can be negative (deflation)

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_cpi_data`: Get CPI data
- `get_pmi_index`: Get PMI data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- PPI = Producer Price Index (生产者物价指数)
- Measures factory-gate prices
- Leading indicator for CPI
- Negative PPI = industrial deflation
- Positive PPI = inflation
- Production material more volatile
- Consumer goods more stable
- Affects corporate profits
- Watch for trends in PPI
- Compare with CPI for price transmission