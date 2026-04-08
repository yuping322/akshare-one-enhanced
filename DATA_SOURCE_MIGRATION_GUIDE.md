# 数据源迁移指南

## 变更说明

由于东方财富 API (`eastmoney` 和 `eastmoney_direct`) 存在 IP 封禁问题（详见 `EASTMONEY_API_ISSUE.md`），我们已将所有默认数据源切换到 **sina** 和 **lixinger**。

## 默认数据源变更（2026-04-08）

### 历史数据 API

**之前**：
```python
get_hist_data(symbol="600000")  # 默认使用 eastmoney_direct
```

**现在**：
```python
get_hist_data(symbol="600000")  # 默认使用 sina（已验证可用）
```

**多数据源优先级变更**：
- 之前: `["eastmoney_direct", "eastmoney", "sina", ...]`
- 现在: `["sina", "lixinger", "eastmoney_direct", "eastmoney", ...]`

### 实时数据 API

**重要提示**：实时数据模块目前不支持 sina 数据源

**推荐方式**：
```python
# 使用多数据源自动切换
df = get_realtime_data_multi_source("600000")
# 自动尝试: sina → eastmoney_direct → eastmoney → xueqiu
```

**单数据源方式**（可能失败）：
```python
# 显式指定数据源
df = get_realtime_data("600000", source="eastmoney")  # 可能被封
```

### 财务数据 API

**之前**：
```python
get_financial_metrics(symbol="600000")  # 默认使用 eastmoney_direct
```

**现在**：
```python
get_financial_metrics(symbol="600000")  # 默认使用 sina（已验证可用）
```

### 新闻数据 API

**之前**：
```python
get_news_data(symbol="300059")  # 默认使用 eastmoney
```

**现在**：
```python
get_news_data(symbol="300059")  # 默认使用 eastmoney
# 如需切换：source="sina"
```

## 已验证可用的数据源

| 数据源 | 历史数据 | 实时数据 | 财务数据 | 状态 |
|--------|---------|---------|---------|------|
| **sina** | ✓ | ✗ | ✓ | **推荐** - 稳定可用 |
| **lixinger** | ✓ | ✗ | ✓ | **推荐** - 稳定可用 |
| eastmoney | ✗ | ✓ | ✗ | IP 封禁 |
| eastmoney_direct | ✗ | ✓ | ✗ | IP 封禁 |
| xueqiu | ✗ | ✓ | ✗ | 需验证 |

## 迁移建议

### 1. 历史数据（推荐）

```python
from akshare_one import get_hist_data, get_hist_data_multi_source

# 方法1: 使用默认值（sina）
df = get_hist_data("600000")

# 方法2: 显式指定数据源
df = get_hist_data("600000", source="sina")  # 推荐
df = get_hist_data("600000", source="lixinger")  # 推荐

# 方法3: 多数据源自动切换（最佳实践）
df = get_hist_data_multi_source("600000")
# 自动尝试: sina → lixinger → eastmoney → ...
```

### 2. 实时数据

```python
from akshare_one import get_realtime_data_multi_source

# 推荐使用多数据源 API
df = get_realtime_data_multi_source("600000")
# 自动尝试多个数据源，提升成功率
```

### 3. 财务数据

```python
from akshare_one import get_balance_sheet, get_income_statement, get_cash_flow

# 默认使用 sina（已验证可用）
df = get_balance_sheet("600000")
df = get_income_statement("600000")
df = get_cash_flow("600000")
```

## 性能对比

基于测试结果（2026-04-08）：

| 数据源 | 历史数据响应时间 | 稳定性 |
|--------|----------------|--------|
| sina | 0.19s | ✓ 稳定 |
| lixinger | 0.13s | ✓ 稳定 |
| eastmoney | - | ✗ 不可用 |

## 常见问题

### Q1: 为什么实时数据不支持 sina？

A: 新浪财经 API 目前不提供实时行情接口，仅支持历史数据和财务数据。实时数据建议使用多数据源自动切换。

### Q2: 如何使用 eastmoney 数据源？

A: eastmoney 数据源目前被 IP 封禁，建议：
1. 使用 sina/lixinger 数据源
2. 使用多数据源自动切换
3. 安装 `akshare-proxy-patch` 插件（详见 `EASTMONEY_API_ISSUE.md`）

### Q3: 旧代码需要修改吗？

A: 大部分代码无需修改：
- 使用默认值的代码会自动切换到 sina
- 显式指定 `source="eastmoney"` 的代码建议修改为 `source="sina"`
- 使用多数据源 API 的代码无需修改

### Q4: 多数据源 API 的优势？

A: 
- 自动故障转移，提升稳定性
- 按优先级自动选择最快的数据源
- 适合生产环境

## 总结

**立即可行的方案**：
1. ✓ 历史数据默认使用 sina（无需修改代码）
2. ✓ 财务数据默认使用 sina（无需修改代码）
3. ⚠ 实时数据使用多数据源 API（推荐）

**建议**：
- 优先使用多数据源 API (`*_multi_source`)
- 显式指定数据源时，优先选择 `sina` 或 `lixinger`
- 避免 `eastmoney` 和 `eastmoney_direct`（当前不可用）

---

**更新时间**: 2026-04-08  
**测试环境**: macOS, Python 3.12, AKShare 1.18.51  
**验证结果**: sina ✓, lixinger ✓, eastmoney ✗