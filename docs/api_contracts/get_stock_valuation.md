# API Contract: get_stock_valuation

## Overview

**API Function**: `get_stock_valuation`

**Purpose**: 获取个股估值数据（PE、PB、PS等）

**Module**: `src.akshare_one.modules.valuation`

**Data Sources**: legu, eastmoney, lixinger

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | 日期 | '2024-03-15' |
| `symbol` | string | - | 股票代码 | '600000' |
| `close` | float | yuan | 收盘价 | 10.25 |
| `pe_ttm` | float | ratio | 市盈率TTM | 8.5 |
| `pe_static` | float | ratio | 静态市盈率 | 9.0 |
| `pb` | float | ratio | 市净率 | 0.8 |
| `ps` | float | ratio | 市销率 | 1.2 |
| `pcf` | float | ratio | 市现率 | 5.5 |
| `peg` | float | ratio | PEG指标 | 0.5 |
| `market_cap` | float | yuan | 总市值 | 3.0e10 |
| `float_market_cap` | float | yuan | 流通市值 | 3.0e10 |

## Optional Fields

- 其他估值相关指标

## Data Source Mapping

### Source: `legu`

**Original Fields**:
- 使用 standardize_and_filter 自动映射

**Field Transformations**:
- 市值单位标准化为元
- 自动标准化字段名称

**Note**: Legu 主要提供市场估值数据，个股估值可能返回空DataFrame

### Source: `eastmoney`

- 提供完整的个股估值数据
- 包含PE、PB、PS等多种估值指标

## Update Frequency

- **Daily**: 每日更新（随股价变化）
- **Historical**: 提供历史估值数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 股票代码 |
| `start_date` | string | no | '1970-01-01' | 开始日期 |
| `end_date` | string | no | '2030-12-31' | 结束日期 |
| `source` | string | no | 'legu' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_stock_valuation

# Basic usage
df = get_stock_valuation(symbol="600000")

# With date range
df = get_stock_valuation(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-03-31"
)
```

## Example Response

```python
         date  symbol  close  pe_ttm  pe_static    pb    ps   pcf  peg    market_cap
0  2024-03-15  600000  10.25    8.5       9.0   0.8  1.2   5.5  0.5      3.0e10
```

## Validation Rules

1. **Required Fields**: 估值指标字段必须存在
2. **Type Validation**:
   - 估值比率 > 0（正常范围）
   - 市值 > 0
3. **Consistency Rules**:
   - PE = close / EPS
   - PB = close / BVPS
   - Market_cap = close * total_shares

## Error Handling

- **Empty DataFrame**: Legu源可能返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_market_valuation`: 市场估值数据
- `get_financial_metrics`: 财务指标
- `get_basic_info`: 股票基础信息

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestStockValuationContract`

## Notes

- PE、PB、PS等估值比率无单位（比值）
- 市值单位为元
- 不同数据源提供的估值指标可能有差异
- Legu主要提供市场估值，个股估值建议使用eastmoney