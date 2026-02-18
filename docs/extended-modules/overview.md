# 扩展模块概览

AKShare One 提供了 27 个专业市场数据扩展模块，涵盖了全面的金融数据需求。这些模块统一了接口设计，提供标准化的数据输出。

## 扩展模块列表

### 基础数据模块

### 1. 指数数据 (Index)

**模块**: `akshare_one.modules.index`

获取股票指数历史行情、实时行情和成分股数据。

**核心接口**:
- `get_index_hist_data()` - 指数历史数据
- `get_index_realtime_data()` - 指数实时行情
- `get_index_list()` - 指数列表
- `get_index_constituents()` - 指数成分股

**数据源**: 东方财富、新浪财经

[详细文档](index.md)

### 2. ETF基金 (ETF)

**模块**: `akshare_one.modules.etf`

获取ETF基金历史数据、实时行情、基金经理和评级信息。

**核心接口**:
- `get_etf_hist_data()` - ETF历史数据
- `get_etf_realtime_data()` - ETF实时行情
- `get_etf_list()` - ETF列表
- `get_fund_manager_info()` - 基金经理信息
- `get_fund_rating_data()` - 基金评级

**数据源**: 东方财富、新浪财经

[详细文档](etf.md)

### 3. 可转债 (Bonds)

**模块**: `akshare_one.modules.bond`

获取可转债列表、历史行情和实时数据。

**核心接口**:
- `get_bond_list()` - 可转债列表
- `get_bond_hist_data()` - 债券历史数据
- `get_bond_realtime_data()` - 债券实时行情

**数据源**: 东方财富、集思录

[详细文档](bond.md)

### 4. 行业板块 (Industry)

**模块**: `akshare_one.modules.industry`

获取行业板块列表和行情数据。

**核心接口**:
- `get_industry_list()` - 行业板块列表

**数据源**: 东方财富

[详细文档](industry.md)

### 5. 概念板块 (Concept)

**模块**: `akshare_one.modules.concept`

获取概念板块列表和行情数据。

**核心接口**:
- `get_concept_list()` - 概念板块列表

**数据源**: 东方财富

[详细文档](concept.md)

### 6. 港股美股 (HKUS)

**模块**: `akshare_one.modules.hkus`

获取港股实时行情数据。

**核心接口**:
- `get_hk_stocks()` - 港股列表和行情

**数据源**: 东方财富

[详细文档](hkus.md)

### 7. 科创板创业板 (Board)

**模块**: `akshare_one.modules.board`

获取科创板和创业板股票数据。

**核心接口**:
- `get_kcb_stocks()` - 科创板股票
- `get_cyb_stocks()` - 创业板股票

**数据源**: 东方财富

[详细文档](board.md)

### 8. 新股次新 (IPO)

**模块**: `akshare_one.modules.ipo`

获取IPO和新上市股票数据。

**核心接口**:
- `get_new_stocks()` - 新股列表
- `get_ipo_info()` - IPO详细信息

**数据源**: 东方财富、巨潮资讯

[详细文档](ipo.md)

### 9. ST股票 (ST)

**模块**: `akshare_one.modules.st`

