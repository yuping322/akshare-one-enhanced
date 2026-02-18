# 行业板块（Industry）

行业板块模块提供A股行业板块相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.industry import (
    get_industry_list,
)
```

## 接口列表

### get_industry_list

获取行业板块列表。

**功能描述**: 查询所有行业板块的行情数据，包括涨跌幅、领涨股等。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 排名 | 1 |
| name | str | 行业名称 | "银行" |
| code | str | 行业代码 | "BK0475" |
| price | float | 行业指数 | 1200.5 |
| pct_change | float | 涨跌幅(%) | 2.5 |
| turnover | float | 换手率(%) | 1.5 |
| up_count | int | 上涨家数 | 25 |
| down_count | int | 下跌家数 | 5 |
| leading_stock | str | 领涨股票 | "某某银行" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.industry import get_industry_list

# 获取行业板块列表
industries = get_industry_list()
print(industries.head(10))

# 筛选涨幅前10的行业
top_industries = industries.nlargest(10, 'pct_change')
print("\n涨幅前10的行业:")
print(top_industries[['name', 'pct_change', 'leading_stock']])
```

## 使用场景

### 场景1: 行业轮动分析

```python
from akshare_one.modules.industry import get_industry_list
import pandas as pd

# 获取行业数据
industries = get_industry_list()

# 计算行业涨跌分布
up_industries = industries[industries['pct_change'] > 0]
down_industries = industries[industries['pct_change'] < 0]

print(f"上涨行业: {len(up_industries)}")
print(f"下跌行业: {len(down_industries)}")

# 查看领涨行业
print("\n领涨行业:")
print(up_industries.nlargest(5, 'pct_change')[['name', 'pct_change']])
```

### 场景2: 行业对比分析

```python
from akshare_one.modules.industry import get_industry_list

# 关注特定行业
watch_list = ['银行', '医药', '电子', '房地产', '汽车']

industries = get_industry_list()
filtered = industries[industries['name'].isin(watch_list)]
filtered = filtered.sort_values('pct_change', ascending=False)

print("关注的行业表现:")
print(filtered[['name', 'pct_change', 'turnover']])
```

## 一级行业分类

| 行业名称 | 特点 | 周期性 |
|---------|------|--------|
| 银行 | 金融核心 | 弱周期 |
| 房地产 | 固定资产投资 | 强周期 |
| 医药 | 防御性 | 弱周期 |
| 电子 | 科技创新 | 成长型 |
| 汽车 | 消费升级 | 周期型 |
| 食品饮料 | 消费刚需 | 弱周期 |
| 化工 | 基础材料 | 强周期 |
| 钢铁 | 工业基础 | 强周期 |

## 相关模块

- [概念板块](concept.md) - 概念板块数据
- [资金流](fundflow.md) - 板块资金流向
- [宏观数据](macro.md) - 宏观经济数据

## 注意事项

1. 行业分类基于证监会标准
2. 行业表现与宏观经济周期相关
3. 建议结合行业基本面和政策导向分析
