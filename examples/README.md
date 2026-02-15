# API 示例程序

本目录包含 akshare-one-enhanced 项目的 12 个市场数据扩展模块的完整示例程序。每个示例程序展示了如何使用相应模块的接口获取和分析数据，包含实际使用场景、错误处理和数据格式化。

## 目录

- [快速开始](#快速开始)
- [依赖要求](#依赖要求)
- [示例列表](#示例列表)
  - [资金流模块](#1-资金流模块-fundflow)
  - [公告信披模块](#2-公告信披模块-disclosure)
  - [北向资金模块](#3-北向资金模块-northbound)
  - [宏观数据模块](#4-宏观数据模块-macro)
  - [大宗交易模块](#5-大宗交易模块-blockdeal)
  - [龙虎榜模块](#6-龙虎榜模块-lhb)
  - [涨停池模块](#7-涨停池模块-limitup)
  - [融资融券模块](#8-融资融券模块-margin)
  - [股权质押模块](#9-股权质押模块-pledge)
  - [限售解禁模块](#10-限售解禁模块-restricted)
  - [商誉模块](#11-商誉模块-goodwill)
  - [ESG 评级模块](#12-esg-评级模块-esg)
- [运行说明](#运行说明)
- [错误处理](#错误处理)
- [相关资源](#相关资源)

## 快速开始

1. **安装依赖**

```bash
# 安装 akshare-one 包
pip install -e .

# 或者从 PyPI 安装
pip install akshare-one
```

2. **运行示例**

```bash
# 运行单个示例
python examples/fundflow_example.py

# 运行所有示例
for file in examples/*_example.py; do
    python "$file"
done
```

## 依赖要求

### 核心依赖

- **Python**: >= 3.10
- **akshare**: >= 1.17.80（数据源）
- **pandas**: 数据处理和格式化（akshare 自带）
- **cachetools**: >= 5.5.0（缓存支持）

### 可选依赖

- **ta-lib**: >= 0.6.4（技术分析，可选）

所有依赖已在 `pyproject.toml` 中定义，安装 akshare-one 时会自动安装。

## 示例列表

### 1. 资金流模块 (FundFlow)

**文件**: `fundflow_example.py`

**描述**: 展示如何获取和分析个股、板块的资金流向数据，追踪主力资金动向。

**覆盖接口** (7个):
- `get_stock_fund_flow` - 个股资金流
- `get_sector_fund_flow` - 板块资金流
- `get_main_fund_flow_rank` - 主力资金排名
- `get_industry_list` - 行业板块列表
- `get_industry_constituents` - 行业成分股
- `get_concept_list` - 概念板块列表
- `get_concept_constituents` - 概念成分股

**使用场景**:
- 追踪个股资金流向
- 分析板块资金轮动
- 主力资金排名分析
- 获取行业和概念板块信息

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/fundflow_example.py
```

---

### 2. 公告信披模块 (Disclosure)

**文件**: `disclosure_example.py`

**描述**: 展示如何获取上市公司公告、分红派息、股票回购和 ST/退市风险数据。

**覆盖接口** (4个):
- `get_disclosure_news` - 公告数据
- `get_dividend_data` - 分红派息
- `get_repurchase_data` - 股票回购
- `get_st_delist_data` - ST/退市风险

**使用场景**:
- 监控分红公告
- 追踪股票回购进展
- 查询公告信息
- ST 和退市风险查询

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/disclosure_example.py
```

---

### 3. 北向资金模块 (Northbound)

**文件**: `northbound_example.py`

**描述**: 展示如何获取北向资金（沪股通、深股通）的流向和持股数据。

**覆盖接口** (3个):
- `get_northbound_flow` - 北向资金流向
- `get_northbound_holdings` - 北向持股明细
- `get_northbound_top_stocks` - 北向资金排名

**使用场景**:
- 分析北向资金流向趋势
- 追踪北向资金持股明细
- 识别北向资金热门股票

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/northbound_example.py
```

---

### 4. 宏观数据模块 (Macro)

**文件**: `macro_example.py`

**描述**: 展示如何获取中国宏观经济数据，包括利率、PMI、CPI、PPI、货币供应量等。

**覆盖接口** (6个):
- `get_lpr_rate` - LPR 利率
- `get_pmi_index` - PMI 指数
- `get_cpi_data` - CPI 数据
- `get_ppi_data` - PPI 数据
- `get_m2_supply` - M2 货币供应
- `get_shibor_rate` - Shibor 利率

**使用场景**:
- 监控 LPR 利率变化
- 追踪 PMI 指数
- 查询 CPI 和 PPI 数据
- 监控货币供应量
- 追踪 Shibor 利率

**数据源**: 官方数据源 (official) - 中国人民银行、国家统计局

**运行**:
```bash
python examples/macro_example.py
```

---

### 5. 大宗交易模块 (BlockDeal)

**文件**: `blockdeal_example.py`

**描述**: 展示如何获取大宗交易明细和统计数据。

**覆盖接口** (2个):
- `get_block_deal` - 大宗交易明细
- `get_block_deal_summary` - 大宗交易统计

**使用场景**:
- 识别大宗交易
- 分析大宗交易统计

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/blockdeal_example.py
```

---

### 6. 龙虎榜模块 (LHB)

**文件**: `lhb_example.py`

**描述**: 展示如何获取龙虎榜数据，追踪游资和机构的交易行为。

**覆盖接口** (3个):
- `get_dragon_tiger_list` - 龙虎榜数据
- `get_dragon_tiger_summary` - 龙虎榜统计
- `get_dragon_tiger_broker_stats` - 营业部统计

**使用场景**:
- 追踪龙虎榜热钱
- 分析龙虎榜统计
- 营业部活跃度分析

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/lhb_example.py
```

---

### 7. 涨停池模块 (LimitUp)

**文件**: `limitup_example.py`

**描述**: 展示如何获取涨停池、跌停池和涨停统计数据。

**覆盖接口** (3个):
- `get_limit_up_pool` - 涨停池
- `get_limit_down_pool` - 跌停池
- `get_limit_up_stats` - 涨停统计

**使用场景**:
- 监控涨停池
- 监控跌停池
- 分析市场情绪

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/limitup_example.py
```

---

### 8. 融资融券模块 (Margin)

**文件**: `margin_example.py`

**描述**: 展示如何获取融资融券数据，分析市场杠杆情况。

**覆盖接口** (2个):
- `get_margin_data` - 融资融券数据
- `get_margin_summary` - 融资融券汇总

**使用场景**:
- 追踪融资融券余额趋势
- 识别高杠杆股票

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/margin_example.py
```

---

### 9. 股权质押模块 (Pledge)

**文件**: `pledge_example.py`

**描述**: 展示如何获取股权质押数据，监控质押风险。

**覆盖接口** (2个):
- `get_equity_pledge` - 股权质押数据
- `get_equity_pledge_ratio_rank` - 质押比例排名

**使用场景**:
- 监控股权质押风险
- 质押比例排名

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/pledge_example.py
```

---

### 10. 限售解禁模块 (Restricted)

**文件**: `restricted_example.py`

**描述**: 展示如何获取限售股解禁数据，分析解禁对市场的影响。

**覆盖接口** (2个):
- `get_restricted_release` - 限售解禁数据
- `get_restricted_release_calendar` - 解禁日历

**使用场景**:
- 追踪限售解禁日历
- 分析解禁对市场的影响

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/restricted_example.py
```

---

### 11. 商誉模块 (Goodwill)

**文件**: `goodwill_example.py`

**描述**: 展示如何获取商誉数据，监控商誉减值风险。

**覆盖接口** (3个):
- `get_goodwill_data` - 商誉数据
- `get_goodwill_impairment` - 商誉减值预期
- `get_goodwill_by_industry` - 行业商誉统计

**使用场景**:
- 监控商誉减值风险
- 行业商誉对比
- 查询个股商誉数据

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/goodwill_example.py
```

---

### 12. ESG 评级模块 (ESG)

**文件**: `esg_example.py`

**描述**: 展示如何获取 ESG（环境、社会、治理）评级数据。

**覆盖接口** (2个):
- `get_esg_rating` - ESG 评分
- `get_esg_rating_rank` - ESG 评级排名

**使用场景**:
- ESG 评级分析
- 行业 ESG 对比

**数据源**: 东方财富 (eastmoney)

**运行**:
```bash
python examples/esg_example.py
```

---

## 运行说明

### 单个示例运行

```bash
# 进入项目根目录
cd akshare-one-enhanced

# 运行指定模块的示例
python examples/fundflow_example.py
python examples/disclosure_example.py
# ... 其他示例
```

### 批量运行所有示例

```bash
# Linux/macOS
for file in examples/*_example.py; do
    echo "Running $file..."
    python "$file"
    echo "---"
done

# Windows PowerShell
Get-ChildItem examples\*_example.py | ForEach-Object {
    Write-Host "Running $_..."
    python $_.FullName
    Write-Host "---"
}
```

### 注意事项

1. **网络连接**: 示例程序需要访问数据源（东方财富、官方网站），请确保网络连接正常。

2. **数据可用性**: 某些数据可能因为时间范围、股票代码等原因不可用，示例程序会捕获并显示友好的错误消息。

3. **运行时间**: 某些示例可能需要较长时间来获取数据，特别是宏观数据模块。

4. **数据更新频率**:
   - 实时数据：资金流、涨停池、龙虎榜等
   - T+1 数据：大宗交易、融资融券等
   - 月度/季度数据：宏观数据

## 错误处理

所有示例程序都包含完整的错误处理，展示如何处理以下异常：

### 1. InvalidParameterError - 参数错误

```python
try:
    df = get_stock_fund_flow("INVALID", "2024-01-01", "2024-01-31")
except InvalidParameterError as e:
    print(f"参数错误：{e}")
    print("提示：股票代码应为6位数字，如 '600000'")
```

### 2. NoDataError - 无数据

```python
try:
    df = get_stock_fund_flow("600000", "2000-01-01", "2000-01-02")
except NoDataError as e:
    print(f"无数据：{e}")
    print("提示：该时间段可能没有数据，请尝试其他日期")
```

### 3. DataSourceUnavailableError - 数据源不可用

```python
try:
    df = get_stock_fund_flow("600000", "2024-01-01", "2024-01-31")
except DataSourceUnavailableError as e:
    print(f"数据源不可用：{e}")
    print("提示：数据源可能暂时无法访问，请稍后重试")
```

### 4. UpstreamChangedError - 上游数据源变化

```python
try:
    df = get_stock_fund_flow("600000", "2024-01-01", "2024-01-31")
except UpstreamChangedError as e:
    print(f"上游数据源变化：{e}")
    print("提示：数据源格式可能已变化，请更新 akshare-one 版本")
```

### 5. 通用错误处理

```python
try:
    df = get_stock_fund_flow("600000", "2024-01-01", "2024-01-31")
except Exception as e:
    print(f"发生未知错误：{e}")
    print("提示：请检查网络连接或联系技术支持")
```

## 相关资源

### 文档

- **API 接口文档**: `docs/api/interfaces-reference.md` - 完整的接口参数文档
- **异常处理文档**: `docs/exceptions.md` - 异常类型和处理方法
- **API 扩展文档**: `docs/api/market-data-extension.md` - 市场数据扩展模块说明

### 验证工具

- **接口验证脚本**: `examples/validate_data_sources.py` - 验证所有接口的可用性
- **接口检查脚本**: `scripts/monitor_data_sources.py` - 批量检查接口状态

### 测试

- **单元测试**: `tests/test_{module}.py` - 各模块的单元测试
- **集成测试**: `tests/test_{module}_integration.py` - 集成测试
- **测试文档**: `tests/README.md` - 测试框架说明

## 示例、文档、验证脚本映射表

| 模块 | 示例文件 | API 文档章节 | 验证脚本配置 | 接口数量 |
|------|---------|-------------|-------------|---------|
| FundFlow | `fundflow_example.py` | `interfaces-reference.md#fundflow` | `VALIDATION_CONFIG['fundflow']` | 7 |
| Disclosure | `disclosure_example.py` | `interfaces-reference.md#disclosure` | `VALIDATION_CONFIG['disclosure']` | 4 |
| Northbound | `northbound_example.py` | `interfaces-reference.md#northbound` | `VALIDATION_CONFIG['northbound']` | 3 |
| Macro | `macro_example.py` | `interfaces-reference.md#macro` | `VALIDATION_CONFIG['macro']` | 6 |
| BlockDeal | `blockdeal_example.py` | `interfaces-reference.md#blockdeal` | `VALIDATION_CONFIG['blockdeal']` | 2 |
| LHB | `lhb_example.py` | `interfaces-reference.md#lhb` | `VALIDATION_CONFIG['lhb']` | 3 |
| LimitUp | `limitup_example.py` | `interfaces-reference.md#limitup` | `VALIDATION_CONFIG['limitup']` | 3 |
| Margin | `margin_example.py` | `interfaces-reference.md#margin` | `VALIDATION_CONFIG['margin']` | 2 |
| Pledge | `pledge_example.py` | `interfaces-reference.md#pledge` | `VALIDATION_CONFIG['pledge']` | 2 |
| Restricted | `restricted_example.py` | `interfaces-reference.md#restricted` | `VALIDATION_CONFIG['restricted']` | 2 |
| Goodwill | `goodwill_example.py` | `interfaces-reference.md#goodwill` | `VALIDATION_CONFIG['goodwill']` | 3 |
| ESG | `esg_example.py` | `interfaces-reference.md#esg` | `VALIDATION_CONFIG['esg']` | 2 |

**总计**: 12 个模块，37 个接口

## 贡献

如果您发现示例程序有问题或希望添加新的使用场景，欢迎提交 Issue 或 Pull Request。

## 许可证

MIT License - 详见项目根目录的 LICENSE 文件。
