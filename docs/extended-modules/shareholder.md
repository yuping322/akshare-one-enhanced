# 股东数据（Shareholder）

股东模块提供股东持股和变动相关数据接口。

**数据源**: 东方财富（eastmoney）、上交所（sse）  
**更新频率**: 日度

## 导入方式

```python
from akshare_one.modules.shareholder import (
    get_shareholder_changes,
    get_top_shareholders,
    get_institution_holdings,
)
```

## 接口列表

### get_shareholder_changes

获取股东增减持数据。

**功能描述**: 查询上市公司股东的增减持情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 否 | None | 股票代码 | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期 | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期 | "2024-12-31" |
| source | Literal["eastmoney","sse"] | 否 | "sse" | 数据源 | "sse" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| holder_name | str | 股东名称 | "某某投资" |
| position | str | 职务 | "董事" |
| change_shares | int | 变动股数 | 10000 |
| reason | str | 变动原因 | "二级市场买卖" |
| change_date | str | 变动日期 | "2024-01-15" |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.shareholder import get_shareholder_changes

# 获取股东增减持数据
changes = get_shareholder_changes("600000", start_date="2024-01-01")
print(changes.head())

# 统计增持vs减持
increase = changes[changes['change_shares'] > 0]
decrease = changes[changes['change_shares'] < 0]

print(f"增持次数: {len(increase)}")
print(f"减持次数: {len(decrease)}")
```

---

### get_top_shareholders

获取十大股东数据。

**功能描述**: 查询上市公司的前十大股东持股情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 股票代码 | "600000" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| institution_count | int | 机构数量 | 150 |
| holding_pct | float | 持股比例(%) | 65.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.shareholder import get_top_shareholders

# 获取十大股东
shareholders = get_top_shareholders("600000")
print(shareholders)

# 查看机构持股比例
print(f"机构持股: {shareholders.iloc[0]['holding_pct']:.2f}%")
```

---

### get_institution_holdings

获取机构持仓数据。

**功能描述**: 查询机构对某只股票的持仓情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 股票代码 | "600000" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| institution_count | int | 机构数量 | 150 |
| holding_pct | float | 持股比例(%) | 65.5 |
| float_holding_pct | float | 流通盘占比(%) | 75.2 |

#### 异常

- `InvalidParameterError` - 参数无效
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.shareholder import get_institution_holdings

# 获取机构持仓
holdings = get_institution_holdings("600000")
print(holdings)

# 分析机构持仓
if not holdings.empty:
    print(f"机构数量: {holdings.iloc[0]['institution_count']}")
    print(f"持股比例: {holdings.iloc[0]['holding_pct']:.2f}%")
    print(f"流通盘占比: {holdings.iloc[0]['float_holding_pct']:.2f}%")
```

## 使用场景

### 场景1: 高管增减持监控

```python
from akshare_one.modules.shareholder import get_shareholder_changes

# 获取最近的高管增减持
changes = get_shareholder_changes(start_date="2024-01-01")

# 筛选重要股东（高管、董事）
key_positions = ['董事长', '总经理', '董事', '监事']
key_changes = changes[changes['position'].isin(key_positions)]

# 统计增持
increase = key_changes[key_changes['change_shares'] > 0]
print("高管增持:")
print(increase[['name', 'holder_name', 'change_shares', 'change_date']].head(10))
```

### 场景2: 机构持仓分析

```python
from akshare_one.modules.shareholder import get_institution_holdings

# 获取多只股票机构持仓
symbols = ['600000', '000001', '600519']
holdings_list = []

for symbol in symbols:
    try:
        holding = get_institution_holdings(symbol)
        if not holding.empty:
            holdings_list.append(holding.iloc[0])
    except:
        pass

# 对比分析
import pandas as pd
df = pd.DataFrame(holdings_list)
df = df.sort_values('holding_pct', ascending=False)
print("机构持仓排名:")
print(df[['name', 'institution_count', 'holding_pct']])
```

### 场景3: 股东集中度分析

```python
from akshare_one.modules.shareholder import (
    get_top_shareholders,
    get_institution_holdings
)

# 获取数据
top10 = get_top_shareholders("600000")
inst = get_institution_holdings("600000")

if not top10.empty and not inst.empty:
    top10_pct = top10.iloc[0]['holding_pct']
    inst_pct = inst.iloc[0]['holding_pct']
    
    print(f"十大股东持股: {top10_pct:.2f}%")
    print(f"机构持股: {inst_pct:.2f}%")
    print(f"散户持股: {100 - top10_pct:.2f}%")
    
    # 判断筹码集中度
    if top10_pct > 70:
        print("筹码高度集中")
    elif top10_pct > 50:
        print("筹码中度集中")
    else:
        print("筹码分散")
```

## 股东类型说明

### 按身份分类

| 类型 | 说明 | 关注重点 |
|------|------|---------|
| **控股股东** | 实际控制人 | 增减持信号意义重大 |
| **高管** | 董监高 | 最了解公司经营状况 |
| **机构投资者** | 基金、保险等 | 专业投资能力 |
| **员工持股** | 股权激励 | 内部人信心指标 |

### 变动原因

| 原因 | 说明 | 影响 |
|------|------|------|
| 二级市场买卖 | 正常交易 | 中性 |
| 股权激励 | 员工持股计划 | 利好 |
| 协议转让 | 大宗交易 | 需关注受让方 |
| 继承/赠与 | 非交易过户 | 中性 |
| 司法处置 | 法院强制执行 | 利空 |

## 数据来源对比

| 数据源 | 优势 | 适用场景 |
|--------|------|---------|
| **sse** | 上交所官方数据，增减持信息权威 | 股东变动查询 |
| **eastmoney** | 数据整合，持仓信息全面 | 机构持仓分析 |

## 相关模块

- [估值](valuation.md) - 估值分析
- [业绩](performance.md) - 业绩预告
- [融资融券](margin.md) - 杠杆资金

## 注意事项

1. 增减持数据有披露延迟，大宗交易次日公布
2. 高管增减持受窗口期限制（定期报告前30日等）
3. 机构持仓数据为季度披露，非实时
4. 需结合股价位置和公司基本面综合判断

## 投资策略

### 1. 跟庄策略

```python
# 关注高管/大股东增持
if executive_increase and price_near_low:
    print("内部人增持+股价低位，可能是机会")
```

### 2. 筹码分析

```python
# 机构持仓持续增加
if inst_holding_trend == "increasing":
    print("机构持续买入，看好后市")
```

### 3. 风险预警

```python
# 大股东减持
if major_holder_decrease > 5:  # 减持超5%
    print("大股东大幅减持，需警惕")
```
