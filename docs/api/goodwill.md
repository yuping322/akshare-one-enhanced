# 商誉（Goodwill）

商誉模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：季度  
**示例程序**：[examples/goodwill_example.py](../../examples/goodwill_example.py)

## 导入方式

```python
from akshare_one.modules.goodwill import (
    get_goodwill_data,
    get_goodwill_impairment,
    get_goodwill_by_industry
)
```

## 接口列表

### get_goodwill_data

获取商誉数据。

**功能描述**：查询指定股票或全市场的商誉数据。

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
| report_date | str | 报告日期（YYYY-MM-DD） | "2024-03-31" |
| goodwill_balance | float | 商誉余额（元） | 5000000000.0 |
| goodwill_ratio | float | 商誉占净资产比例（%） | 25.0 |
| goodwill_impairment | float | 商誉减值（元） | 100000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.goodwill import get_goodwill_data

# 获取浦发银行的商誉数据
df = get_goodwill_data("600000", start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_goodwill_impairment

获取商誉减值预期。

**功能描述**：查询指定日期的商誉减值预期数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 查询日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| goodwill_balance | float | 商誉余额（元） | 5000000000.0 |
| expected_impairment | float | 预期减值金额（元） | 500000000.0 |
| risk_level | str | 风险等级 | "高" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.goodwill import get_goodwill_impairment

# 获取商誉减值预期
df = get_goodwill_impairment("2024-12-31")
print(df.head())
```

### get_goodwill_by_industry

获取行业商誉统计。

**功能描述**：查询指定日期各行业的商誉统计数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 查询日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| industry | str | 行业名称 | "银行" |
| total_goodwill | float | 总商誉金额（元） | 50000000000.0 |
| avg_ratio | float | 平均商誉占净资产比例（%） | 20.0 |
| total_impairment | float | 总减值金额（元） | 5000000000.0 |
| company_count | int | 公司数量 | 42 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.goodwill import get_goodwill_by_industry

# 获取行业商誉统计
df = get_goodwill_by_industry("2024-12-31")
print(df.head())
```