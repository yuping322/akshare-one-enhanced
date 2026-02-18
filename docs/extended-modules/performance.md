# 业绩快报（Performance）

业绩模块提供上市公司业绩预告和快报数据。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 季度（业绩披露期）

## 导入方式

```python
from akshare_one.modules.performance import (
    get_performance_forecast,
    get_performance_express,
)
```

## 接口列表

### get_performance_forecast

获取业绩预告数据。

**功能描述**: 查询上市公司的业绩预告信息，包括预增、预减等类型。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 否 | "20240331" | 报告期 | "20240331" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| indicator | str | 预告类型 | "预增"/"预减"/"预盈"/"预亏" |
| change_pct | float | 变动幅度(%) | 50.5 |
| forecast_value | float | 预计净利润(亿) | 500.0 |
| previous_value | float | 上年同期(亿) | 332.2 |
| report_date | str | 报告日期 | "2024-01-31" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.performance import get_performance_forecast

# 获取2024年一季度业绩预告
df = get_performance_forecast(date="20240331")
print(df.head())

# 筛选大幅预增的股票
high_growth = df[df['change_pct'] > 100]
print(f"预增超过100%的股票数: {len(high_growth)}")
print(high_growth[['symbol', 'name', 'change_pct']].head())
```

---

### get_performance_express

获取业绩快报数据。

**功能描述**: 查询上市公司的业绩快报，包含详细的财务数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 否 | "20240331" | 报告期 | "20240331" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| eps | float | 每股收益 | 1.85 |
| revenue | float | 营业收入(亿) | 1500.5 |
| revenue_yoy | float | 营收同比(%) | 15.2 |
| net_profit | float | 净利润(亿) | 500.5 |
| net_profit_yoy | float | 净利同比(%) | 20.5 |
| report_date | str | 报告日期 | "2024-04-15" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.performance import get_performance_express

# 获取2024年一季度业绩快报
df = get_performance_express(date="20240331")
print(df.head())

# 筛选高增长股票
high_growth = df[
    (df['revenue_yoy'] > 30) & 
    (df['net_profit_yoy'] > 30)
]
print("营收和净利均增长超30%:")
print(high_growth[['symbol', 'name', 'revenue_yoy', 'net_profit_yoy']].head())
```

## 业绩预告 vs 业绩快报

| 类型 | 发布时间 | 详细程度 | 准确性 |
|------|---------|---------|--------|
| **业绩预告** | 较早（报告期前） | 粗略（区间） | 约70-80% |
| **业绩快报** | 较晚（报告期后） | 详细（准确数据） | 约95%+ |

## 使用场景

### 场景1: 业绩预增筛选

```python
from akshare_one.modules.performance import get_performance_forecast

# 获取最新业绩预告
forecasts = get_performance_forecast()

# 筛选条件：预增 + 幅度>50% + 盈利
filtered = forecasts[
    (forecasts['indicator'] == '预增') &
    (forecasts['change_pct'] > 50) &
    (forecasts['forecast_value'] > 0)
]

# 按增幅排序
filtered = filtered.sort_values('change_pct', ascending=False)
print("优质预增股票:")
print(filtered[['symbol', 'name', 'change_pct', 'forecast_value']].head(10))
```

### 场景2: 业绩对比分析

```python
from akshare_one.modules.performance import (
    get_performance_forecast,
    get_performance_express
)

# 获取同一报告期的预告和快报
forecast = get_performance_forecast(date="20240331")
express = get_performance_express(date="20240331")

# 对比某只股票的预告vs实际
symbol = "600000"
f_data = forecast[forecast['symbol'] == symbol]
e_data = express[express['symbol'] == symbol]

if not f_data.empty and not e_data.empty:
    print(f"\n{symbol} 业绩对比:")
    print(f"预告净利: {f_data.iloc[0]['forecast_value']:.2f}亿")
    print(f"实际净利: {e_data.iloc[0]['net_profit']:.2f}亿")
    
    diff_pct = ((e_data.iloc[0]['net_profit'] - f_data.iloc[0]['forecast_value']) 
                / f_data.iloc[0]['forecast_value'] * 100)
    print(f"差异: {diff_pct:+.2f}%")
```

## 预告类型说明

| 类型 | 说明 | 投资建议 |
|------|------|----------|
| **预增** | 净利润增长>50% | 利好 |
| **略增** | 净利润增长0-50% | 中性偏利好 |
| **续盈** | 继续盈利 | 中性 |
| **扭亏** | 由亏转盈 | 重大利好 |
| **预减** | 净利润下降 | 利空 |
| **略减** | 净利润略降 | 中性偏利空 |
| **首亏** | 首次亏损 | 利空 |
| **续亏** | 继续亏损 | 利空 |
| **不确定** | 无法预计 | 需关注 |

## 数据披露时间

| 报告期 | 预告时间 | 快报时间 | 正式报告 |
|--------|---------|---------|---------|
| 一季报 | 3-4月 | 4月 | 4月底 |
| 半年报 | 7-8月 | 7-8月 | 8月底 |
| 三季报 | 10月 | 10月 | 10月底 |
| 年报 | 1-2月 | 1-3月 | 4月底 |

## 相关模块

- [财务数据](../core-api/financial.md) - 详细财务报表
- [估值](valuation.md) - 估值分析
- [分析师](analyst.md) - 研报评级

## 注意事项

1. 业绩预告为预估数据，可能与实际有偏差
2. 业绩快报数据未经审计，最终数据以正式财报为准
3. 需结合行业景气度和公司基本面综合分析
4. 预告和快报仅在披露期有数据，平时可能为空
