# Feature Requirements: 市场数据扩展接口

## 1. 功能概述

为 akshare-one 添加 12 个缺失的市场数据接口，覆盖资金流、公告信披、北向资金、宏观数据、大宗交易、龙虎榜、涨停池、融资融券、股权质押、限售解禁、商誉和 ESG 评级等核心数据维度。

## 2. 背景

### 2.1 现状

akshare-one 目前已实现 7 个核心接口：
- ✅ PV.HistOHLCV - 历史行情
- ✅ PV.RealtimeQuotes - 实时行情
- ✅ PV.BasicInfo - 基础信息
- ✅ PV.FinStatements - 财务报表
- ✅ PV.FinMetrics - 财务指标
- ✅ PV.InsiderMgmt - 内部交易
- ✅ 期货/期权 - 衍生品

### 2.2 问题

缺失 12 个重要的市场数据接口，影响 20+ 个上层 skills 的功能实现：
- 资金流分析
- 公告监控
- 北向资金追踪
- 宏观经济分析
- 市场异常监控
- 风险预警

## 3. 接口清单

### 3.1 P0 - 高优先级（影响多个 skills）

#### 3.1.1 PV.FundFlow - 资金流数据 (影响 6 个 skills)

**用户故事**: 作为量化交易员，我需要获取个股和板块的资金流向数据，用于分析主力资金动向和板块轮动。

**接口需求**:
```python
# 个股资金流
get_stock_fund_flow(symbol: str, start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, 主力净流入, 超大单, 大单, 中单, 小单, 净占比

# 板块资金流
get_sector_fund_flow(
    sector_type: Literal["industry", "concept"],
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 板块名称, 主力净流入, 涨跌幅, 领涨股

# 主力资金排名
get_main_fund_flow_rank(
    date: str,
    indicator: Literal["net_inflow", "net_inflow_rate"]
) -> pd.DataFrame
# 返回: 排名, 股票代码, 股票名称, 主力净流入, 涨跌幅

# 行业板块列表
get_industry_list() -> pd.DataFrame
# 返回: 板块代码, 板块名称, 成分股数量

# 行业成分股
get_industry_constituents(industry_code: str) -> pd.DataFrame
# 返回: 股票代码, 股票名称, 权重

# 概念板块列表
get_concept_list() -> pd.DataFrame
# 返回: 板块代码, 板块名称, 成分股数量

# 概念成分股
get_concept_constituents(concept_code: str) -> pd.DataFrame
# 返回: 股票代码, 股票名称, 权重
```

**验收标准**:
- [ ] 支持获取个股历史资金流数据
- [ ] 支持获取行业/概念板块资金流
- [ ] 支持主力资金排名查询
- [ ] 支持板块成分股查询
- [ ] 数据字段标准化
- [ ] 支持多数据源（eastmoney）

---

#### 3.1.2 PV.DisclosureNews - 公告信披 (影响 5 个 skills)

**用户故事**: 作为投资分析师，我需要及时获取上市公司的公告信息，包括分红、回购、ST 等重要事件。

**接口需求**:
```python
# 公告数据
get_disclosure_news(
    symbol: str | None,
    start_date: str,
    end_date: str,
    category: Literal["all", "dividend", "repurchase", "st", "major_event"]
) -> pd.DataFrame
# 返回: 日期, 股票代码, 公告标题, 公告类型, 公告内容, URL

# 分红派息
get_dividend_data(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 分红年度, 每股分红, 股权登记日, 除权除息日, 派息日

# 股票回购
get_repurchase_data(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 公告日期, 回购进度, 回购金额, 回购数量, 回购价格区间

# ST/退市风险
get_st_delist_data(symbol: str | None) -> pd.DataFrame
# 返回: 股票代码, 股票名称, ST类型, 风险等级, 公告日期
```

**验收标准**:
- [ ] 支持按类别筛选公告
- [ ] 支持分红派息数据查询
- [ ] 支持回购进度追踪
- [ ] 支持 ST/退市风险预警
- [ ] 数据实时性 < 1 小时

---

#### 3.1.3 PV.NorthboundHSGT - 北向资金 (影响 2 个 skills)

**用户故事**: 作为市场分析师，我需要追踪北向资金的流向和持仓变化，判断外资对 A 股的态度。

**接口需求**:
```python
# 北向资金流向
get_northbound_flow(
    start_date: str,
    end_date: str,
    market: Literal["sh", "sz", "all"] = "all"
) -> pd.DataFrame
# 返回: 日期, 市场, 净买入额, 买入额, 卖出额, 余额

# 北向持股明细
get_northbound_holdings(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 股票代码, 持股数量, 持股市值, 持股占比, 持股变化

# 北向资金排名
get_northbound_top_stocks(
    date: str,
    market: Literal["sh", "sz", "all"] = "all",
    top_n: int = 100
) -> pd.DataFrame
# 返回: 排名, 股票代码, 股票名称, 净买入额, 持股数量, 持股占比
```

