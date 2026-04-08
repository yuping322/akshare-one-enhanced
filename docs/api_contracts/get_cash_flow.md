# API Contract: get_cash_flow

## Overview

**API Function**: `get_cash_flow`

**Purpose**: 获取现金流量表数据

**Module**: `src.akshare_one.modules.financial`

**Data Sources**: sina, eastmoney_direct, cninfo

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `report_date` | datetime | - | 报告日期 | '2024-03-31' |

**经营活动现金流**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `net_cash_flow_from_operations` | float | yuan | 经营活动现金流量净额 |
| `cash_from_sales` | float | yuan | 销售商品收到的现金 |
| `total_cash_inflow_from_operations` | float | yuan | 经营活动现金流入小计 |
| `total_cash_outflow_from_operations` | float | yuan | 经营活动现金流出小计 |

**投资活动现金流**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `net_cash_flow_from_investing` | float | yuan | 投资活动现金流量净额 |
| `capital_expenditure` | float | yuan | 资本性支出 |
| `cash_from_investment_recovery` | float | yuan | 投资收回的现金 |
| `total_cash_inflow_from_investing` | float | yuan | 投资活动现金流入小计 |
| `total_cash_outflow_from_investing` | float | yuan | 投资活动现金流出小计 |

**筹资活动现金流**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `net_cash_flow_from_financing` | float | yuan | 筹资活动现金流量净额 |
| `total_cash_inflow_from_financing` | float | yuan | 筹资活动现金流入小计 |
| `total_cash_outflow_from_financing` | float | yuan | 筹资活动现金流出小计 |

**现金余额**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `beginning_cash_balance` | float | yuan | 期初现金余额 |
| `ending_cash_balance` | float | yuan | 期末现金余额 |
| `change_in_cash_and_equivalents` | float | yuan | 现金及现金等价物净增加额 |

## Optional Fields

- 其他现金流明细项
- 税费相关现金流项

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 使用 map_source_fields 自动映射
- 中文字段映射为英文标准字段

**Field Transformations**:
- 金额单位为元（yuan）
- 日期格式标准化

## Update Frequency

- **Quarterly**: 季度更新（03-31, 06-30, 09-30, 12-31）
- **Historical**: 提供历史所有季度数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 股票代码 |
| `source` | string | no | 'sina' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_cash_flow

# Basic usage
df = get_cash_flow(symbol="600600")

# Filter specific columns
df = get_cash_flow(
    symbol="600600",
    columns=['report_date', 'net_cash_flow_from_operations', 'ending_cash_balance']
)
```

## Example Response

```python
  report_date  net_cash_flow_from_operations  ending_cash_balance
0  2024-03-31                      1.5e8              8.0e8
1  2023-12-31                      1.2e8              7.5e8
```

## Validation Rules

1. **Required Fields**: report_date 必须存在
2. **Type Validation**: 金额字段为数值
3. **Consistency Rules**:
   - net_cash_flow = inflow - outflow（各项活动）
   - ending_balance ≈ beginning_balance + net_change
   - 总现金净变化 = 经营 + 投资 + 筹资净流量

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 抛出 ValueError

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_balance_sheet`: 资产负债表
- `get_income_statement`: 利润表
- `get_financial_metrics`: 财务指标汇总

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestCashFlowContract`

## Notes

- 所有金额单位为元（yuan）
- 现金流量表反映现金收支情况
- 报告日期格式为 YYYY-MM-DD