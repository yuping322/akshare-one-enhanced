# 融资融券（MarginFinancing）

融资融券模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：T+1  
**示例程序**：[examples/margin_example.py](../../examples/margin_example.py)

## 导入方式

```python
from akshare_one.modules.margin import (
    get_margin_data,
    get_margin_summary
)
```

## 接口列表

### get_margin_data

获取融资融券数据。

**功能描述**：查询指定股票或全市场的融资融券数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str \| None | 否 | None | 股票代码（None表示全市场） | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| margin_balance | float | 融资余额（元） | 500000000.0 |
| margin_buy | float | 融资买入额（元） | 10000000.0 |
| short_balance | float | 融券余额（元） | 50000000.0 |
| short_sell_volume | float | 融券卖出量（股） | 1000000.0 |
| total_balance | float | 融资融券余额（元） | 550000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.margin import get_margin_data

# 获取浦发银行的融资融券数据
df = get_margin_data("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_margin_summary

获取融资融券汇总。

**功能描述**：查询沪深市场或全市场的融资融券汇总数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| market | Literal["sh", "sz", "all"] | 否 | "all" | 市场类型 | "all" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| market | str | 市场类型 | "all" |
| margin_balance | float | 融资余额（元） | 15000000000.0 |
| short_balance | float | 融券余额（元） | 1500000000.0 |
| total_balance | float | 融资融券余额（元） | 16500000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.margin import get_margin_summary

# 获取全市场融资融券汇总数据
df = get_margin_summary(start_date="2024-01-01", end_date="2024-01-31", market="all")
print(df.head())
```