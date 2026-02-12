# Implementation Tasks: 市场数据扩展接口

## Phase 1: 基础设施 + P0 接口 (Week 1-2)

### 1. 基础设施搭建
- [x] 1.1 创建 BaseProvider 抽象类
  - 定义通用接口方法
  - 实现 JSON 兼容性工具函数
  - 实现参数验证工具
  - 添加元数据属性支持
- [x] 1.2 创建异常类体系
  - MarketDataError 基类
  - InvalidParameterError
  - DataSourceUnavailableError
  - NoDataError
  - UpstreamChangedError
- [x] 1.3 建立测试框架
  - 单元测试模板
  - 契约测试（golden sample）框架
  - 集成测试工具

### 2. PV.FundFlow - 资金流数据
- [x] 2.1 创建模块结构
  - `modules/fundflow/__init__.py`
  - `modules/fundflow/base.py`
  - `modules/fundflow/factory.py`
  - `modules/fundflow/eastmoney.py`
- [x] 2.2 实现 FundFlowProvider 基类
  - 定义抽象方法
  - 实现数据标准化方法
  - 添加元数据属性
- [x] 2.3 实现个股资金流接口
  - `get_stock_fund_flow()`
  - 调用 akshare 原始接口
  - 数据标准化和 JSON 兼容性处理
  - 参数验证
- [x] 2.4 实现板块资金流接口
  - `get_sector_fund_flow()`
  - 支持行业和概念板块
  - 数据标准化
- [x] 2.5 实现主力资金排名接口
  - `get_main_fund_flow_rank()`
  - 支持多种排序指标
- [x] 2.6 实现板块列表和成分股接口
  - `get_industry_list()`
  - `get_industry_constituents()`
  - `get_concept_list()`
  - `get_concept_constituents()`
- [x] 2.7 实现 FundFlowFactory
  - 创建 Provider 实例
  - 支持多数据源（预留）
- [x] 2.8 添加公共接口到 __init__.py
  - `get_stock_fund_flow()`
  - `get_sector_fund_flow()`
  - `get_main_fund_flow_rank()`
  - `get_industry_list()`
  - `get_industry_constituents()`
  - `get_concept_list()`
  - `get_concept_constituents()`
- [x] 2.9 编写单元测试
  - 测试数据获取
  - 测试 JSON 兼容性
  - 测试参数验证
  - 测试空结果处理
- [x] 2.10 编写契约测试
  - 建立 golden sample
  - 测试字段稳定性
- [x] 2.11 编写集成测试
  - 测试完整流程
  - 测试真实数据获取

### 3. PV.DisclosureNews - 公告信披
- [x] 3.1 创建模块结构
  - `modules/disclosure/__init__.py`
  - `modules/disclosure/base.py`
  - `modules/disclosure/factory.py`
  - `modules/disclosure/eastmoney.py`
- [x] 3.2 实现 DisclosureProvider 基类
  - 定义抽象方法
  - 实现数据标准化方法
- [x] 3.3 实现公告数据接口
  - `get_disclosure_news()`
  - 支持按类别筛选
  - 数据标准化
- [x] 3.4 实现分红派息接口
  - `get_dividend_data()`
  - 支持单股票和全市场查询
  - 数据标准化
- [x] 3.5 实现股票回购接口
  - `get_repurchase_data()`
  - 回购进度追踪
  - 数据标准化
- [x] 3.6 实现 ST/退市风险接口
  - `get_st_delist_data()`
  - 风险等级分类
- [x] 3.7 实现 DisclosureFactory
- [x] 3.8 添加公共接口到 __init__.py
  - `get_disclosure_news()`
  - `get_dividend_data()`
  - `get_repurchase_data()`
  - `get_st_delist_data()`
- [x] 3.9 编写单元测试
- [x] 3.10 编写契约测试
- [x] 3.11 编写集成测试

### 4. PV.NorthboundHSGT - 北向资金
- [x] 4.1 创建模块结构
  - `modules/northbound/__init__.py`
  - `modules/northbound/base.py`
  - `modules/northbound/factory.py`
  - `modules/northbound/eastmoney.py`
- [x] 4.2 实现 NorthboundProvider 基类
- [x] 4.3 实现北向资金流向接口
  - `get_northbound_flow()`
  - 支持沪深市场分别查询
  - 数据标准化
