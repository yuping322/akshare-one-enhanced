# 分析师研报（Analyst）

分析师模块提供研报相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 日度

## 导入方式

```python
from akshare_one.modules.analyst import (
    get_analyst_rank,
    get_research_report,
)
```

## 接口列表

### get_analyst_rank

获取分析师排名数据。

**功能描述**: 查询分析师的历史收益率排名和行业分布情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| analyst_name | str | 分析师姓名 | "张三" |
| institution | str | 所属机构 | "中信证券" |
| industry | str | 擅长行业 | "电子" |
| return_rate | float | 历史收益率(%) | 25.5 |
| rank | int | 排名 | 1 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.analyst import get_analyst_rank

# 获取分析师排名
df = get_analyst_rank()
print(df.head(10))
```

---

### get_research_report

获取个股研报数据。

**功能描述**: 查询指定股票的研究报告，包括评级、目标价、机构等信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 股票代码（6位数字） | "600000" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| report_date | str | 报告日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| title | str | 报告标题 | "浦发银行：业绩稳健增长" |
| institution | str | 发布机构 | "中信证券" |
| analyst | str | 分析师 | "张三" |
| rating | str | 评级 | "买入" |
| target_price | float | 目标价 | 12.5 |

#### 异常

- `InvalidParameterError` - 参数无效（如股票代码格式错误）
- `NoDataError` - 指定股票无研报数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.analyst import get_research_report

# 获取浦发银行研报
reports = get_research_report("600000")
print(reports.head())

# 筛选买入评级
buy_reports = reports[reports['rating'] == '买入']
print(f"买入评级报告数: {len(buy_reports)}")
```

## 使用场景

### 场景1: 寻找优秀分析师

```python
from akshare_one.modules.analyst import get_analyst_rank

# 获取Top 10分析师
top_analysts = get_analyst_rank().head(10)
print("优秀分析师:")
print(top_analysts[['analyst_name', 'institution', 'return_rate']])
```

### 场景2: 研报跟踪

```python
from akshare_one.modules.analyst import get_research_report
import pandas as pd

# 获取某股票最近研报
reports = get_research_report("600000")

# 查看最新评级
latest = reports.iloc[0]
print(f"最新评级: {latest['rating']}, 目标价: {latest['target_price']}")
```

## 数据质量说明

- 研报数据覆盖A股主要上市公司
- 更新频率为日度，通常在交易日收盘后更新
- 评级标准可能因机构而异，常见评级：买入、增持、中性、减持

## 相关模块

- [基金评级](etf.md) - 基金评级数据
- [业绩快报](performance.md) - 业绩预告和快报
- [财务数据](../core-api/financial.md) - 财务报表数据

## 注意事项

1. 研报观点仅供参考，不构成投资建议
2. 不同机构的评级标准可能存在差异
3. 历史收益率不代表未来表现
