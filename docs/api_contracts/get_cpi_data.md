# API Contract: get_cpi_data

## Overview

**API Function**: `get_cpi_data`

**Purpose**: Get CPI (Consumer Price Index) inflation data.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Report date | `2024-01-31` |
| `cpi_yoy` | float | percent | CPI year-over-year change | `2.1` |
| `cpi_mom` | float | percent | CPI month-over-month change | `0.3` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `food_cpi_yoy` | float | percent | Food CPI yoy | Most sources |
| `non_food_cpi_yoy` | float | percent | Non-food CPI yoy | Most sources |
| `core_cpi_yoy` | float | percent | Core CPI yoy (excluding food & energy) | Some sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from NBS official data):
- `月份` → `date`
- `全国当月同比` → `cpi_yoy`
- `全国环比` → `cpi_mom`
- `食品同比` → `food_cpi_yoy`
- `非食品同比` → `non_food_cpi_yoy`

**Field Transformations**:
- Date converted to datetime (month-end)
- All values as percentages

## Update Frequency

- **Monthly**: Released around 10th of following month
- Historical CPI data available

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
from akshare_one import get_cpi_data

# Get CPI data
df = get_cpi_data()

# Get CPI for specific period
df = get_cpi_data(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_cpi_data(
    columns=['date', 'cpi_yoy', 'cpi_mom']
)
```

## Example Response

```python
# Example DataFrame structure
         date  cpi_yoy  cpi_mom  food_cpi_yoy  non_food_cpi_yoy
0  2024-01-31      2.1      0.3           5.0               1.0
```

## Validation Rules

1. **Required Fields**: `date`, `cpi_yoy`, `cpi_mom`
2. **Type Validation**:
   - `date`: datetime
   - All CPI values: float
   - Percentages can be negative (deflation)

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_ppi_data`: Get PPI data
- `get_pmi_index`: Get PMI data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- CPI = Consumer Price Index (消费者物价指数)
- Measures consumer inflation
- yoy = year-over-year (同比)
- mom = month-over-month (环比)
- Food prices often volatile
- Core CPI excludes volatile items
- High CPI = high inflation
- Low/negative CPI = low inflation/deflation
- Important for monetary policy
- Target typically around 3%