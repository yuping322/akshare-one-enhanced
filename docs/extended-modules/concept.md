# 概念板块（Concept）

概念板块模块提供A股概念板块相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.concept import (
    get_concept_list,
)
```

## 接口列表

### get_concept_list

获取概念板块列表。

**功能描述**: 查询所有概念板块的行情数据，包括涨跌幅、领涨股等。

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
| name | str | 板块名称 | "人工智能" |
| code | str | 板块代码 | "BK0559" |
| price | float | 板块指数 | 1500.5 |
| pct_change | float | 涨跌幅(%) | 3.5 |
| turnover | float | 换手率(%) | 5.2 |
| up_count | int | 上涨家数 | 45 |
| down_count | int | 下跌家数 | 5 |
| leading_stock | str | 领涨股票 | "某某科技" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.concept import get_concept_list

# 获取概念板块列表
concepts = get_concept_list()
print(concepts.head(10))

# 筛选涨幅前10的概念板块
top_concepts = concepts.nlargest(10, 'pct_change')
print("\n涨幅前10的概念板块:")
print(top_concepts[['name', 'pct_change', 'leading_stock']])
```

## 使用场景

### 场景1: 热门概念追踪

```python
from akshare_one.modules.concept import get_concept_list

# 获取概念板块数据
concepts = get_concept_list()

# 筛选活跃度高的概念（换手率>5%）
active_concepts = concepts[concepts['turnover'] > 5]
active_concepts = active_concepts.sort_values('pct_change', ascending=False)

print("活跃概念板块:")
print(active_concepts[['name', 'pct_change', 'turnover']].head(10))
```

### 场景2: 概念强度分析

```python
from akshare_one.modules.concept import get_concept_list

# 获取数据
concepts = get_concept_list()

# 计算概念强度（涨跌幅*上涨家数比例）
concepts['up_ratio'] = concepts['up_count'] / (concepts['up_count'] + concepts['down_count'])
concepts['strength'] = concepts['pct_change'] * concepts['up_ratio']

# 排序
strong_concepts = concepts.nlargest(10, 'strength')
print("概念强度排名:")
print(strong_concepts[['name', 'pct_change', 'up_ratio', 'strength']])
```

## 常见概念板块

| 概念名称 | 说明 | 相关股票 |
|---------|------|----------|
| 人工智能 | AI相关 | 科技股 |
| 新能源汽车 | 电动车产业链 | 汽车股 |
| 芯片 | 半导体 | 芯片股 |
| 5G | 通信技术 | 通信股 |
| 医药 | 医疗保健 | 医药股 |

## 相关模块

- [行业板块](industry.md) - 行业板块数据
- [资金流](fundflow.md) - 板块资金流向
- [市场情绪](sentiment.md) - 市场情绪指标

## 注意事项

1. 概念板块成分股可能重叠
2. 热点概念轮动较快，需及时跟踪
3. 概念炒作风险较高，需结合基本面分析
