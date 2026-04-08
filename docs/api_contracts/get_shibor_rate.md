# API Contract: get_shibor_rate

## Overview

**API Function**: `get_shibor_rate`

**Purpose**: Get Shibor (Shanghai Interbank Offered Rate) interest rate data.

**Module**: `akshare_one.modules.macro`

**Data Sources**: `official`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Rate date | `2024-01-15` |
| `shibor_on` | float | percent | Overnight Shibor rate | `1.80` |
| `shibor_1w` | float | percent | 1-week Shibor rate | `2.00` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `shibor_2w` | float | percent | 2-week Shibor rate | Most sources |
| `shibor_1m` | float | percent | 1-month Shibor rate | Most sources |
| `shibor_3m` | float | percent | 3-month Shibor rate | Most sources |
| `shibor_6m` | float | percent | 6-month Shibor rate | Some sources |
| `shibor_1y` | float | percent | 1-year Shibor rate | Some sources |

## Data Source Mapping

### Source: `official`

**Original Fields** (from Shibor official data):
- `日期` → `date`
- `隔夜` → `shibor_on`
- `1周` → `shibor_1w`
- `2周` → `shibor_2w`
- `1个月` → `shibor_1m`
- `3个月` → `shibor_3m`
- `6个月` → `shibor_6m`
- `1年` → `shibor_1y`

**Field Transformations**:
- Date converted to datetime
- All rates as percentages

## Update Frequency

- **Daily**: Published every trading day at 11:30 AM
- Historical Shibor data available

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
from akshare_one import get_shibor_rate

# Get Shibor rates
df = get_shibor_rate()

# Get Shibor for specific period
df = get_shibor_rate(
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_shibor_rate(
    columns=['date', 'shibor_on', 'shibor_1w', 'shibor_3m']
)
```

## Example Response

```python
# Example DataFrame structure
         date  shibor_on  shibor_1w  shibor_1m  shibor_3m
0  2024-01-15       1.80       2.00       2.30       2.50
```

## Validation Rules

1. **Required Fields**: `date`, `shibor_on`, `shibor_1w`
2. **Type Validation**:
   - `date`: datetime
   - All rates: float, positive

## Error Handling

- **Empty DataFrame**: No data in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_lpr_rate`: Get LPR rates
- `get_m2_supply`: Get M2 money supply

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestMacroContract`

## Notes

- Shibor = Shanghai Interbank Offered Rate (上海银行间同业拆放利率)
- Benchmark for interbank lending
- Overnight rate = shortest term
- 3-month rate = commonly used benchmark
- High rates = tight liquidity
- Low rates = ample liquidity
- Compare overnight vs 3-month for yield curve
- Spike in rates indicates liquidity stress
- Important for money market analysis