- [x] 4.4 实现北向持股明细接口
  - `get_northbound_holdings()`
  - 支持历史持仓追踪
  - 数据标准化
- [x] 4.5 实现北向资金排名接口
  - `get_northbound_top_stocks()`
  - 支持 Top N 查询
- [x] 4.6 实现 NorthboundFactory
- [x] 4.7 添加公共接口到 __init__.py
  - `get_northbound_flow()`
  - `get_northbound_holdings()`
  - `get_northbound_top_stocks()`
- [x] 4.8 编写单元测试
- [x] 4.9 编写契约测试
- [x] 4.10 编写集成测试

## Phase 2: P1 接口 (Week 3)

### 5. PV.MacroCN - 宏观数据
- [x] 5.1 创建模块结构
  - `modules/macro/__init__.py`
  - `modules/macro/base.py`
  - `modules/macro/factory.py`
  - `modules/macro/official.py`
- [x] 5.2 实现 MacroProvider 基类
- [x] 5.3 实现 LPR 利率接口
  - `get_lpr_rate()`
  - 数据标准化
- [x] 5.4 实现 PMI 指数接口
  - `get_pmi_index()`
  - 支持制造业/非制造业/财新 PMI
  - 数据标准化
- [x] 5.5 实现 CPI/PPI 接口
  - `get_cpi_data()`
  - `get_ppi_data()`
  - 数据标准化
- [x] 5.6 实现 M2 货币供应接口
  - `get_m2_supply()`
  - 数据标准化
- [x] 5.7 实现 Shibor 利率接口
  - `get_shibor_rate()`
  - 支持多期限
  - 数据标准化
- [x] 5.8 实现社会融资规模接口
  - `get_social_financing()`
  - 数据标准化
- [x] 5.9 实现 MacroFactory
- [x] 5.10 添加公共接口到 __init__.py
- [x] 5.11 编写单元测试
- [x] 5.12 编写契约测试
- [x] 5.13 编写集成测试

### 6. PV.BlockDeal - 大宗交易
- [x] 6.1 创建模块结构
  - `modules/blockdeal/__init__.py`
  - `modules/blockdeal/base.py`
  - `modules/blockdeal/factory.py`
  - `modules/blockdeal/eastmoney.py`
- [x] 6.2 实现 BlockDealProvider 基类
- [x] 6.3 实现大宗交易明细接口
  - `get_block_deal()`
  - 支持个股和全市场查询
  - 计算折溢价率
  - 数据标准化
- [x] 6.4 实现大宗交易统计接口
  - `get_block_deal_summary()`
  - 支持多维度分组
  - 数据标准化
- [x] 6.5 实现 BlockDealFactory
- [x] 6.6 添加公共接口到 __init__.py
- [x] 6.7 编写单元测试
- [x] 6.8 编写契约测试
- [x] 6.9 编写集成测试

## Phase 3: P2 接口 (Week 4-5)

### 7. PV.DragonTigerLHB - 龙虎榜
- [x] 7.1 创建模块结构
- [x] 7.2 实现 DragonTigerProvider 基类
- [x] 7.3 实现龙虎榜数据接口
  - `get_dragon_tiger_list()`
  - 数据标准化
- [x] 7.4 实现龙虎榜统计接口
  - `get_dragon_tiger_summary()`
  - 支持多维度分组
- [x] 7.5 实现营业部统计接口
  - `get_dragon_tiger_broker_stats()`
- [x] 7.6 实现 Factory 和公共接口
- [x] 7.7 编写测试

### 8. PV.LimitUpDown - 涨停池
- [x] 8.1 创建模块结构
- [x] 8.2 实现 LimitUpDownProvider 基类
- [x] 8.3 实现涨停池接口
  - `get_limit_up_pool()`
  - 数据标准化
- [x] 8.4 实现跌停池接口
  - `get_limit_down_pool()`
- [x] 8.5 实现涨停统计接口
  - `get_limit_up_stats()`
- [x] 8.6 实现 Factory 和公共接口
- [x] 8.7 编写测试

### 9. PV.MarginFinancing - 融资融券
- [x] 9.1 创建模块结构
- [x] 9.2 实现 MarginProvider 基类
- [x] 9.3 实现融资融券数据接口
  - `get_margin_data()`
  - 支持个股和全市场
  - 数据标准化
- [x] 9.4 实现融资融券汇总接口
  - `get_margin_summary()`
  - 支持市场分组
