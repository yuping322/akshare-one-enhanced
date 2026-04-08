# 默认数据源变更日志

## 2026-04-08 - 默认数据源切换到 sina/lixinger

### 变更原因

东方财富 API (`eastmoney` 和 `eastmoney_direct`) 因 IP 封禁导致不可用。详细分析见 `EASTMONEY_API_ISSUE.md`。

### 影响范围

#### 1. 单数据源函数默认值变更

| 函数 | 之前默认值 | 新默认值 | 状态 |
|------|-----------|---------|------|
| `get_hist_data()` | `eastmoney_direct` | `sina` | ✓ 已验证 |
| `get_realtime_data()` | `eastmoney_direct` | `eastmoney` | ⚠ 可能失败 |
| `get_basic_info()` | `eastmoney` | `sina` | ✓ 已验证 |
| `get_news_data()` | `eastmoney` | `eastmoney` | ✓ 无变化 |
| `get_financial_metrics()` | `eastmoney_direct` | `sina` | ✓ 已验证 |

#### 2. 多数据源函数优先级变更

| 函数 | 之前优先级 | 新优先级 |
|------|-----------|---------|
| `get_hist_data_multi_source()` | `["eastmoney_direct", "eastmoney", "sina", ...]` | `["sina", "lixinger", "eastmoney_direct", "eastmoney", ...]` |
| `get_realtime_data_multi_source()` | `["eastmoney_direct", "eastmoney", "xueqiu"]` | `["sina", "eastmoney_direct", "eastmoney", "xueqiu"]` |
| `get_basic_info_multi_source()` | `["eastmoney", "sina"]` | `["sina", "eastmoney"]` |
| `get_financial_data_multi_source()` | `["eastmoney_direct", "sina"]` | `["sina", "eastmoney_direct", "lixinger"]` |

### 向后兼容性

- ✓ 使用默认值的代码：自动切换到新数据源
- ⚠ 显式指定 `source="eastmoney"` 的代码：建议修改
- ✓ 使用多数据源 API 的代码：自动调整优先级

### 测试结果

```
历史数据 (get_hist_data):
  ✓ sina 数据源 - 0.19s - 22 行数据
  ✓ lixinger 数据源 - 0.13s - 22 行数据
  ✗ eastmoney 数据源 - IP 封禁

实时数据 (get_realtime_data):
  ✗ eastmoney 数据源 - IP 封禁
  建议：使用 get_realtime_data_multi_source()

财务数据 (get_financial_metrics):
  ✓ sina 数据源 - 正常可用
```

### 推荐使用方式

```python
# 历史数据 - 默认使用 sina
from akshare_one import get_hist_data
df = get_hist_data("600000")  # 自动使用 sina

# 实时数据 - 使用多数据源
from akshare_one import get_realtime_data_multi_source
df = get_realtime_data_multi_source("600000")  # 自动切换

# 财务数据 - 默认使用 sina
from akshare_one import get_balance_sheet
df = get_balance_sheet("600000")  # 自动使用 sina
```

### 文件变更清单

1. `src/akshare_one/modules/multi_source.py`
   - 修改所有默认数据源优先级列表
   - 8 处修改

2. `src/akshare_one/__init__.py`
   - 修改单数据源函数默认参数
   - 修改多数据源函数文档说明
   - 10+ 处修改

### 相关文档

- `EASTMONEY_API_ISSUE.md` - 东方财富 API 问题诊断
- `SOLUTION_SUMMARY.md` - 解决方案总结
- `DATA_SOURCE_MIGRATION_GUIDE.md` - 数据源迁移指南

### 回滚方案

如需回滚到旧版本，可以显式指定数据源：

```python
# 显式指定 eastmoney（可能失败）
df = get_hist_data("600000", source="eastmoney_direct")

# 或使用多数据源，自定义优先级
df = get_hist_data_multi_source(
    "600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

---

**变更人**: AI Assistant  
**审核状态**: 已测试  
**生效日期**: 2026-04-08  
**版本**: v0.5.0+