**验收标准**:
- [ ] 支持沪深市场分别查询
- [ ] 支持历史持仓追踪
- [ ] 支持北向资金排名
- [ ] 数据更新及时（T+1）

---

### 3.2 P1 - 中优先级

#### 3.2.1 PV.MacroCN - 宏观数据 (影响 3 个 skills)

**用户故事**: 作为宏观策略分析师，我需要获取中国宏观经济数据，用于判断市场趋势和政策影响。

**接口需求**:
```python
# LPR 利率
get_lpr_rate(start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, 1年期LPR, 5年期LPR

# PMI 指数
get_pmi_index(
    start_date: str,
    end_date: str,
    pmi_type: Literal["manufacturing", "non_manufacturing", "caixin"]
) -> pd.DataFrame
# 返回: 日期, PMI值, 同比, 环比

# CPI/PPI
get_cpi_data(start_date: str, end_date: str) -> pd.DataFrame
get_ppi_data(start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, 当月, 同比, 环比, 累计

# M2 货币供应
get_m2_supply(start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, M2余额, 同比增长率

# Shibor 利率
get_shibor_rate(start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, 隔夜, 1周, 2周, 1月, 3月, 6月, 9月, 1年

# 社会融资规模
get_social_financing(start_date: str, end_date: str) -> pd.DataFrame
# 返回: 日期, 社融规模, 同比, 环比, 新增人民币贷款
```

**验收标准**:
- [ ] 支持主要宏观指标查询
- [ ] 数据来源权威（央行、统计局）
- [ ] 历史数据完整
- [ ] 更新及时（月度/季度）

---

#### 3.2.2 PV.BlockDeal - 大宗交易 (影响 1 个 skill)

**用户故事**: 作为交易员，我需要监控大宗交易数据，识别机构行为和潜在的价格影响。

**接口需求**:
```python
# 大宗交易明细
get_block_deal(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 股票代码, 成交价, 成交量, 成交额, 买方营业部, 卖方营业部, 折溢价率

# 大宗交易统计
get_block_deal_summary(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "date", "broker"]
) -> pd.DataFrame
# 返回: 分组维度, 成交笔数, 成交总额, 平均折溢价率
```

**验收标准**:
- [ ] 支持个股和全市场查询
- [ ] 支持营业部统计
- [ ] 支持折溢价率计算
- [ ] 数据更新及时（T+1）

---

### 3.3 P2 - 低优先级

#### 3.3.1 PV.DragonTigerLHB - 龙虎榜

**接口需求**:
```python
# 龙虎榜数据
get_dragon_tiger_list(
    date: str,
    symbol: str | None
) -> pd.DataFrame
# 返回: 日期, 股票代码, 上榜原因, 买入额, 卖出额, 净额, 营业部明细

# 龙虎榜统计
get_dragon_tiger_summary(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "broker", "reason"]
) -> pd.DataFrame

# 营业部统计
get_dragon_tiger_broker_stats(
    start_date: str,
    end_date: str,
    top_n: int = 50
) -> pd.DataFrame
```

---

#### 3.3.2 PV.LimitUpDown - 涨停池

**接口需求**:
```python
# 涨停池
get_limit_up_pool(date: str) -> pd.DataFrame
# 返回: 股票代码, 涨停时间, 打开次数, 封单额, 连板数, 涨停原因

# 跌停池
get_limit_down_pool(date: str) -> pd.DataFrame

# 涨停统计
get_limit_up_stats(
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 涨停家数, 跌停家数, 炸板率
```

---

#### 3.3.3 PV.MarginFinancing - 融资融券

**接口需求**:
```python
# 融资融券数据
get_margin_data(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 股票代码, 融资余额, 融券余额, 融资买入额, 融券卖出量

# 融资融券汇总
get_margin_summary(
    start_date: str,
    end_date: str,
    market: Literal["sh", "sz", "all"]
) -> pd.DataFrame
# 返回: 日期, 市场, 融资余额, 融券余额, 融资融券余额
```

---

#### 3.3.4 PV.EquityPledge - 股权质押

**接口需求**:
```python
# 股权质押数据
get_equity_pledge(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 股东名称, 质押数量, 质押比例, 质押机构, 质押日期

# 质押比例排名
get_equity_pledge_ratio_rank(
    date: str,
    top_n: int = 100
) -> pd.DataFrame
# 返回: 排名, 股票代码, 质押比例, 质押市值
```

---

#### 3.3.5 PV.RestrictedRelease - 限售解禁

**接口需求**:
```python
# 限售解禁数据
get_restricted_release(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 解禁日期, 解禁数量, 解禁市值, 解禁类型, 股东名称

# 解禁日历
get_restricted_release_calendar(
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 日期, 解禁股票数, 解禁总市值
```

---

#### 3.3.6 PV.Goodwill - 商誉

