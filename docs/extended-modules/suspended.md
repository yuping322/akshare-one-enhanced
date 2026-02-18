# 停复牌（Suspended）

停复牌模块提供股票停牌和复牌相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.suspended import (
    get_suspended_stocks,
)
```

## 接口列表

### get_suspended_stocks

获取停牌股票列表和相关信息。

**功能描述**: 查询当前处于停牌状态的股票列表和停牌原因。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600001" |
| name | str | 股票名称 | "某某股份" |
| suspended_date | str | 停牌日期 | "2024-01-15" |
| suspended_reason | str | 停牌原因 | "重大资产重组" |
| expected_resume_date | str | 预计复牌日期 | "2024-02-15" |
| suspended_days | int | 停牌天数 | 30 |
| market | str | 所属市场 | "上交所" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.suspended import get_suspended_stocks

# 获取停牌股票列表
suspended = get_suspended_stocks()
print(suspended.head(10))

# 统计停牌股票数量
print(f"停牌股票总数: {len(suspended)}")

# 筛选长期停牌股票
long_suspended = suspended[suspended['suspended_days'] > 30]
print(f"长期停牌(>30天): {len(long_suspended)}只")
```

## 使用场景

### 场景1: 停牌风险监控

```python
from akshare_one.modules.suspended import get_suspended_stocks

# 获取停牌股票
suspended = get_suspended_stocks()

# 分析停牌原因分布
reason_dist = suspended['suspended_reason'].value_counts()
print("停牌原因分布:")
print(reason_dist)

# 筛选重大事项停牌
major_events = suspended[suspended['suspended_reason'].str.contains('重大')]
print(f"\n重大事项停牌: {len(major_events)}只")
print(major_events[['name', 'suspended_reason', 'expected_resume_date']].head())
```

### 场景2: 复牌预期分析

```python
from akshare_one.modules.suspended import get_suspended_stocks
import pandas as pd

# 获取停牌股票
suspended = get_suspended_stocks()

# 查看即将复牌的股票
suspended['expected_resume_date'] = pd.to_datetime(suspended['expected_resume_date'])
today = pd.Timestamp.now()
near_resume = suspended[
    (suspended['expected_resume_date'] >= today) & 
    (suspended['expected_resume_date'] <= today + pd.Timedelta(days=7))
]

print(f"一周内预计复牌: {len(near_resume)}只")
if not near_resume.empty:
    print(near_resume[['name', 'expected_resume_date', 'suspended_reason']])
```

## 停牌基础知识

### 停牌类型
- **临时停牌**: 盘中异常波动
- **例行停牌**: 定期报告披露
- **重大事项停牌**: 重组、收购等
- **风险警示停牌**: 违规、财务问题

### 停牌规则
- **主板**: 涨跌停板达到±10%时可能临时停牌
- **科创板/创业板**: ±20%涨跌停，停牌规则不同
- **重大事项**: 无固定时间，根据事项进展

### 复牌条件
- **临时停牌**: 达到时间或价格稳定
- **重大事项**: 事项完成或公告披露
- **风险警示**: 问题解决并申请

### 投资影响
1. **流动性风险**: 无法买卖
2. **价格风险**: 复牌后可能大幅波动
3. **信息不对称**: 停牌期间无法获取实时信息
4. **机会成本**: 资金占用

## 相关模块

- [公告信披](disclosure.md) - 停牌相关公告
- [龙虎榜](lhb.md) - 复牌后异动交易
- [资金流](fundflow.md) - 复牌资金流向

## 注意事项

1. 停牌股票无法进行交易操作
2. 复牌后可能出现大幅波动
3. 长期停牌可能存在退市风险
4. 关注停牌原因和进展公告

## 常见停牌原因

| 原因类型 | 说明 | 风险等级 |
|---------|------|----------|
| **重大资产重组** | 资产注入、收购等 | 中高 |
| **筹划重大事项** | 未明确具体事项 | 中 |
| **补充公告** | 信息披露不完整 | 低 |
| **股价异常** | 连续涨停/跌停 | 中 |
| **财务问题** | 审计、年报问题 | 高 |
| **违规调查** | 监管部门调查 | 高 |

## 数据局限性

- 停牌信息可能有延迟
- 预计复牌日期可能变更
- 部分停牌原因描述简略
- 需结合公告信息综合判断
