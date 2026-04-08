# API Contract: get_market_valuation

## Overview

**API Function**: `get_market_valuation`

**Purpose**: 获取市场整体估值数据（如上证指数PE/PB历史）

**Module**: `src.akshare_one.modules.valuation`

**Data Sources**: legu

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | 日期 | '2024-03-15' |
| `index_name` | string | - | 指数名称 | '上证指数' |

**估值指标字段**:
| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `pe_ttm` | float | ratio | 市盈率TTM |
| `pe_static` | float | ratio | 静态市盈率 |
| `pb` | float | ratio | 市净率 |

## Optional Fields

- 其他估值指标
- 其他市场指数数据

## Data Source Mapping

### Source: `legu`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 数据来自乐咕乐股网站

**Field Transformations**:
- 自动添加 index_name 字段
- 自动标准化字段名称

## Update Frequency

- **Daily**: 每日更新
- **Historical**: 提供完整历史数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | 'legu' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_market_valuation

# Get market valuation data
df = get_market_valuation()

# With filtering
df = get_market_valuation(
    columns=['date', 'index_name', 'pe_ttm', 'pb']
)
```

## Example Response

```python
         date   index_name  pe_ttm     pb
0  2024-03-15     上证指数    12.5   1.2
1  2024-03-14     上证指数    12.3   1.19
```

## Validation Rules

1. **Required Fields**: date 必须存在
2. **Type Validation**:
   - 估值比率 > 0
   - 日期格式为 YYYY-MM-DD
3. **Consistency Rules**:
   - 市场估值比率应在合理范围内

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_stock_valuation`: 个股估值数据
- `get_index_hist_data`: 指数历史数据
- `get_index_realtime_data`: 指数实时数据

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestMarketValuationContract`

## Notes

- 数据源为乐咕乐股（legu）
- 主要提供上证指数的历史估值数据
- 估值比率反映市场整体估值水平
- 可用于判断市场估值高低