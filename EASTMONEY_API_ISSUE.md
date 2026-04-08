# 东方财富 API 问题诊断与解决方案

## 问题诊断结果

### 1. 问题根源

通过测试和 GitHub Issue 调查，发现东方财富 API 存在以下问题：

**核心问题**：IP 被封禁，触发 `RemoteDisconnected` 错误
- 测试 URL: `https://push2his.eastmoney.com/api/qt/stock/kline/get`
- 错误信息: `('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
- 影响: 所有东方财富数据源（eastmoney, eastmoney_direct）均不可用

**原因分析**：
1. 东方财富对高频请求有严格的封控机制
2. 即使使用 AKShare 内部的 `ut` token (`7eea3edcaed734bea9cbfc24409ed989`) 也可能被封
3. 批量请求、自动化抓取更容易触发封禁
4. 这是 AKShare 的已知问题（Issue #7166）

### 2. GitHub Issue 参考

相关 Issue:
- [#7166](https://github.com/akfamily/akshare/issues/7166): AKShare东财接口报错RemoteDisconnected问题
- [#7171](https://github.com/akfamily/akshare/issues/7171): 分红配送-东财接口问题
- [#7178](https://github.com/akfamily/akshare/issues/7178): AKShare 接口问题报告

用户反馈:
> "近期akshare几乎用不了，提交上来的issue也是秒关，没有讨论，没有解决，直接关闭"

这表明这是一个长期存在的系统性问题。

### 3. 测试验证

```python
# 测试结果
- push2his.eastmoney.com: ✗ 连接被拒绝
- push2.eastmoney.com: ✗ 连接被拒绝（即使添加正确 headers）
- sina 数据源: ✓ 正常可用
- lixinger 数据源: ✓ 正常可用
```

## 解决方案

### 方案1：使用 akshare-proxy-patch（推荐，低频免费）

**优点**：
- 低频场景下可免费使用
- 自动注入请求头和代理
- 无需修改业务代码
- 支持自定义封控域名列表

**安装**：
```bash
pip install akshare-proxy-patch==0.2.13
```

**使用方法**：
```python
# 在 Python 文件顶部添加
import akshare_proxy_patch

# 获取 TOKEN: https://ak.cheapproxy.net/dashboard/akshare
akshare_proxy_patch.install_patch(
    "101.201.173.125",
    auth_token="你的TOKEN",  # 低频可免费获取
    retry=30,
    hook_domains=[
        "push2his.eastmoney.com",
        "push2.eastmoney.com",
        "emweb.securities.eastmoney.com",
    ],
)

# 后续正常使用 akshare-one
from akshare_one import get_hist_data
df = get_hist_data(symbol="600000", source="eastmoney")
```

**项目链接**：
- GitHub: https://github.com/HelloYie/akshare-proxy-patch
- TOKEN获取: https://ak.cheapproxy.net/dashboard/akshare

### 方案2：使用代理轮转（生产环境推荐）

**优点**：
- 健壮的代理池管理
- 多代理轮转 + 直连兜底
- 支持超时自动重试
- 适合高频批量抓取

**缺点**：
- 需要购买代理服务（极量IP、快代理等）

**使用方法**：
参考项目：https://github.com/VeKiner/akshare-stock-data-fetcher

```python
# 在 utils.py 中配置代理 API
proxy_ips = requests.get('你的代理API地址').text
# 返回格式: ip:port:user:password
```

### 方案3：切换到其他可用数据源（临时方案）

**当前可用数据源**：
- **sina**: ✓ 稳定可用，响应快
- **lixinger**: ✓ 稳定可用，响应最快
- **eastmoney**: ✗ 不可用（IP封禁）
- **eastmoney_direct**: ✗ 不可用（IP封禁）
- **tencent**: ✗ 无数据
- **netease**: ✗ 无数据

**使用建议**：
```python
from akshare_one import get_hist_data, get_hist_data_multi_source

# 方法1：指定可用数据源
df = get_hist_data(symbol="600000", source="sina")

