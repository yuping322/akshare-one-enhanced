# API Contract: get_performance_forecast

## Overview

**API Function**: `get_performance_forecast`

**Purpose**: Get performance forecast data (业绩预告) for listed companies.

**Module**: `akshare_one.modules.performance`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |
| `forecast_type` | string | - | Forecast type (预增/预减/扭亏等) | `预增` |
| `report_date` | string | - | Report period date | `20231231` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `net_profit_min` | float | yuan | Minimum net profit forecast | Most sources |
| `net_profit_max` | float | yuan | Maximum net profit forecast | Most sources |
| `net_profit_change_min` | float | percent | Minimum profit change % | Most sources |
| `net_profit_change_max` | float | percent | Maximum profit change % | Most sources |
| `announcement_date` | datetime | - | Announcement date | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare performance forecast API):
- `股票代码` → `symbol`
- `股票简称` → `name`
- `预告类型` → `forecast_type`
- `报告期` → `report_date`
- `预测净利润最小值` → `net_profit_min`
- `预测净利润最大值` → `net_profit_max`
- `预测净利润变动幅度最小值` → `net_profit_change_min`
- `预测净利润变动幅度最大值` → `net_profit_change_max`
- `公告日期` → `announcement_date`

**Field Transformations**:
- Report date in YYYYMMDD format
- Profit values in yuan

## Update Frequency

- **Quarterly**: Updated during earnings season
- Historical forecasts available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | yes | - | Report period date (YYYYMMDD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_performance_forecast

# Get performance forecasts for Q4 2023
df = get_performance_forecast(date="20231231")

# With column filtering
df = get_performance_forecast(
    date="20231231",
    columns=['symbol', 'name', 'forecast_type', 'net_profit_change_min']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name forecast_type report_date  net_profit_min  net_profit_max  net_profit_change_min  net_profit_change_max  announcement_date
0  600000  浦发银行         预增    20231231      500000000.0    600000000.0                    50.0                   70.0         2024-01-15
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`, `forecast_type`, `report_date`
2. **Type Validation**:
   - `report_date`: string, YYYYMMDD format
   - Profit values: float
   - Change percentages: float

## Error Handling

- **Empty DataFrame**: No forecasts for that period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_performance_express`: Get performance express data
- `get_financial_metrics`: Get actual financial metrics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestPerformanceContract`

## Notes

- Forecast types: 预增, 预减, 扭亏, 续盈, 续亏, etc.
- Useful for earnings expectations
- Compare forecasts with actual results later
- Important for investment decisions