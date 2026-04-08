# API Contract: get_etf_list

## Overview

**API Function**: `get_etf_list`

**Purpose**: 获取ETF/LOF/REITs基金列表

**Module**: `src.akshare_one.modules.etf`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 基金代码 | '510300' |
| `name` | string | - | 基金名称 | '300ETF' |
| `type` | string | - | 基金类型 | 'etf' |

## Optional Fields

无额外可选字段。

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- `代码` → `symbol`
- `名称` → `name`

**Field Transformations**:
- 自动添加 type 字段，标识为 'etf'

## Update Frequency

- **Daily**: 每日更新
- **Historical**: 提供历史完整列表

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fund_type` | string | no | 'etf' | 基金类型 ('etf', 'lof', 'reits', 'all') |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_etf_list

# Get ETF list
df = get_etf_list()

# Get all fund types
df = get_etf_list(fund_type='all')
```

## Example Response

```python
   symbol    name   type
0  510300  300ETF    etf
1  510050   50ETF    etf
2  160105   LOF基金  lof
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 6位数字字符串
   - `type`: 'etf', 'lof', 'reits', 'all' 之一

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_etf_realtime_data`: ETF实时行情
- `get_etf_hist_data`: ETF历史数据
- `get_fund_manager_info`: 基金经理信息

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestETFListContract`

## Notes

- fund_type 参数决定返回的基金类型
- 支持别名 get_fund_list