# API Contract: get_income_statement

## Overview

**API Function**: `get_income_statement`

**Purpose**: 获取利润表数据

**Module**: `src.akshare_one.modules.financial`

**Data Sources**: sina, eastmoney_direct, cninfo

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `report_date` | datetime | - | 报告日期 | '2024-03-31' |

**收入类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `revenue` | float | yuan | 营业收入 |
| `operating_revenue` | float | yuan | 主营业务收入 |

**成本类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `total_operating_costs` | float | yuan | 营业总成本 |
| `cost_of_revenue` | float | yuan | 营业成本 |
| `selling_expenses` | float | yuan | 销售费用 |
| `administrative_expenses` | float | yuan | 管理费用 |
| `financial_expenses` | float | yuan | 财务费用 |
| `research_and_development` | float | yuan | 研发费用 |

**利润类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `operating_profit` | float | yuan | 营业利润 |
| `net_income` | float | yuan | 净利润 |
| `income_tax_expense` | float | yuan | 所得税费用 |
| `investment_income` | float | yuan | 投资收益 |
| `ebit` | float | yuan | 息税前利润 |

**每股指标**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `earnings_per_share` | float | yuan/股 | 每股收益 |
| `earnings_per_share_diluted` | float | yuan/股 | 稀释每股收益 |

## Optional Fields

- 其他收入明细项
- 其他成本费用明细项
- 其他综合收益项目

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 使用 map_source_fields 自动映射
- 中文字段映射为英文标准字段

**Field Transformations**:
- 金额单位为元（yuan）
- 自动计算 EBIT 等衍生指标

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
from akshare_one import get_income_statement

# Basic usage
df = get_income_statement(symbol="600600")

# Filter specific columns
df = get_income_statement(
    symbol="600600",
    columns=['report_date', 'revenue', 'net_income', 'earnings_per_share']
)
```

## Example Response

```python
  report_date     revenue  net_income  earnings_per_share
0  2024-03-31   5.0e9      8.0e8      0.50
1  2023-12-31   4.8e9      7.5e8      0.45
```

## Validation Rules

1. **Required Fields**: report_date 必须存在
2. **Type Validation**: 金额字段为数值
3. **Consistency Rules**:
   - operating_profit ≈ revenue - total_operating_costs
   - net_income ≈ operating_profit - income_tax_expense
   - 所有收入类字段 >= 0
   - EPS > 0（盈利公司）

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 抛出 ValueError

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_balance_sheet`: 资产负债表
- `get_cash_flow`: 现金流量表
- `get_financial_metrics`: 财务指标汇总

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestIncomeStatementContract`

## Notes

- 所有金额单位为元（yuan）
- EPS单位为元/股
- 报告日期格式为 YYYY-MM-DD