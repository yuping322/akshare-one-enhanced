# 限售解禁（RestrictedRelease）

限售解禁模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：T+1  
**示例程序**：[examples/restricted_example.py](../../examples/restricted_example.py)

## 导入方式

```python
from akshare_one.modules.restricted import (
    get_restricted_release,
    get_restricted_release_calendar
)
```

## 接口列表

### get_restricted_release

获取限售解禁数据。

**功能描述**：查询指定股票或全市场的限售股解禁明细数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str \| None | 否 | None | 股票代码（None表示全市场） | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| release_date | str | 解禁日期（YYYY-MM-DD） | "2024-06-15" |
| release_shares | float | 解禁股数（股） | 100000000.0 |
| release_value | float | 解禁市值（元） | 1200000000.0 |
| release_type | str | 解禁类型 | "首发原股东限售股份" |
| shareholder_name | str | 股东名称 | "某某公司" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.restricted import get_restricted_release

# 获取浦发银行的解禁数据
df = get_restricted_release("600000", start_date="2024-01-01", end_date="2024-12-31")
print(df.head())
```

### get_restricted_release_calendar

获取解禁日历。

**功能描述**：查询指定时间范围内的解禁日历汇总数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 解禁日期（YYYY-MM-DD） | "2024-06-15" |
| release_stock_count | int | 解禁股票数量 | 50 |
| total_release_value | float | 总解禁市值（元） | 50000000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.restricted import get_restricted_release_calendar

# 获取2024年的解禁日历
df = get_restricted_release_calendar("2024-01-01", "2024-12-31")
print(df.head())
```