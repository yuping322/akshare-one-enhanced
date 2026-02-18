# 公告信披（Disclosure）

公告信披模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：实时  
**示例程序**：[examples/disclosure_example.py](../../examples/disclosure_example.py)

## 导入方式

```python
from akshare_one.modules.disclosure import (
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data
)
```

## 接口列表

### get_disclosure_news

获取公告数据。

**功能描述**：查询指定股票或全市场的公告信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str \| None | 否 | None | 股票代码（None表示全市场） | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| category | Literal["all", "dividend", "repurchase", "st", "major_event"] | 否 | "all" | 公告类别 | "all" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 公告日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| title | str | 公告标题 | "2023年年度报告" |
| category | str | 公告类别 | "年报" |
| content | str | 公告摘要 | "公司2023年实现营业收入..." |
| url | str | 公告链接 | "http://..." |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.disclosure import get_disclosure_news

# 获取浦发银行的公告
df = get_disclosure_news("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_dividend_data

获取分红派息数据。

**功能描述**：查询指定股票或全市场的分红派息信息。

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
| fiscal_year | str | 分红年度 | "2023" |
| dividend_per_share | float | 每股分红（元） | 0.5 |
| record_date | str | 股权登记日（YYYY-MM-DD） | "2024-06-15" |
| ex_dividend_date | str | 除权除息日（YYYY-MM-DD） | "2024-06-16" |
| payment_date | str | 派息日（YYYY-MM-DD） | "2024-06-20" |
| dividend_ratio | float | 分红率（%） | 30.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.disclosure import get_dividend_data

# 获取浦发银行的分红数据
df = get_dividend_data("600000", start_date="2020-01-01")
print(df.head())
```

### get_repurchase_data

获取股票回购数据。

**功能描述**：查询指定股票或全市场的股票回购信息。

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
| announcement_date | str | 公告日期（YYYY-MM-DD） | "2024-01-15" |
| progress | str | 回购进展 | "实施中" |
| amount | float | 回购金额（万元） | 50000.0 |
| quantity | float | 回购数量（万股） | 1000.0 |
| price_range | str | 回购价格区间 | "10.00-12.00" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.disclosure import get_repurchase_data

# 获取浦发银行的回购数据
df = get_repurchase_data("600000", start_date="2023-01-01")
print(df.head())
```

### get_st_delist_data

获取ST/退市风险数据。

**功能描述**：查询指定股票或全市场的ST和退市风险信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str \| None | 否 | None | 股票代码（None表示全市场） | "600000" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| st_type | str | ST类型 | "ST" |
| risk_level | str | 风险等级 | "高" |
| announcement_date | str | 公告日期（YYYY-MM-DD） | "2024-01-15" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 无ST/退市风险数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.disclosure import get_st_delist_data

# 获取全市场ST和退市风险股票
df = get_st_delist_data()
print(df.head())
```