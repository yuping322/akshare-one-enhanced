# API Contract: get_social_financing

## Overview

**API Function**: `get_social_financing`

**Purpose**: Get social financing scale data (社会融资规模).

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Report date | `2024-01-31` |
| `total_financing` | float | yuan | Total social financing stock | `350000000000000` |
| `monthly_addition` | float | yuan | Monthly new financing | `5000000000000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `bank_loans` | float | yuan | Bank loans (人民币贷款) | Most sources |
| `bond_financing` | float | yuan | Bond financing (企业债券) | Most sources |
| `stock_financing` | float | yuan | Stock financing (非金融企业股票) | Some sources |
| `yoy_growth` | float | percent | Year-over-year growth | Some sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from PBoC official data):
- `月份` → `date`
- `社会融资规模存量` → `total_financing`
- `社会融资规模增量` → `monthly_addition`
- `人民币贷款` → `bank_loans`
- `企业债券` → `bond_financing`
- `非金融企业境内股票` → `stock_financing`
- `同比增长` → `yoy_growth`

**Field Transformations**:
- Date converted to datetime (month-end)
- All monetary values in yuan
- Growth rate as percentage

## Update Frequency

- **Monthly**: Released around 10th-15th of following month
- Historical social financing data available

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
from akshare_one import get_social_financing

# Get social financing data
df = get_social_financing()

# Get data for specific period
df = get_social_financing(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_social_financing(
    columns=['date', 'monthly_addition', 'bank_loans', 'yoy_growth']
)
```

## Example Response

```python
# Example DataFrame structure
         date      total_financing  monthly_addition     bank_loans  yoy_growth
0  2024-01-31  350000000000000  5000000000000  4000000000000        9.5
```

## Validation Rules

1. **Required Fields**: `date`, `total_financing`, `monthly_addition`
2. **Type Validation**:
   - `date`: datetime
   - Monetary values: float
   - Growth rate: float

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_m2_supply`: Get M2 money supply
- `get_lpr_rate`: Get LPR rates

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- Social financing = broad measure of credit
- Includes bank loans, bonds, stocks, etc.
- Total financing = stock (存量)
- Monthly addition = flow (增量)
- Key indicator of credit conditions
- High growth = expansionary credit
- Bank loans usually largest component
- Compare with GDP for credit intensity
- Important for understanding financial conditions
- Watch for shifts in financing structure