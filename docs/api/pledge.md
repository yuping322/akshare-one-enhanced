# 股权质押（EquityPledge）

股权质押模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：T+1  
**示例程序**：[examples/pledge_example.py](../../examples/pledge_example.py)

## 导入方式

```python
from akshare_one.modules.pledge import (
    get_equity_pledge,
    get_equity_pledge_ratio_rank
)
```

## 接口列表

### get_equity_pledge

获取股权质押数据。

**功能描述**：查询指定股票或全市场的股权质押明细数据。

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
| symbol | str | 股票代码 | "600000" |
| shareholder_name | str | 股东名称 | "某某公司" |
| pledge_shares | float | 质押股数（股） | 100000000.0 |
| pledge_ratio | float | 质押比例（%） | 50.0 |
| pledgee | str | 质权人 | "某某银行" |
| pledge_date | str | 质押日期（YYYY-MM-DD） | "2024-01-15" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.pledge import get_equity_pledge

# 获取浦发银行的股权质押数据
df = get_equity_pledge("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_equity_pledge_ratio_rank

获取质押比例排名。

**功能描述**：查询指定日期质押比例排名前N的股票。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 查询日期（YYYY-MM-DD格式） | "2024-01-31" |
| top_n | int | 否 | 100 | 返回前N名 | 50 |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 排名 | 1 |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| pledge_ratio | float | 总质押比例（%） | 70.0 |
| pledge_value | float | 质押市值（元） | 5000000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.pledge import get_equity_pledge_ratio_rank

# 获取质押比例排名前50的股票
df = get_equity_pledge_ratio_rank("2024-01-31", top_n=50)
print(df.head())
```