获取ST/*ST股票列表和行情。

**核心接口**:
- `get_st_stocks()` - ST股票列表

**数据源**: 东方财富

[详细文档](st.md)

### 10. 停复牌 (Suspended)

**模块**: `akshare_one.modules.suspended`

获取停牌股票列表和相关信息。

**核心接口**:
- `get_suspended_stocks()` - 停牌股票列表

**数据源**: 东方财富

[详细文档](suspended.md)

### 市场分析模块

### 4. 资金流 (FundFlow)

**模块**: `akshare_one.modules.fundflow`

获取个股资金流向、板块资金流分析和主力资金排名。

**核心接口**:
- `get_stock_fund_flow()` - 个股资金流
- `get_sector_fund_flow()` - 板块资金流
- `get_main_fund_flow_rank()` - 主力资金排名
- `get_industry_list()` - 行业列表
- `get_concept_list()` - 概念板块列表

**数据源**: 东方财富

[详细文档](fundflow.md)

### 2. 公告信披 (Disclosure)

**模块**: `akshare_one.modules.disclosure`

获取上市公司公告、分红派息、股票回购等信息。

**核心接口**:
- `get_disclosure_news()` - 公告数据
- `get_dividend_data()` - 分红派息
- `get_repurchase_data()` - 股票回购
- `get_st_delist_data()` - ST/退市风险

**数据源**: 东方财富、新浪财经

[详细文档](disclosure.md)

### 3. 北向资金 (Northbound)

**模块**: `akshare_one.modules.northbound`

追踪沪港通、深港通北向资金流向和持股变化。

**核心接口**:
- `get_northbound_flow()` - 北向资金流向
- `get_northbound_holdings()` - 北向持股明细
- `get_northbound_top_stocks()` - 北向资金Top股票

**数据源**: 东方财富

[详细文档](northbound.md)

### 4. 宏观数据 (Macro)

**模块**: `akshare_one.modules.macro`

获取宏观经济指标，包括利率、通胀、货币供应等。

**核心接口**:
- `get_lpr_rate()` - LPR利率
- `get_pmi_index()` - PMI指数
- `get_cpi_data()` - CPI数据
- `get_ppi_data()` - PPI数据
- `get_m2_supply()` - M2货币供应
- `get_shibor_rate()` - Shibor利率

**数据源**: 官方统计数据

[详细文档](macro.md)

### 5. 大宗交易 (BlockDeal)

**模块**: `akshare_one.modules.blockdeal`

获取大宗交易明细和市场统计。

**核心接口**:
- `get_block_deal()` - 大宗交易明细
- `get_block_deal_summary()` - 大宗交易统计

**数据源**: 东方财富

[详细文档](blockdeal.md)

### 6. 龙虎榜 (LHB)

**模块**: `akshare_one.modules.lhb`

获取龙虎榜数据，包括异常交易、营业部活跃度等。

**核心接口**:
- `get_dragon_tiger_list()` - 龙虎榜列表
- `get_dragon_tiger_summary()` - 龙虎榜统计
- `get_dragon_tiger_broker_stats()` - 营业部分析

**数据源**: 东方财富

[详细文档](lhb.md)

### 7. 涨停池 (LimitUp)

**模块**: `akshare_one.modules.limitup`

获取涨停/跌停池数据和统计分析。

**核心接口**:
- `get_limit_up_pool()` - 涨停池
- `get_limit_down_pool()` - 跌停池
- `get_limit_up_stats()` - 涨停统计分析

**数据源**: 东方财富

[详细文档](limitup.md)

### 8. 融资融券 (Margin Trading)

**模块**: `akshare_one.modules.margin`

获取融资融券数据和市场汇总。

**核心接口**:
- `get_margin_data()` - 个股融资融券数据
- `get_margin_summary()` - 市场融资融券汇总

**数据源**: 东方财富

[详细文档](margin.md)

### 9. 股权质押 (Pledge)

**模块**: `akshare_one.modules.pledge`

获取股权质押数据和质押比例排名。

**核心接口**:
- `get_equity_pledge()` - 股权质押数据
- `get_equity_pledge_ratio_rank()` - 质押比例排名

**数据源**: 东方财富

[详细文档](pledge.md)

### 10. 限售解禁 (Restricted)

**模块**: `akshare_one.modules.restricted`

获取限售股解禁数据和未来解禁日历。

**核心接口**:
- `get_restricted_release()` - 限售解禁数据
- `get_restricted_release_calendar()` - 解禁日历

**数据源**: 东方财富

[详细文档](restricted.md)

### 11. 商誉 (Goodwill)

**模块**: `akshare_one.modules.goodwill`

获取商誉数据、减值预期和行业统计。

**核心接口**:
- `get_goodwill_data()` - 商誉数据
- `get_goodwill_impairment()` - 商誉减值预期
- `get_goodwill_by_industry()` - 行业商誉统计

**数据源**: 东方财富

[详细文档](goodwill.md)

### 12. ESG 评级 (ESG Rating)

**模块**: `akshare_one.modules.esg`

获取环境、社会和治理（ESG）评级数据。

**核心接口**:
- `get_esg_rating()` - ESG评分详情
- `get_esg_rating_rank()` - ESG排名

**数据源**: 新浪财经

[详细文档](esg.md)

### 深度分析模块

### 13. 估值分析 (Valuation)

**模块**: `akshare_one.modules.valuation`

获取股票PE、PB、PS等估值指标和市场估值数据。

**核心接口**:
- `get_stock_valuation()` - 个股估值数据
- `get_market_valuation()` - 市场估值数据

**数据源**: 东方财富、乐估

[详细文档](valuation.md)

### 14. 股东数据 (Shareholder)

**模块**: `akshare_one.modules.shareholder`

获取股东增减持、十大股东和机构持仓数据。

**核心接口**:
- `get_shareholder_changes()` - 股东增减持
- `get_top_shareholders()` - 十大股东
- `get_institution_holdings()` - 机构持仓

**数据源**: 东方财富、上交所

[详细文档](shareholder.md)

### 15. 业绩快报 (Performance)

**模块**: `akshare_one.modules.performance`

获取上市公司业绩预告和业绩快报数据。

**核心接口**:
- `get_performance_forecast()` - 业绩预告
- `get_performance_express()` - 业绩快报

**数据源**: 东方财富

[详细文档](performance.md)

### 16. 分析师研报 (Analyst)

**模块**: `akshare_one.modules.analyst`

获取分析师排名和个股研报数据。

**核心接口**:
- `get_analyst_rank()` - 分析师排名
- `get_research_report()` - 个股研报

**数据源**: 东方财富

[详细文档](analyst.md)

### 17. 市场情绪 (Sentiment)

**模块**: `akshare_one.modules.sentiment`

获取热门股票排行和市场情绪数据。

**核心接口**:
- `get_hot_rank()` - 热门排行
- `get_stock_sentiment()` - 个股情绪

**数据源**: 东方财富

[详细文档](sentiment.md)

## 共同特点

### 统一的接口设计

所有扩展模块遵循一致的 API 设计：

```python
# 通用参数模式
def get_module_data(
    symbol: str,           # 股票代码（可选）
    start_date: str,       # 开始日期
    end_date: str,         # 结束日期
    **kwargs               # 模块特定参数
) -> pd.DataFrame:
    """返回标准化的DataFrame"""
    pass
```

### 标准化的输出格式

所有模块返回 `pandas.DataFrame`，具有：
- 清晰的英文列名（snake_case）
- 一致的数据类型
- JSON 友好（无 NaN/Infinity）
- 统一的日期格式（YYYY-MM-DD）

### 统一的异常处理

所有模块使用项目标准的异常类：

- `InvalidParameterError` - 参数无效
- `DataSourceUnavailableError` - 数据源不可用
- `NoDataError` - 无可用数据

### 智能缓存

内置 LRU 缓存，自动优化性能：

- 实时数据: 5-10 分钟 TTL
- 历史数据: 24 小时 TTL

## 使用示例

### 批量获取多个模块数据

```python
from akshare_one.modules import (
    fundflow,
    northbound,
    macro,
)

# 资金流分析
fund_flow = fundflow.get_stock_fund_flow("600000", "2024-01-01", "2024-12-31")

# 北向资金追踪
north_holdings = northbound.get_northbound_holdings("600000", "2024-01-01", "2024-12-31")

# 宏观数据
cpi = macro.get_cpi_data("2024-01-01", "2024-12-31")
```

### 数据合并分析

由于所有模块返回标准格式，可以轻松合并：

```python
import pandas as pd

# 获取不同模块数据
df1 = fundflow.get_stock_fund_flow("600000", start_date, end_date)
df2 = northbound.get_northbound_holdings("600000", start_date, end_date)
df3 = disclosure.get_dividend_data("600000", start_date, end_date)

# 直接按日期合并
merged = df1.merge(df2, on=['date', 'symbol'], how='outer')
merged = merged.merge(df3, on=['date', 'symbol'], how='outer')
```

## 模块对比

| 模块 | 数据源 | 更新频率 | 延迟 | 使用场景 |
|------|--------|----------|------|----------|
| 指数数据 | 东方财富/新浪 | 实时 | 低 | 大盘分析、指数基金 |
| ETF基金 | 东方财富/新浪 | 实时 | 低 | ETF投资、基金分析 |
| 可转债 | 东方财富/集思录 | 实时 | 低 | 可转债投资 |
| 行业板块 | 东方财富 | 实时 | 低 | 行业轮动分析 |
| 概念板块 | 东方财富 | 实时 | 低 | 热点概念追踪 |
| 港股美股 | 东方财富 | 实时 | 低 | 港股投资分析 |
| 科创板创业板 | 东方财富 | 实时 | 低 | 特殊板块分析 |
| 新股次新 | 东方财富/巨潮资讯 | 日度 | 低 | IPO分析、次新跟踪 |
| ST股票 | 东方财富 | 日度 | 低 | 风险监控、摘帽博弈 |
| 停复牌 | 东方财富 | 实时 | 低 | 停牌风险监控 |
| 资金流 | 东方财富 | 实时 | 低 | 短线交易、资金分析 |
| 公告信披 | 多源 | 事件驱动 | 低 | 事件驱动策略 |
| 北向资金 | 东方财富 | T+1 | 中 | 外资流向分析 |
| 宏观数据 | 官方 | 月度 | 高 | 宏观经济分析 |
| 大宗交易 | 东方财富 | 日频 | 低 | 大宗交易分析 |
| 龙虎榜 | 东方财富 | 日频 | 低 | 异动交易分析 |
| 涨停池 | 东方财富 | 日频 | 低 | 涨停跌停分析 |
| 融资融券 | 东方财富 | 日频 | 低 | 杠杆资金分析 |
| 股权质押 | 东方财富 | 日频 | 低 | 股权质押分析 |
| 限售解禁 | 东方财富 | 日频 | 低 | 解禁压力分析 |
| 商誉 | 东方财富 | 季度 | 中 | 商誉风险分析 |
| ESG评级 | 新浪财经 | 季度 | 中 | ESG投资分析 |
| 估值分析 | 东方财富/乐估 | 日频 | 低 | 价值分析、选股 |
| 股东数据 | 东方财富/上交所 | 日频 | 中 | 股东分析、跟庄策略 |
| 业绩快报 | 东方财富 | 季度 | 中 | 业绩分析、基本面 |
| 分析师研报 | 东方财富 | 日频 | 中 | 研报跟踪、分析师跟踪 |
| 市场情绪 | 东方财富 | 实时 | 低 | 情绪分析、逆向投资 |

## 性能考虑

### 缓存策略

扩展模块自动受益于缓存系统：
- 高频查询（如资金流）缓存5-10分钟
- 历史数据（如宏观数据）缓存24小时

### 请求限制

部分数据源有频率限制：
- **东方财富**: 建议间隔 0.5 秒以上
- **新浪财经**: 建议间隔 1 秒以上

### 批量查询

某些模块支持批量查询（返回多只股票数据），可以显著提升效率：

```python
# 批量获取资金流（如果支持）
df = fundflow.get_stock_fund_flow(
    symbol=None,  # 获取所有股票
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## 最佳实践

1. ✅ **使用时间范围限制** - 避免查询过多历史数据
2. ✅ **利用缓存** - 重复查询几乎零成本
3. ✅ **处理异常** - 使用 try-except 捕获 `DataSourceUnavailableError`
4. ✅ **监测频率** - 避免触发限流
5. ✅ **合并数据** - 使用标准键（date, symbol）合并多模块数据
6. ✅ **验证数据** - 检查 DataFrame 是否为空

## 扩展性

该架构易于扩展新的数据模块。参考 [开发文档/架构设计](../development/architecture.md) 了解如何实现新的数据模块。

## 反馈与支持

- **Issues**: [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)
- **文档**: 各模块详细文档见下方链接
- **示例**: [examples/](../../examples/) 目录

## 相关文档

### 基础数据
- [指数数据](index.md) - 指数行情和成分股
- [ETF基金](etf.md) - ETF数据和基金信息
- [可转债](bond.md) - 可转债数据

### 市场分析
- [资金流详细文档](fundflow.md)
- [公告信披详细文档](disclosure.md)
- [北向资金详细文档](northbound.md)
- [宏观数据详细文档](macro.md)

### 深度分析
- [估值分析](valuation.md)
- [股东数据](shareholder.md)
- [业绩快报](performance.md)
- [分析师研报](analyst.md)
- [市场情绪](sentiment.md)

### 其他
- [错误处理指南](../advanced/error-handling.md)
- [性能优化指南](../advanced/performance.md)

---

**快速导航**: 选择您需要的模块开始使用！
