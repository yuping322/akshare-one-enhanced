# AKShare-One 缺失接口分析

## 当前已实现的接口（akshare-one）

### ✅ 已覆盖的 Primitive Views

1. **PV.HistOHLCV** ✅ 完全覆盖
   - `get_hist_data()` - 支持 eastmoney, eastmoney_direct, sina
   - 支持多周期：minute, hour, day, week, month, year
   - 支持复权：none, qfq, hfq

2. **PV.RealtimeQuotes** ✅ 完全覆盖
   - `get_realtime_data()` - 支持 eastmoney, eastmoney_direct, xueqiu
   - 返回实时行情和盘口数据

3. **PV.BasicInfo** ✅ 完全覆盖
   - `get_basic_info()` - 支持 eastmoney
   - 返回基础信息、行业、上市日期等

4. **PV.FinStatements** ✅ 完全覆盖
   - `get_balance_sheet()` - 资产负债表
   - `get_income_statement()` - 利润表
   - `get_cash_flow()` - 现金流量表

5. **PV.FinMetrics** ✅ 完全覆盖
   - `get_financial_metrics()` - 财务关键指标

6. **PV.InsiderMgmt** ✅ 完全覆盖
   - `get_inner_trade_data()` - 内部交易数据

7. **期货/期权** ✅ 已实现
   - `get_futures_hist_data()`, `get_futures_realtime_data()`
   - `get_options_chain()`, `get_options_realtime()`

---

## ❌ 缺失的 Primitive Views（需要补充）

### 高优先级（P0）- 影响多个 skills

#### 1. **PV.DisclosureNews** (公告/信披/交易提示) ❌
**影响**: 5 个 skills
- disclosure-notice-monitor
- dividend-corporate-action-tracker
- high-dividend-strategy
- share-repurchase-monitor
- st-delist-risk-scanner

**需要的接口**:
```python
# 公告数据
get_disclosure_news(symbol, start_date, end_date, category)
# category: 'all', 'dividend', 'repurchase', 'st', 'delist', 'major_event'

# 分红派息
get_dividend_data(symbol, start_date, end_date)

# 股票回购
get_repurchase_data(symbol, start_date, end_date)

# ST/退市风险
get_st_delist_data(symbol)
```

**akshare 原始接口**:
- `stock_notice_report()` - 东方财富公告
- `stock_dividend_cninfo()` - 巨潮分红
- `stock_repurchase_em()` - 东方财富回购
- `stock_stop()` - 停牌数据

---

#### 2. **PV.FundFlow** (资金流/主力/板块) ❌
**影响**: 6 个 skills
- fund-flow-monitor
- hsgt-holdings-monitor
- industry-board-analyzer
- industry-chain-mapper
- northbound-flow-analyzer
- sector-rotation-detector

**需要的接口**:
```python
# 个股资金流
get_stock_fund_flow(symbol, start_date, end_date)

# 板块资金流
get_sector_fund_flow(sector_type, start_date, end_date)
# sector_type: 'industry', 'concept'

# 主力资金
get_main_fund_flow(symbol, start_date, end_date)

# 行业板块列表和成分股
get_industry_constituents(industry_name)
get_concept_constituents(concept_name)
```

**akshare 原始接口**:
- `stock_individual_fund_flow_rank()` - 个股资金流排名
- `stock_market_fund_flow()` - 大盘资金流
- `stock_sector_fund_flow_rank()` - 板块资金流排名
- `stock_board_industry_name_em()` - 行业板块列表
- `stock_board_industry_cons_em()` - 行业成分股

---

#### 3. **PV.NorthboundHSGT** (沪深港通/北向) ❌
**影响**: 2 个 skills
- hsgt-holdings-monitor
- northbound-flow-analyzer

**需要的接口**:
```python
# 北向资金流向
get_northbound_flow(start_date, end_date, market)
# market: 'sh', 'sz', 'all'

# 北向持股明细
get_northbound_holdings(symbol, start_date, end_date)

# 北向资金排名
get_northbound_top_stocks(date, market, top_n)
```

**akshare 原始接口**:
- `stock_hsgt_hist_em()` - 沪深港通历史数据
- `stock_hsgt_hold_stock_em()` - 北向持股明细
- `stock_hsgt_board_rank_em()` - 北向资金排名

---

#### 4. **PV.BlockDeal** (大宗交易) ❌
**影响**: 1 个 skill
- block-deal-monitor

**需要的接口**:
```python
# 大宗交易数据
get_block_deal(symbol, start_date, end_date)

# 大宗交易统计
get_block_deal_summary(start_date, end_date)
```

