# ESG评级（ESG）

ESG评级模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：季度  
**示例程序**：[examples/esg_example.py](../../examples/esg_example.py)

## 导入方式

```python
from akshare_one.modules.esg import (
    get_esg_rating,
    get_esg_rating_rank
)
```

## 接口列表

### get_esg_rating

获取ESG评分数据。

**功能描述**：查询指定股票或全市场的ESG评分数据。

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
| rating_date | str | 评级日期（YYYY-MM-DD） | "2024-06-30" |
| esg_score | float | ESG总分 | 75.5 |
| e_score | float | 环境得分 | 70.0 |
| s_score | float | 社会得分 | 80.0 |
| g_score | float | 治理得分 | 76.5 |
| rating_agency | str | 评级机构 | "某某评级机构" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.esg import get_esg_rating

# 获取浦发银行的ESG评分
df = get_esg_rating("600000", start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_esg_rating_rank

获取ESG评级排名。

**功能描述**：查询指定日期的ESG评级排名，可按行业筛选。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 查询日期（YYYY-MM-DD格式） | "2024-12-31" |
| industry | str \| None | 否 | None | 行业筛选（None表示全部行业） | "银行" |
| top_n | int | 否 | 100 | 返回前N名 | 50 |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 总排名 | 1 |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| esg_score | float | ESG总分 | 85.5 |
| industry | str | 行业名称 | "银行" |
| industry_rank | int | 行业内排名 | 1 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.esg import get_esg_rating_rank

# 获取全市场ESG评级排名前100
df = get_esg_rating_rank("2024-12-31", top_n=100)
print(df.head())

# 获取银行业ESG评级排名
df = get_esg_rating_rank("2024-12-31", industry="银行")
print(df.head())
```