**接口需求**:
```python
# 商誉数据
get_goodwill_data(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 报告期, 商誉余额, 商誉占净资产比, 商誉减值

# 商誉减值预期
get_goodwill_impairment(date: str) -> pd.DataFrame
# 返回: 股票代码, 商誉余额, 预期减值额, 风险等级

# 行业商誉统计
get_goodwill_by_industry(date: str) -> pd.DataFrame
# 返回: 行业名称, 商誉总额, 平均占比, 减值总额
```

---

#### 3.3.7 PV.ESG - ESG 评级

**接口需求**:
```python
# ESG 评分
get_esg_rating(
    symbol: str | None,
    start_date: str,
    end_date: str
) -> pd.DataFrame
# 返回: 股票代码, 评级日期, ESG评分, E评分, S评分, G评分, 评级机构

# ESG 评级排名
get_esg_rating_rank(
    date: str,
    industry: str | None,
    top_n: int = 100
) -> pd.DataFrame
# 返回: 排名, 股票代码, ESG评分, 行业排名
```

---

## 4. 架构要求

### 4.1 模块结构

```
src/akshare_one/modules/
├── fundflow/           # PV.FundFlow
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── eastmoney.py
├── disclosure/         # PV.DisclosureNews
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── eastmoney.py
├── northbound/         # PV.NorthboundHSGT
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── eastmoney.py
├── macro/              # PV.MacroCN
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── official.py     # 官方数据源
├── blockdeal/          # PV.BlockDeal
├── lhb/                # PV.DragonTigerLHB
├── limitup/            # PV.LimitUpDown
├── margin/             # PV.MarginFinancing
├── pledge/             # PV.EquityPledge
├── restricted/         # PV.RestrictedRelease
├── goodwill/           # PV.Goodwill
└── esg/                # PV.ESG
```

### 4.2 设计模式

遵循现有的 Factory + Provider 模式：
- Factory 类负责创建 Provider 实例
- Provider 基类定义抽象方法
- 具体 Provider 实现数据获取和标准化

### 4.3 数据标准化

所有接口返回的 DataFrame 必须：
- 使用英文字段名
- 统一日期格式（YYYY-MM-DD）
- 统一数值类型（float/int）
- 统一缺失值处理（NaN）

## 5. 非功能需求

### 5.1 性能要求
- 单次请求响应时间 < 10 秒
- 支持并发请求
- 合理使用缓存（日线数据缓存 24 小时）

### 5.2 可靠性要求
- 支持多数据源自动切换
- 完善的错误处理和重试机制
- 详细的日志记录

### 5.3 可维护性要求
- 代码覆盖率 >= 80%
- 完整的类型注解
- 详细的文档字符串

## 6. 实现优先级

### Phase 1: P0 接口（Week 1-2）
1. PV.FundFlow - 资金流数据
2. PV.DisclosureNews - 公告信披
3. PV.NorthboundHSGT - 北向资金

### Phase 2: P1 接口（Week 3）
4. PV.MacroCN - 宏观数据
5. PV.BlockDeal - 大宗交易

### Phase 3: P2 接口（Week 4-5）
6. PV.DragonTigerLHB - 龙虎榜
7. PV.LimitUpDown - 涨停池
8. PV.MarginFinancing - 融资融券
9. PV.EquityPledge - 股权质押
10. PV.RestrictedRelease - 限售解禁
11. PV.Goodwill - 商誉
12. PV.ESG - ESG 评级

## 7. 验收标准

### 7.1 功能完整性
- [ ] 实现所有 12 个 Primitive Views
- [ ] 每个接口支持至少 1 个数据源
- [ ] 数据字段标准化符合规范
- [ ] 错误处理机制完善

### 7.2 代码质量
- [ ] 代码覆盖率 >= 80%
- [ ] 通过所有单元测试
- [ ] 通过所有集成测试
- [ ] 代码符合 PEP 8 规范

### 7.3 文档完整性
- [ ] API 文档完整
- [ ] 提供使用示例
- [ ] 更新 README.md
- [ ] 更新 CHANGELOG.md

### 7.4 性能达标
- [ ] 单次请求响应时间 < 10 秒
- [ ] 支持并发请求
- [ ] 缓存机制有效

## 8. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 数据源 API 变更 | 高 | 中 | 多数据源支持，定期监控 |
| 数据格式不一致 | 中 | 低 | 严格的数据标准化 |
| 性能问题 | 中 | 低 | 性能测试，优化代码 |
| 接口数量多 | 中 | 高 | 分阶段实现，优先 P0 |

## 9. 依赖关系

### 9.1 外部依赖
- pandas >= 1.0.0
- requests >= 2.25.0
- akshare (原始数据源)

### 9.2 内部依赖
- akshare_one.modules.multi_source.MultiSourceRouter
- akshare_one.http_client
- akshare_one.modules.cache

## 10. 成功指标

- 12 个接口全部实现并通过测试
- 影响的 20+ 个 skills 可以正常使用数据
- 代码覆盖率 >= 80%
- 用户反馈积极
- 无重大 bug
