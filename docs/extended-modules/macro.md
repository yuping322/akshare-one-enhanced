# 宏观数据（Macro）

宏观数据模块提供相关数据接口。

**数据源**：官方数据源（official）  
**更新频率**：月度  
**示例程序**：[examples/macro_example.py](../../examples/macro_example.py)

## 导入方式

```python
from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate
)
```

## 接口列表

### get_lpr_rate

获取LPR利率数据。

**功能描述**：查询贷款市场报价利率（LPR）的历史数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-20" |
| lpr_1y | float | 1年期LPR利率（%） | 3.45 |
| lpr_5y | float | 5年期LPR利率（%） | 4.20 |

#### 异常

- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_lpr_rate

# 获取LPR利率数据
df = get_lpr_rate(start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_pmi_index

获取PMI指数数据。

**功能描述**：查询制造业、非制造业或财新PMI指数数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| pmi_type | Literal["manufacturing", "non_manufacturing", "caixin"] | 否 | "manufacturing" | PMI类型 | "manufacturing" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-31" |
| pmi_value | float | PMI值 | 50.8 |
| yoy | float | 同比变化 | 0.5 |
| mom | float | 环比变化 | 0.2 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_pmi_index

# 获取制造业PMI数据
df = get_pmi_index(start_date="2023-01-01", pmi_type="manufacturing")
print(df.head())
```

### get_cpi_data

获取CPI数据。

**功能描述**：查询居民消费价格指数（CPI）数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-31" |
| current | float | 当月值 | 102.5 |
| yoy | float | 同比增长（%） | 2.5 |
| mom | float | 环比增长（%） | 0.3 |
| cumulative | float | 累计值 | 102.0 |

#### 异常

- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_cpi_data

# 获取CPI数据
df = get_cpi_data(start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_ppi_data

获取PPI数据。

**功能描述**：查询工业生产者出厂价格指数（PPI）数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-31" |
| current | float | 当月值 | 98.5 |
| yoy | float | 同比增长（%） | -1.5 |
| mom | float | 环比增长（%） | -0.2 |
| cumulative | float | 累计值 | 99.0 |

#### 异常

- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_ppi_data

# 获取PPI数据
df = get_ppi_data(start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_m2_supply

获取M2货币供应量数据。

**功能描述**：查询广义货币供应量（M2）数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-31" |
| m2_balance | float | M2余额（亿元） | 2800000.0 |
| yoy_growth_rate | float | 同比增长率（%） | 9.5 |

#### 异常

- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_m2_supply

# 获取M2货币供应量数据
df = get_m2_supply(start_date="2023-01-01", end_date="2024-12-31")
print(df.head())
```

### get_shibor_rate

获取Shibor利率数据。

**功能描述**：查询上海银行间同业拆放利率（Shibor）数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-12-31" |
| source | Literal["official"] | 否 | "official" | 数据源 | "official" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| overnight | float | 隔夜利率（%） | 1.85 |
| week_1 | float | 1周利率（%） | 1.95 |
| week_2 | float | 2周利率（%） | 2.05 |
| month_1 | float | 1月利率（%） | 2.15 |
| month_3 | float | 3月利率（%） | 2.35 |
| month_6 | float | 6月利率（%） | 2.55 |
| month_9 | float | 9月利率（%） | 2.65 |
| year_1 | float | 1年利率（%） | 2.75 |

#### 异常

- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.macro import get_shibor_rate

# 获取Shibor利率数据
df = get_shibor_rate(start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```