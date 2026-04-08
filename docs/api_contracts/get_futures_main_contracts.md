# API Contract: get_futures_main_contracts

## Overview

**API Function**: `get_futures_main_contracts`

**Purpose**: 获取期货主力合约列表

**Module**: `src.akshare_one.modules.futures`

**Data Sources**: sina

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 期货代码 | 'AG' |
| `name` | string | - | 期货名称 | '白银' |
| `contract` | string | - | 主力合约代码 | 'AG2406' |
| `exchange` | string | - | 交易所 | 'SHFE' |

## Optional Fields

无额外可选字段。

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 通过 get_main_contracts 方法获取
- 自动标准化字段名称

**Field Transformations**:
- 提取主力合约信息
- 添加交易所字段

## Update Frequency

- **Daily**: 每日更新（主力合约变更）
- **Historical**: 提供主力合约变更历史

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | 'sina' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_futures_main_contracts

# Get main contracts list
df = get_futures_main_contracts()
```

## Example Response

```python
  symbol    name contract exchange
0    AG    白银   AG2406    SHFE
1    AU    黄金   AU2406    SHFE
2    CU      铜   CU2405    SHFE
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 有效期货代码
   - `contract`: YYMM格式的合约代码
   - `exchange`: 交易所代码（SHFE, DCE, CZCE, CFFEX, INE）

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_futures_hist_data`: 期货历史数据
- `get_futures_realtime_data`: 期货实时行情

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestFuturesMainContractsContract`

## Notes

- 主力合约按月份滚动（如AG2406表示2024年6月）
- 交易所代码：
  - SHFE: 上海期货交易所
  - DCE: 大连商品交易所
  - CZCE: 郑州商品交易所
  - CFFEX: 中国金融期货交易所
  - INE: 上海国际能源交易中心