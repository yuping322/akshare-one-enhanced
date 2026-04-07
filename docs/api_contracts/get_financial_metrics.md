# API Contract: get_financial_metrics

## Overview

**API Function**: `get_financial_metrics`

**Purpose**: Get key financial metrics from three major financial statements (balance sheet, income statement, cash flow) aggregated into a single view.

**Module**: `akshare_one.modules.financial`

**Data Sources**: `eastmoney_direct`, `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response (though exact fields depend on data availability).

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `report_date` | datetime | - | Financial report date | `2023-12-31` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |

**Note**: Financial metrics vary by company and period. The API returns available metrics dynamically.

### Common Financial Metrics (Examples)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `total_revenue` | float | yuan | Total revenue (营业总收入) | `1234567890.0` |
| `net_profit` | float | yuan | Net profit (净利润) | `234567890.0` |
| `total_assets` | float | yuan | Total assets (资产总计) | `5000000000.0` |
| `total_liabilities` | float | yuan | Total liabilities (负债合计) | `3000000000.0` |
| `net_cash_flow` | float | yuan | Net cash flow from operating activities | `123456789.0` |

### Field Types

- `datetime`: Report date in YYYY-MM-DD format (quarterly or annual)
- `string`: Stock symbol in 6-digit format
- `float`: Financial amounts in yuan (元)
- `yuan`: Chinese Yuan (元) - all monetary values

## Optional Fields

The following fields MAY be present depending on company and report period.

| Category | Field Examples | Description |
|----------|----------------|-------------|
| **Balance Sheet** | `total_assets`, `total_liabilities`, `total_equity`, `current_assets`, `current_liabilities` | Asset and liability metrics |
| **Income Statement** | `total_revenue`, `operating_profit`, `net_profit`, `ebit`, `eps` | Revenue and profit metrics |
| **Cash Flow** | `operating_cash_flow`, `investing_cash_flow`, `financing_cash_flow`, `free_cash_flow` | Cash flow metrics |
| **Ratios** | `roe`, `roa`, `debt_ratio`, `current_ratio`, `gross_margin`, `net_margin` | Financial ratios (percentages) |

## Data Source Mapping

### Source: `eastmoney_direct`

**Original Fields** (from eastmoney financial statements API):
- `报告期` → `report_date`
- Field names vary based on financial statement type
- All amounts in yuan (元)

**Field Transformations**:
- Multiple financial statement fields merged into single response
- Standardized field names to English
- Amounts preserved in yuan

### Source: `sina`

**Original Fields**:
- Similar structure to eastmoney
- Field names standardized

## Update Frequency

- **Quarterly reports**: Available after quarterly report publication (季报)
- **Annual reports**: Available after annual report publication (年报)
- **Semi-annual reports**: Available after semi-annual publication (半年报)
- Update timing depends on company disclosure schedule

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit code) |
| `source` | string | no | `eastmoney_direct` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_financial_metrics

# Basic usage - get financial metrics for a stock
df = get_financial_metrics(symbol="600000")

# With column filtering (focus on key metrics)
df = get_financial_metrics(
    symbol="600000",
    columns=['report_date', 'total_revenue', 'net_profit', 'total_assets']
)

# With specific source
df = get_financial_metrics(symbol="600000", source="sina")

# Multi-source version
from akshare_one import get_financial_metrics_multi_source
df = get_financial_metrics_multi_source(symbol="600000")
```

## Example Response

```python
# Example DataFrame structure
  report_date     symbol  total_revenue     net_profit    total_assets  total_liabilities      roe
0  2023-12-31    600000  1234567890.0    234567890.0   5000000000.0    3000000000.0         10.5
1  2023-09-30    600000   987654321.0    187654321.0   4800000000.0    2900000000.0         9.8
2  2023-06-30    600000   654321098.0    123456789.0   4500000000.0    2800000000.0         8.5
```

## Validation Rules

1. **Required Fields**: `report_date` and `symbol` MUST be present
2. **Type Validation**:
   - `report_date`: datetime or string in YYYY-MM-DD format
   - `symbol`: string, 6-digit format
   - All amounts: numeric (float), in yuan

3. **Value Ranges**:
   - Report date must be valid historical date
   - Financial amounts can be positive or negative (losses)
   - Ratio fields typically in percentage format (e.g., ROE = 10.5 means 10.5%)

4. **Consistency Rules**:
   - Balance sheet: `total_assets` = `total_liabilities` + `total_equity` (if all present)
   - Cash flow: `net_cash_flow` should sum three activity components

## Error Handling

- **Empty DataFrame**: Returned when no financial data available or invalid symbol
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_balance_sheet`: Get detailed balance sheet data
- `get_income_statement`: Get detailed income statement data
- `get_cash_flow`: Get detailed cash flow statement data
- `get_financial_metrics_multi_source`: Multi-source version

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestFinancialMetricsContract`

Test coverage includes:
- Required field presence (`report_date`, `symbol`)
- Field type validation
- Value range validation
- Report date format validation

## Notes

- Financial metrics come from quarterly, semi-annual, and annual reports
- Report dates typically: 03-31, 06-30, 09-30, 12-31
- Different companies disclose different metrics - field set is dynamic
- All monetary amounts in yuan (元)
- Ratio metrics (ROE, ROA, margins) typically in percentage format
- Historical reports may have different field availability
- Newly listed companies may have limited historical data
- Some fields may be null/NaN if not disclosed by company