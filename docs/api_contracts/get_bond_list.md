# API Contract: get_bond_list

## Overview

**API Function**: `get_bond_list`

**Purpose**: 获取可转债列表

**Module**: `src.akshare_one.modules.bond`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `bond_code` | string | - | 债券代码 | '110001' |
| `bond_name` | string | - | 债券名称 | '招路转债' |
| `stock_code` | string | - | 正股代码 | '600000' |
| `stock_name` | string | - | 正股名称 | '招商公路' |
| `issue_date` | datetime | - | 发行日期 | '2024-03-01' |
| `maturity_date` | datetime | - | 到期日期 | '2029-03-01' |
| `coupon_rate` | float | percent | 票面利率 | 0.5 |

## Optional Fields

- `issue_amount`: 发行规模（元）
- `conversion_price`: 转股价（元）
- `current_price`: 现价（元）

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 中文字段映射为英文标准字段

**Field Transformations**:
- 票面利率单位为百分比
- 自动标准化字段名称

## Update Frequency

- **Daily**: 每日更新（新发行债券）
- **Historical**: 提供历史债券列表

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_bond_list

# Get convertible bond list
df = get_bond_list()
```

## Example Response

```python
  bond_code  bond_name stock_code stock_name  issue_date maturity_date coupon_rate
0   110001   招路转债     600000    招商公路  2024-03-01   2029-03-01      0.5
1   110002   招商转债     600036    招商银行  2024-02-01   2029-02-01      0.3
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `bond_code`: 6位数字字符串
   - `coupon_rate` >= 0
3. **Consistency Rules**:
   - maturity_date > issue_date

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_bond_hist_data`: 可转债历史数据
- `get_bond_realtime_data`: 可转债实时行情

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestBondListContract`

## Notes

- 可转债代码为6位数字
- 票面利率单位为百分比（如0.5表示0.5%）
- 到期日期应大于发行日期