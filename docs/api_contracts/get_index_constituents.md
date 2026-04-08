# API Contract: get_index_constituents

## Overview

**API Function**: `get_index_constituents`

**Purpose**: 获取指数成分股及权重

**Module**: `src.akshare_one.modules.index`

**Data Sources**: eastmoney (via CSIndex)

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 成分股代码 | '600000' |
| `name` | string | - | 成分股名称 | '浦发银行' |
| `weight` | float | percent | 权重百分比 | 1.5 |

## Optional Fields

- `market`: 市场（上海/深圳）
- 其他成分股属性字段

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 原始数据来自 CSIndex (中证指数公司)

**Field Transformations**:
- 权重单位为百分比
- 自动标准化字段名称

## Update Frequency

- **Quarterly**: 季度更新（成分股调整）
- **Historical**: 提供历史成分股列表

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 指数代码 |
| `include_weight` | boolean | no | True | 是否包含权重 |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_index_constituents

# Get constituents with weights
df = get_index_constituents(symbol="000300")

# Get constituents without weights
df = get_index_constituents(symbol="000300", include_weight=False)
```

## Example Response

```python
   symbol      name  weight
0  600000   浦发银行     1.5
1  600036   招商银行     2.3
2  601318   中国平安     3.8
```

## Validation Rules

1. **Required Fields**: symbol, name 必须存在
2. **Type Validation**:
   - `symbol`: 6位数字字符串
   - `weight`: 0-100 范围
3. **Consistency Rules**:
   - 权重总和 ≈ 100%（考虑精度误差）

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame（含默认列）
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_index_list`: 指数列表
- `get_index_hist_data`: 指数历史数据
- `get_index_realtime_data`: 指数实时数据

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestIndexConstituentsContract`

## Notes

- 权重单位为百分比（如1.5表示1.5%）
- 成分股列表每季度调整
- 数据源为 CSIndex (中证指数公司)