- [x] 9.5 实现 Factory 和公共接口
- [x] 9.6 编写测试

### 10. PV.EquityPledge - 股权质押
- [x] 10.1 创建模块结构
- [x] 10.2 实现 EquityPledgeProvider 基类
- [x] 10.3 实现股权质押数据接口
  - `get_equity_pledge()`
  - 数据标准化
- [x] 10.4 实现质押比例排名接口
  - `get_equity_pledge_ratio_rank()`
- [x] 10.5 实现 Factory 和公共接口
- [x] 10.6 编写测试

### 11. PV.RestrictedRelease - 限售解禁
- [x] 11.1 创建模块结构
- [x] 11.2 实现 RestrictedReleaseProvider 基类
- [x] 11.3 实现限售解禁数据接口
  - `get_restricted_release()`
  - 数据标准化
- [x] 11.4 实现解禁日历接口
  - `get_restricted_release_calendar()`
- [x] 11.5 实现 Factory 和公共接口
- [x] 11.6 编写测试

### 12. PV.Goodwill - 商誉
- [x] 12.1 创建模块结构
- [x] 12.2 实现 GoodwillProvider 基类
- [x] 12.3 实现商誉数据接口
  - `get_goodwill_data()`
  - 数据标准化
- [x] 12.4 实现商誉减值预期接口
  - `get_goodwill_impairment()`
- [x] 12.5 实现行业商誉统计接口
  - `get_goodwill_by_industry()`
- [x] 12.6 实现 Factory 和公共接口
- [x] 12.7 编写测试

### 13. PV.ESG - ESG 评级
- [x] 13.1 创建模块结构
- [x] 13.2 实现 ESGProvider 基类
- [x] 13.3 实现 ESG 评分接口
  - `get_esg_rating()`
  - 数据标准化
- [x] 13.4 实现 ESG 评级排名接口
  - `get_esg_rating_rank()`
  - 支持行业筛选
- [x] 13.5 实现 Factory 和公共接口
- [x] 13.6 编写测试

## Phase 4: 文档和发布 (Week 6)

### 14. 文档完善
- [x] 14.1 更新 README.md
  - 添加新接口列表
  - 添加使用示例
  - 更新功能特性说明
- [x] 14.2 更新 CHANGELOG.md
  - 记录新增接口
  - 记录重要变更
- [x] 14.3 完善 API 文档
  - 确保所有接口有完整 docstring
  - 添加更多使用示例
- [x] 14.4 编写迁移指南
  - 从 akshare 迁移到 akshare-one
  - 接口对照表

### 15. 性能优化和测试
- [x] 15.1 性能测试
  - 测试响应时间
  - 测试并发性能
  - 测试内存使用
- [x] 15.2 性能优化
  - 优化慢接口
  - 减少内存占用
  - 优化 JSON 序列化
- [x] 15.3 端到端测试
  - 测试所有接口
  - 测试真实场景
  - 测试错误处理

### 16. 发布准备
- [x] 16.1 代码审查
  - 检查代码质量
  - 检查测试覆盖率
  - 检查文档完整性
- [x] 16.2 版本发布
  - 更新版本号
  - 创建 Git tag
  - 发布到 PyPI
- [x] 16.3 发布公告
  - 编写发布说明
  - 通知用户

## 验收标准

### 功能完整性
- [x] 实现所有 12 个 Primitive Views
- [x] 每个接口至少支持 1 个数据源
- [x] 数据字段标准化符合规范
- [x] JSON 兼容性 100%
- [x] 错误处理机制完善
- [x] 空结果正确处理

### 代码质量
- [x] 代码覆盖率 >= 80%
- [x] 所有单元测试通过
- [x] 所有集成测试通过
- [x] 契约测试建立
- [x] 代码符合 PEP 8 规范
- [x] 类型注解完整

### 文档完整性
- [x] API 文档完整
- [x] 每个接口至少 2 个示例
- [x] README 更新
- [x] CHANGELOG 更新
- [x] 迁移指南完整

### 性能达标
- [x] 单次请求响应时间 < 10 秒（95%）
- [x] 支持并发调用
- [x] 内存使用合理
- [x] JSON 序列化成功率 100%

### 兼容性
- [x] 与现有接口风格一致
- [x] 不破坏现有功能
- [x] 向后兼容
- [x] 符合 view-api-spec.zh.md 规范
