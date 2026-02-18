# 资金流（FundFlow）

资金流模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：实时  
**示例程序**：[examples/fundflow_example.py](../../examples/fundflow_example.py)

## 导入方式

```python
from akshare_one.modules.fundflow import (
    get_stock_fund_flow,
    get_sector_fund_flow,
    get_main_fund_flow_rank,
    get_industry_list,
    get_industry_constituents,
    get_concept_list,
    get_concept_constituents
)
```

## 接口列表

### get_stock_fund_flow

获取个股资金流数据。

**功能描述**：查询指定股票在指定时间范围内的资金流向数据，包括主力资金、超大单、大单、中单、小单的净流入情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 股票代码（6位数字） | "600000" |
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
| close | float | 收盘价 | 12.34 |
| pct_change | float | 涨跌幅（%） | 2.5 |
| main_net_inflow | float | 主力资金净流入（万元） | 5000.0 |
| main_net_inflow_rate | float | 主力资金净流入率（%） | 3.2 |
| super_large_net_inflow | float | 超大单净流入（万元） | 3000.0 |
| large_net_inflow | float | 大单净流入（万元） | 2000.0 |
| medium_net_inflow | float | 中单净流入（万元） | -1000.0 |
| small_net_inflow | float | 小单净流入（万元） | -4000.0 |

#### 异常

- `InvalidParameterError` - 参数无效（如股票代码格式错误）
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_stock_fund_flow

# 获取浦发银行近30天的资金流数据
df = get_stock_fund_flow("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```


### get_sector_fund_flow

获取板块资金流数据。

**功能描述**：查询行业板块或概念板块的资金流向数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| sector_type | Literal["industry", "concept"] | 是 | - | 板块类型（industry=行业，concept=概念） | "industry" |
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| sector_code | str | 板块代码 | "BK0001" |
| sector_name | str | 板块名称 | "银行" |
| sector_type | str | 板块类型 | "industry" |
| main_net_inflow | float | 主力资金净流入（万元） | 50000.0 |
| pct_change | float | 涨跌幅（%） | 1.5 |
| leading_stock | str | 领涨股代码 | "600000" |
| leading_stock_pct | float | 领涨股涨跌幅（%） | 3.2 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_sector_fund_flow

# 获取行业板块资金流数据
df = get_sector_fund_flow("industry", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_main_fund_flow_rank

获取主力资金流排名。

**功能描述**：查询指定日期的主力资金净流入或净流入率排名。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 日期（YYYY-MM-DD格式） | "2024-01-15" |
| indicator | Literal["net_inflow", "net_inflow_rate"] | 否 | "net_inflow" | 排名指标 | "net_inflow" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 排名 | 1 |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| main_net_inflow | float | 主力资金净流入（万元） | 50000.0 |
| pct_change | float | 涨跌幅（%） | 3.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_main_fund_flow_rank

# 获取主力资金净流入排名
df = get_main_fund_flow_rank("2024-01-15", indicator="net_inflow")
print(df.head(10))
```

### get_industry_list

获取行业板块列表。

**功能描述**：查询所有行业板块的列表及成分股数量。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| sector_code | str | 板块代码 | "BK0001" |
| sector_name | str | 板块名称 | "银行" |
| constituent_count | int | 成分股数量 | 42 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_industry_list

# 获取行业板块列表
df = get_industry_list()
print(df.head())
```

### get_industry_constituents

获取行业板块成分股。

**功能描述**：查询指定行业板块的成分股列表。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| industry_code | str | 是 | - | 行业板块代码 | "BK0001" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| weight | float | 权重（可能为None） | 0.15 |

#### 异常

- `InvalidParameterError` - 参数无效（如板块代码不存在）
- `NoDataError` - 板块无成分股数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_industry_constituents

# 获取银行板块成分股
df = get_industry_constituents("BK0001")
print(df.head())
```

### get_concept_list

获取概念板块列表。

**功能描述**：查询所有概念板块的列表及成分股数量。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| sector_code | str | 板块代码 | "BK0001" |
| sector_name | str | 板块名称 | "人工智能" |
| constituent_count | int | 成分股数量 | 120 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_concept_list

# 获取概念板块列表
df = get_concept_list()
print(df.head())
```

### get_concept_constituents

获取概念板块成分股。

**功能描述**：查询指定概念板块的成分股列表。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| concept_code | str | 是 | - | 概念板块代码 | "BK0001" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| weight | float | 权重（可能为None） | 0.08 |

#### 异常

- `InvalidParameterError` - 参数无效（如板块代码不存在）
- `NoDataError` - 板块无成分股数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.fundflow import get_concept_constituents

# 获取人工智能概念成分股
df = get_concept_constituents("BK0001")
print(df.head())
```