**akshare 原始接口**:
- `stock_dzjy_mrmx()` - 东方财富大宗交易明细
- `stock_dzjy_mrtj()` - 东方财富大宗交易统计

---

### 中优先级（P1）

#### 5. **PV.DragonTigerLHB** (龙虎榜) ❌
**影响**: 1 个 skill
- dragon-tiger-list-analyzer

**需要的接口**:
```python
# 龙虎榜数据
get_dragon_tiger_list(date, symbol)

# 龙虎榜统计
get_dragon_tiger_summary(start_date, end_date)

# 营业部统计
get_dragon_tiger_broker_stats(start_date, end_date)
```

**akshare 原始接口**:
- `stock_lhb_detail_em()` - 龙虎榜详情
- `stock_lhb_ggtj_em()` - 龙虎榜个股统计
- `stock_lhb_jgmx_em()` - 龙虎榜机构明细

---

#### 6. **PV.LimitUpDown** (涨停池/强势股池) ❌
**影响**: 1 个 skill
- limit-up-pool-analyzer

**需要的接口**:
```python
# 涨停池
get_limit_up_pool(date)

# 跌停池
get_limit_down_pool(date)

# 涨停统计
get_limit_up_stats(start_date, end_date)
```

**akshare 原始接口**:
- `stock_zt_pool_em()` - 涨停池
- `stock_zt_pool_previous_em()` - 昨日涨停池
- `stock_zt_pool_strong_em()` - 强势股池

---

#### 7. **PV.MarginFinancing** (融资融券) ❌
**影响**: 1 个 skill
- margin-risk-monitor

**需要的接口**:
```python
# 融资融券数据
get_margin_data(symbol, start_date, end_date)

# 融资融券汇总
get_margin_summary(start_date, end_date, market)
# market: 'sh', 'sz', 'all'
```

**akshare 原始接口**:
- `stock_margin_detail_em()` - 融资融券明细
- `stock_margin_underlying_info_em()` - 融资融券标的
- `stock_margin_sse()` - 上交所融资融券
- `stock_margin_szse()` - 深交所融资融券

---

#### 8. **PV.EquityPledge** (股权质押) ❌
**影响**: 1 个 skill
- equity-pledge-risk-monitor

**需要的接口**:
```python
# 股权质押数据
get_equity_pledge(symbol, start_date, end_date)

# 股权质押统计
get_equity_pledge_summary(date)

# 质押比例排名
get_equity_pledge_ratio_rank(date, top_n)
```

**akshare 原始接口**:
- `stock_gpzy_pledge_ratio_em()` - 质押比例
- `stock_gpzy_pledge_detail_em()` - 质押明细
- `stock_gpzy_industry_data_em()` - 行业质押数据

---

#### 9. **PV.RestrictedRelease** (限售解禁) ❌
**影响**: 1 个 skill
- ipo-lockup-risk-monitor

**需要的接口**:
```python
# 限售解禁数据
get_restricted_release(symbol, start_date, end_date)

# 解禁日历
get_restricted_release_calendar(start_date, end_date)
```

**akshare 原始接口**:
- `stock_restricted_release_queue_em()` - 解禁日历
- `stock_restricted_release_detail_em()` - 解禁明细

---

#### 10. **PV.Goodwill** (商誉/减值) ❌
**影响**: 1 个 skill
- goodwill-risk-monitor

**需要的接口**:
```python
# 商誉数据
get_goodwill_data(symbol, start_date, end_date)

# 商誉减值预期
get_goodwill_impairment(date)

# 行业商誉统计
get_goodwill_by_industry(date)
```

**akshare 原始接口**:
- `stock_sy_profile_em()` - 商誉概况
- `stock_sy_yq_em()` - 商誉减值预期
- `stock_sy_jz_em()` - 商誉减值明细
- `stock_sy_hy_em()` - 行业商誉

---

#### 11. **PV.MacroCN** (LPR/PMI/CPI/M2/Shibor/社融) ❌
**影响**: 3 个 skills
- liquidity-impact-estimator
- macro-liquidity-monitor
- policy-sensitivity-brief

**需要的接口**:
```python
# LPR利率
get_lpr_rate(start_date, end_date)

# PMI指数
get_pmi_index(start_date, end_date, pmi_type)
# pmi_type: 'manufacturing', 'non_manufacturing', 'caixin'

# CPI/PPI
get_cpi_data(start_date, end_date)
get_ppi_data(start_date, end_date)

# M2货币供应
get_m2_supply(start_date, end_date)

# Shibor利率
get_shibor_rate(start_date, end_date)

# 社会融资规模
get_social_financing(start_date, end_date)
```

