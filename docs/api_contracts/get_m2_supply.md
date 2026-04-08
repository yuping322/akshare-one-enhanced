# API Contract: get_m2_supply

## Overview

**API Function**: `get_m2_supply`

**Purpose**: Get M2 money supply data.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Report date | `2024-01-31` |
| `m2` | float | yuan | M2 money supply | `290000000000000` |
| `m2_yoy` | float | percent | M2 year-over-year growth | `9.5` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `m1` | float | yuan | M1 money supply | Most sources |
| `m1_yoy` | float | percent | M1 year-over-year growth | Most sources |
| `m0` | float | yuan | M0 money supply (currency in circulation) | Some sources |
| `m0_yoy` | float | percent | M0 year-over-year growth | Some sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from PBoC official data):
- `月份` → `date`
- `货币和准货币(M2)` → `m2`
- `M2同比增长` → `m2_yoy`
- `货币(M1)` → `m1`
- `M1同比增长` → `m1_yoy`
- `流通中货币(M0)` → `m0`
- `M0同比增长` → `m0_yoy`

**Field Transformations**:
- Date converted to datetime (month-end)
- Money supply in yuan
- Growth rates as percentages

## Update Frequency

- **Monthly**: Released around 10th-15th of following month
- Historical money supply data available

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
from akshare_one import get_m2_supply

# Get M2 money supply data
df = get_m2_supply()

# Get M2 for specific period
df = get_m2_supply(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_m2_supply(
    columns=['date', 'm2', 'm2_yoy', 'm1_yoy']
)
```

## Example Response

```python
# Example DataFrame structure
         date            m2  m2_yoy            m1  m1_yoy
0  2024-01-31  290000000000000    9.5  70000000000000    5.0
```

## Validation Rules

1. **Required Fields**: `date`, `m2`, `m2_yoy`
2. **Type Validation**:
   - `date`: datetime
   - Money supply: float, positive
   - Growth rates: float

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_social_financing`: Get social financing data
- `get_lpr_rate`: Get LPR rates

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- M2 = broad money supply (货币供应量)
- M1 = narrow money (checking deposits)
- M0 = currency in circulation
- M2 growth shows monetary policy stance
- High M2 growth = expansionary policy
- Low M2 growth = tight policy
- M1-M2剪刀头 indicates economic activity
- Compare with GDP growth for money velocity
- Important for understanding liquidity