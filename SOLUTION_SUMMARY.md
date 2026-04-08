# 东方财富 API 问题解决总结

## 问题诊断结果

**核心问题**: eastmoney 和 eastmoney_direct 数据源不可用
- **原因**: IP 被东方财富 API 封禁，触发 RemoteDisconnected 错误
- **验证**: GitHub Issue #7166 显示这是 AKShare 的已知问题
- **影响**: 所有东方财富 API 接口均被封控

## 可用数据源（已验证）

✓ **sina** - 稳定可用，响应快（0.19s）
✓ **lixinger** - 稳定可用，响应快
✗ **eastmoney** - IP 封禁，连接被拒绝
✗ **eastmoney_direct** - IP 封禁，连接被拒绝
✗ **tencent** - 无数据返回
✗ **netease** - 无数据返回

## 解决方案（立即可用）

### 方案1: 切换数据源（推荐，无需额外配置）

```python
from akshare_one import get_hist_data

# 使用 sina 数据源（已验证可用）
df = get_hist_data(symbol="600000", source="sina")

# 或使用 lixinger 数据源
df = get_hist_data(symbol="600000", source="lixinger")
```

**优点**: 
- 简单直接，无需额外配置
- sina 和 lixinger 已验证可用
- 响应速度快

**测试结果**: ✓ 成功获取 22 条数据，响应时间 0.19s

### 方案2: 多数据源自动切换（推荐，自动容错）

```python
from akshare_one import get_hist_data_multi_source

# 自动优先使用可用数据源
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["sina", "lixinger", "eastmoney_direct", "eastmoney"]
)

# 实际使用的数据源
actual_source = df.attrs.get("source")
print(f"使用数据源: {actual_source}")  # 输出: sina
```

**优点**:
- 自动跳过不可用数据源
- 自动切换到可用数据源
- 提供容错机制

**测试结果**: ✓ 成功获取 22 条数据，自动使用 sina 数据源

### 方案3: 使用 akshare-proxy-patch（付费，适合高频）

**安装**:
```bash
pip install akshare-proxy-patch==0.2.13
```

**使用**:
```python
import akshare_proxy_patch

# 获取 TOKEN: https://ak.cheapproxy.net/dashboard/akshare
akshare_proxy_patch.install_patch(
    "101.201.173.125",
    auth_token="你的TOKEN",
    retry=30,
    hook_domains=[
        "push2his.eastmoney.com",
        "push2.eastmoney.com",
    ],
)

# 后续正常使用
from akshare_one import get_hist_data
df = get_hist_data(symbol="600000", source="eastmoney")
```

**优点**:
- 低频免费，高频付费
- 自动注入代理
- 无需修改业务代码

**相关资源**:
- GitHub: https://github.com/HelloYie/akshare-proxy-patch
- TOKEN: https://ak.cheapproxy.net/dashboard/akshare

## 建议

### 立即可行:
1. ✓ 使用 sina 或 lixinger 数据源
2. ✓ 使用多数据源自动切换机制

### 中长期:
1. 安装 akshare-proxy-patch（低频免费）
2. 混合使用多种数据源
3. 监控数据源可用性状态

## 相关文档

- [详细诊断报告](EASTMONEY_API_ISSUE.md)
- [测试脚本](test_eastmoney_solution.py)

---

**测试时间**: 2026-04-08
**测试环境**: macOS, Python 3.12, AKShare 1.18.51
**验证结果**: ✓ sina 和 lixinger 数据源可用
