# API Contract: get_performance_express

## Overview

**API Function**: `get_performance_express`

**Purpose**: Get performance express data (业绩快报) - preliminary financial results before formal reports.

**Module**: `akshare_one.modules.performance`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |
| `report_date` | string | - | Report period date | `20231231` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `revenue` | float | yuan | Total revenue | Most sources |
| `revenue_change` | float | percent | Revenue change % | Most sources |
| `net_profit` | float | yuan | Net profit | Most sources |
| `net_profit_change` | float | percent | Net profit change % | Most sources |
| `announcement_date` | datetime | - | Announcement date | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare performance express API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `报告期` → `report_date`
- `营业收入` → `revenue`
- `营业收入变动幅度` → `revenue_change`
- `净利润` → `net_profit`
- `净利润变动幅度` → `net_profit_change`
- `公告日期` → `announcement_date`

**Field Transformations**:
- Report date in YYYYMMDD format
- All monetary values in yuan

## Update Frequency

- **Quarterly**: Published during earnings season
- Usually released 1-2 weeks before formal report

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | yes | - | Report period date (YYYYMMDD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_performance_express

# Get performance express for Q4 2023
df = get_performance_express(date="20231231")

# With column filtering
df = get_performance_express(
    date="20231231",
    columns=['symbol', 'name', 'revenue', 'net_profit', 'net_profit_change']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name report_date        revenue  revenue_change      net_profit  net_profit_change  announcement_date
0  600000  浦发银行    20231231  50000000000.0            10.0   5000000000.0               15.0         2024-01-10
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `report_date`
2. **Type Validation**:
   - `report_date`: string, YYYYMMDD format
   - Monetary values: float
   - Change percentages: float

## Error Handling

- **Empty DataFrame**: No express reports for that period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_performance_forecast`: Get performance forecasts
- `get_financial_metrics`: Get actual financial metrics
- `get_income_statement`: Get formal income statement

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestPerformanceContract`

## Notes

- Express reports are preliminary, may differ from final
- Released earlier than formal quarterly reports
- Useful for early earnings insights
- Compare with forecast data for accuracy