# API Contract: get_balance_sheet

## Overview

**API Function**: `get_balance_sheet`

**Purpose**: 获取资产负债表数据

**Module**: `src.akshare_one.modules.financial`

**Data Sources**: sina, eastmoney_direct, cninfo

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `report_date` | datetime | - | 报告日期 | '2024-03-31' |
| `date` | datetime | - | 日期（同report_date） | '2024-03-31' |
| `currency` | string | - | 货币单位 | 'CNY' |

**资产类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `total_assets` | float | yuan | 资产总计 |
| `current_assets` | float | yuan | 流动资产合计 |
| `cash_and_equivalents` | float | yuan | 货币资金 |
| `inventory` | float | yuan | 存货 |
| `accounts_receivable` | float | yuan | 应收账款 |
| `non_current_assets` | float | yuan | 非流动资产合计 |
| `fixed_assets_net` | float | yuan | 固定资产净值 |
| `goodwill` | float | yuan | 商誉 |
| `intangible_assets` | float | yuan | 无形资产 |

**负债类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `total_liabilities` | float | yuan | 负债合计 |
| `current_liabilities` | float | yuan | 流动负债合计 |
| `non_current_liabilities` | float | yuan | 非流动负债合计 |
| `current_debt` | float | yuan | 短期借款 |
| `non_current_debt` | float | yuan | 长期借款 |

**权益类字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `shareholders_equity` | float | yuan | 股东权益合计 |
| `minority_interest` | float | yuan | 少数股东权益 |

**财务比率**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `current_ratio` | float | ratio | 流动比率 |
| `debt_to_assets` | float | ratio | 资产负债率 |

## Optional Fields

- 其他资产明细项（根据公司实际情况）
- 其他负债明细项
- 其他权益明细项

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 使用 map_source_fields 自动映射
- 原始字段为中文（如 "资产总计" → "total_assets"）

**Field Transformations**:
- 金额字段单位为元（yuan）
- 计算财务比率（current_ratio, debt_to_assets）

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
from akshare_one import get_balance_sheet

# Basic usage
df = get_balance_sheet(symbol="600600")

# With column filtering
df = get_balance_sheet(
    symbol="600600",
    columns=['report_date', 'total_assets', 'total_liabilities', 'shareholders_equity']
)
```

## Example Response

```python
  report_date  total_assets  total_liabilities  shareholders_equity
0  2024-03-31      1.5e10            8.0e9             7.0e9
1  2023-12-31      1.4e10            7.5e9             6.5e9
```

## Validation Rules

1. **Required Fields**: report_date 必须存在
2. **Type Validation**: 金额字段为数值
3. **Consistency Rules**:
   - total_assets = current_assets + non_current_assets
   - total_liabilities = current_liabilities + non_current_liabilities
   - total_assets = total_liabilities + shareholders_equity + minority_interest

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 抛出 ValueError

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_income_statement`: 利润表
- `get_cash_flow`: 现金流量表
- `get_financial_metrics`: 财务指标汇总

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestBalanceSheetContract`

## Notes

- 所有金额单位为元（yuan）
- 报告日期格式为 YYYY-MM-DD
- 财务比率由系统自动计算