**akshare 原始接口**:
- `macro_china_lpr()` - LPR
- `macro_china_pmi()` - PMI
- `macro_china_cpi()` - CPI
- `macro_china_ppi()` - PPI
- `macro_china_m2()` - M2
- `macro_china_shibor()` - Shibor
- `macro_china_shrzgm()` - 社融

---

#### 12. **PV.ESG** (ESG评分/等级) ❌
**影响**: 1 个 skill
- esg-screener

**需要的接口**:
```python
# ESG评分
get_esg_rating(symbol, start_date, end_date)

# ESG评级排名
get_esg_rating_rank(date, industry, top_n)
```

**akshare 原始接口**:
- `stock_esg_rate_sina()` - 新浪ESG评级
- `stock_esg_hz_sina()` - 华证ESG评级

---

## 📊 优先级总结

### P0 - 立即实现（影响多个 skills）
1. ✅ **PV.HistOHLCV** - 已实现
2. ✅ **PV.RealtimeQuotes** - 已实现
3. ✅ **PV.BasicInfo** - 已实现
4. ❌ **PV.DisclosureNews** - 缺失（影响 5 个 skills）
5. ❌ **PV.FundFlow** - 缺失（影响 6 个 skills）
6. ❌ **PV.NorthboundHSGT** - 缺失（影响 2 个 skills）

### P1 - 重要实现
7. ❌ **PV.BlockDeal** - 缺失（影响 1 个 skill）
8. ✅ **PV.FinStatements** - 已实现
9. ✅ **PV.FinMetrics** - 已实现
10. ✅ **PV.InsiderMgmt** - 已实现
11. ❌ **PV.MacroCN** - 缺失（影响 3 个 skills）

### P2 - 可选实现
12. ❌ **PV.DragonTigerLHB** - 缺失
13. ❌ **PV.LimitUpDown** - 缺失
14. ❌ **PV.MarginFinancing** - 缺失
15. ❌ **PV.EquityPledge** - 缺失
16. ❌ **PV.RestrictedRelease** - 缺失
17. ❌ **PV.Goodwill** - 缺失
18. ❌ **PV.ESG** - 缺失

---

## 🎯 建议实现顺序

### Phase 1: 核心市场数据（P0）
1. **PV.FundFlow** - 资金流数据（影响 6 个 skills）
2. **PV.DisclosureNews** - 公告信披（影响 5 个 skills）
3. **PV.NorthboundHSGT** - 北向资金（影响 2 个 skills）

### Phase 2: 宏观和特色数据（P1）
4. **PV.MacroCN** - 宏观数据（影响 3 个 skills）
5. **PV.BlockDeal** - 大宗交易（影响 1 个 skill）

### Phase 3: 专项监控数据（P2）
6. **PV.DragonTigerLHB** - 龙虎榜
7. **PV.LimitUpDown** - 涨停池
8. **PV.MarginFinancing** - 融资融券
9. **PV.EquityPledge** - 股权质押
10. **PV.RestrictedRelease** - 限售解禁
11. **PV.Goodwill** - 商誉
12. **PV.ESG** - ESG评级

---

## 📝 实现建议

### 1. 遵循现有架构
- 使用 Factory + Provider 模式
- 支持多数据源
- 统一返回格式

### 2. 模块组织
```
src/akshare_one/modules/
├── disclosure/      # PV.DisclosureNews
├── fundflow/        # PV.FundFlow
├── northbound/      # PV.NorthboundHSGT
├── blockdeal/       # PV.BlockDeal
├── macro/           # PV.MacroCN
├── lhb/             # PV.DragonTigerLHB
├── limitup/         # PV.LimitUpDown
├── margin/          # PV.MarginFinancing
├── pledge/          # PV.EquityPledge
├── restricted/      # PV.RestrictedRelease
├── goodwill/        # PV.Goodwill
└── esg/             # PV.ESG
```

### 3. 接口命名规范
- 单数据源: `get_xxx_data(symbol, source="eastmoney")`
- 多数据源: `get_xxx_data_multi_source(symbol, sources=None)`

### 4. 数据标准化
- 统一字段名称（英文）
- 统一数据类型
- 统一日期格式（YYYY-MM-DD）
- 统一时间戳格式

---

## 🔍 下一步行动

建议从 **Phase 1** 开始，优先实现：

1. **PV.FundFlow** - 资金流数据模块
   - 影响最多 skills (6个)
   - 数据源明确（东方财富）
   - 实现难度中等

2. **PV.DisclosureNews** - 公告信披模块
   - 影响 5 个 skills
   - 数据源明确（东方财富、巨潮）
   - 实现难度中等

3. **PV.NorthboundHSGT** - 北向资金模块
   - 影响 2 个 skills
   - 数据源明确（东方财富）
   - 实现难度较低