# 方法2：多数据源自动切换（推荐）
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["sina", "lixinger", "eastmoney"]  # 自动跳过不可用的源
)
```

### 方案4：等待 IP 解封（不确定）

**适用场景**：
- 偶发性请求
- 非批量抓取
- 临时性需求

**说明**：
- IP 可能是临时封禁（几小时到一天）
- 等待后可能自动恢复
- 但不建议依赖此方案，封控机制可能长期生效

## 技术细节

### 东方财富 API 认证机制

从 AKShare 源码中发现：
```python
# AKShare stock_zh_a_hist 函数使用的 URL 和参数
url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
params = {
    "ut": "7eea3edcaed734bea9cbfc24409ed989",  # 认证 token
    "klt": "101",  # 日K线
    "fqt": "0",    # 不复权
    ...
}
```

即使使用官方 token，仍然会被封禁，说明东方财富有更严格的 IP 封控机制。

### 为什么 sina 和 lixinger 可用？

- **sina**: 使用新浪财经 API，封控相对宽松
- **lixinger**: 理杏仁 API，有官方认证机制
- **eastmoney**: 东方财富 API，封控最严格

## 建议措施

### 立即可行：
1. **切换到 sina 或 lixinger 数据源**
   - 快速解决当前问题
   - 使用多数据源自动切换作为兜底

2. **安装 akshare-proxy-patch**
   - 低频免费，高频付费
   - 自动处理封控问题

### 中长期：
1. **混合使用多种数据源**
   - sina/lixinger 作为主要源
   - eastmoney 作为备用源（配合代理）

2. **优化请求频率**
   - 添加请求延迟（sleep）
   - 使用缓存减少重复请求
   - 避免批量高频抓取

3. **监控数据源状态**
   - 定期测试各数据源可用性
   - 自动切换到可用数据源

## 代码修复建议

### 修改 akshare-one 配置

建议在 `HistoricalDataFactory` 中调整默认数据源优先级：

```python
# 当前默认优先级
sources=["eastmoney_direct", "eastmoney", "sina", "tencent", "netease"]

# 建议修改为（考虑可用性）
sources=["sina", "lixinger", "eastmoney_direct", "eastmoney", "tencent", "netease"]
```

### 添加智能切换机制

```python
def get_hist_data_smart(symbol, **kwargs):
    """智能选择可用数据源"""
    available_sources = ["sina", "lixinger"]  # 已验证可用
    fallback_sources = ["eastmoney", "eastmoney_direct"]  # 可能被封
    
    # 优先使用可用数据源
    for source in available_sources:
        try:
            df = get_hist_data(symbol, source=source, **kwargs)
            if df and len(df) > 0:
                return df, source
        except:
            continue
    
    # 如果可用源失败，尝试备用源
    return get_hist_data_multi_source(
        symbol, 
        sources=available_sources + fallback_sources,
        **kwargs
    )
```

## 相关资源

- [akshare-proxy-patch](https://github.com/HelloYie/akshare-proxy-patch) - 自动代理注入插件
- [akshare-stock-data-fetcher](https://github.com/VeKiner/akshare-stock-data-fetcher) - 代理轮转方案
- [AKShare Issue #7166](https://github.com/akfamily/akshare/issues/7166) - 问题讨论
- [AKShare 官方文档](https://github.com/akfamily/akshare)

## 总结

**问题本质**：东方财富 API 的严格 IP 封控机制，导致直接请求被封禁。

**最佳实践**：
1. 短期：使用 sina/lixinger 数据源 + 多源自动切换
2. 中期：安装 akshare-proxy-patch（低频免费）
3. 长期：购买代理服务，配置代理轮转机制

**不建议**：
- 继续直接请求 eastmoney API（会被封）
- 依赖等待 IP 自动解封（时间不确定）
- 批量高频抓取（加速封禁）

---

**报告时间**: 2026-04-08
**测试环境**: macOS, Python 3.12, AKShare 1.18.51
**测试结果**: sina ✓, lixinger ✓, eastmoney ✗, eastmoney_direct ✗