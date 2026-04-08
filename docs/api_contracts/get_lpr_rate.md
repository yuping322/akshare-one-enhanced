# API Contract: get_lpr_rate

## Overview

**API Function**: `get_lpr_rate`

**Purpose**: Get LPR (Loan Prime Rate) interest rate data from PBoC.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Rate effective date | `2024-01-15` |
| `lpr_1y` | float | percent | 1-year LPR rate | `3.45` |
| `lpr_5y` | float | percent | 5-year LPR rate | `4.20` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `lpr_1y_change` | float | bp | 1-year LPR change (basis points) | Most sources |
| `lpr_5y_change` | float | bp | 5-year LPR change (basis points) | Most sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from PBoC official data):
- `日期` → `date`
- `1年期LPR` → `lpr_1y`
- `5年期LPR` → `lpr_5y`

**Field Transformations**:
- Date converted to datetime
- Rates as percentages
- Change in basis points (1 bp = 0.01%)

## Update Frequency

- **Monthly**: LPR announced monthly (usually 20th)
- Historical rates available

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
from akshare_one import get_lpr_rate

# Get LPR rate history
df = get_lpr_rate()

# Get LPR rates for specific period
df = get_lpr_rate(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# With column filtering
df = get_lpr_rate(
    columns=['date', 'lpr_1y', 'lpr_5y']
)
```

## Example Response

```python
# Example DataFrame structure
         date  lpr_1y  lpr_5y  lpr_1y_change  lpr_5y_change
0  2024-01-20    3.45    4.20            0.0            0.0
1  2024-02-20    3.45    3.95            0.0          -25.0
```

## Validation Rules

1. **Required Fields**: `date`, `lpr_1y`, `lpr_5y`
2. **Type Validation**:
   - `date`: datetime
   - Rates: float, positive
   - Changes: float (can be negative)

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_shibor_rate`: Get Shibor rates
- `get_pmi_index`: Get PMI data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- LPR = Loan Prime Rate (贷款市场报价利率)
- Benchmark for loan rates
- 1-year LPR affects short-term loans
- 5-year LPR affects mortgages
- Rate cuts = expansionary policy
- Rate hikes = contractionary policy
- Important for financial analysis
- Affects bond and stock markets