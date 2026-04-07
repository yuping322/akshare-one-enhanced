# 数据源选择教程

本教程详细介绍 akshare-one 支持的各种数据源，帮助你选择最适合的数据源。

## 数据源概览

akshare-one 支持以下数据源：

| 数据源 | 代码 | 特点 | 适用场景 |
|--------|------|------|----------|
| 东方财富直连 | `eastmoney_direct` | 快速、稳定、数据完整 | **推荐日常使用** |
| 东方财富 | `eastmoney` | 标准接口、数据全面 | 备用数据源 |
| 新浪财经 | `sina` | 响应快、覆盖广 | 备用数据源 |
| 雪球 | `xueqiu` | 实时性好 | 实时行情备用 |

## 东方财富直连（推荐）

### 特点
- **速度快**：直接解析网页数据，响应迅速
- **数据完整**：包含完整的OHLCV数据
- **稳定可靠**：长期运行稳定
- **复权支持**：支持前复权、后复权、不复权

### 使用示例

```python
from akshare_one import get_hist_data

# 获取日线数据（推荐方式）
df = get_hist_data(
    symbol="600000",
    interval="day",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjust="qfq",
    source="eastmoney_direct"
)
```

### 适用场景
- 日常数据获取
- 批量数据下载
- 历史数据分析
- 技术指标计算

### 数据字段
- `timestamp`: 时间戳
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

## 东方财富（标准接口）

### 特点
- **接口标准**：使用官方API接口
- **数据全面**：包含更多字段
- **更新及时**：数据更新快

### 使用示例

```python
df = get_hist_data(
    symbol="600000",
    source="eastmoney"
)
```

### 适用场景
- 当直连接口失败时的备用方案
- 需要更多数据字段时

## 新浪财经

### 特点
- **响应快**：接口响应速度快
- **覆盖广**：覆盖A股全市场
- **免费使用**：无需认证

### 使用示例

```python
df = get_hist_data(
    symbol="600000",
    source="sina"
)
```

### 适用场景
- 快速获取实时数据
- 作为备用数据源
- 简单的数据查询

## 雪球

### 特点
- **实时性好**：实时数据更新快
- **社区数据**：包含社区讨论数据

### 使用示例

```python
from akshare_one import get_realtime_data

df = get_realtime_data(
    symbol="600000",
    source="xueqiu"
)
```

### 适用场景
- 实时行情获取
- 内部交易数据

## 多数据源策略

### 自动切换

使用多数据源功能，当一个数据源失败时自动切换：

```python
from akshare_one import get_hist_data_multi_source

# 按优先级尝试多个数据源
df = get_hist_data_multi_source(
    symbol="600000",
    interval="day",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

**工作原理：**
1. 首先尝试 `eastmoney_direct`
2. 如果失败，自动切换到 `eastmoney`
3. 如果再失败，切换到 `sina`
4. 所有数据源都失败才返回错误

### 数据源优先级建议

#### 历史数据
```python
sources = ["eastmoney_direct", "eastmoney", "sina"]
```

#### 实时行情
```python
sources = ["eastmoney_direct", "eastmoney", "xueqiu"]
```

#### 财务数据
```python
sources = ["eastmoney_direct", "sina", "cninfo"]
```

## 数据源对比

### 响应速度测试

```python
import time
from akshare_one import get_hist_data

sources = ["eastmoney_direct", "eastmoney", "sina"]

for source in sources:
    start = time.time()
    df = get_hist_data(symbol="600000", source=source)
    elapsed = time.time() - start
    print(f"{source}: {elapsed:.2f}秒, {len(df)}条数据")
```

典型结果：
- `eastmoney_direct`: 0.5-1秒
- `eastmoney`: 1-2秒
- `sina`: 0.8-1.5秒

### 数据完整性对比

不同数据源的数据字段可能略有差异：

| 字段 | eastmoney_direct | eastmoney | sina |
|------|------------------|-----------|------|
| 时间戳 | ✓ | ✓ | ✓ |
| 开盘价 | ✓ | ✓ | ✓ |
| 最高价 | ✓ | ✓ | ✓ |
| 最低价 | ✓ | ✓ | ✓ |
| 收盘价 | ✓ | ✓ | ✓ |
| 成交量 | ✓ | ✓ | ✓ |
| 成交额 | ✓ | ✓ | - |
| 复权 | ✓ | ✓ | - |

## 选择建议

### 按使用场景选择

#### 1. 日线数据分析
**推荐：** `eastmoney_direct` + 前复权

```python
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="qfq",
    source="eastmoney_direct"
)
```

#### 2. 分钟级实时监控
**推荐：** `eastmoney_direct`

```python
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5,
    source="eastmoney_direct"
)
```

#### 3. 实时行情展示
**推荐：** 多数据源

```python
from akshare_one import get_realtime_data_multi_source

df = get_realtime_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "xueqiu"]
)
```

#### 4. 批量数据下载
**推荐：** 多数据源 + 缓存

```python
for symbol in stock_list:
    df = get_hist_data_multi_source(
        symbol=symbol,
        sources=["eastmoney_direct", "sina"]
    )
```

### 按数据类型选择

| 数据类型 | 推荐数据源 |
|----------|-----------|
| 日线数据 | eastmoney_direct |
| 分钟数据 | eastmoney_direct |
| 实时行情 | eastmoney_direct / 多源 |
| 财务数据 | eastmoney_direct / sina |
| 基本信息 | eastmoney |

## 性能优化

### 1. 合理使用缓存

数据会自动缓存，重复调用会使用缓存：

```python
# 第一次调用（从数据源获取）
df1 = get_hist_data(symbol="600000", source="eastmoney_direct")

# 第二次调用（使用缓存）
df2 = get_hist_data(symbol="600000", source="eastmoney_direct")
```

### 2. 批量获取优化

避免在循环中频繁调用：

```python
# 不推荐：每次调用都可能请求
for symbol in stocks:
    df = get_realtime_data(symbol)

# 推荐：一次获取全市场数据
df_all = get_realtime_data()  # 不指定symbol，获取全市场
df_filtered = df_all[df_all['symbol'].isin(stocks)]
```

### 3. 时间范围优化

合理设置时间范围，避免获取过多数据：

```python
# 不推荐：获取过多历史数据
df = get_hist_data(symbol="600000", start_date="2000-01-01")

# 推荐：根据需求设置合理范围
df = get_hist_data(symbol="600000", start_date="2024-01-01")
```

## 故障处理

### 单数据源故障

如果某个数据源不可用：

```python
# 方法1：切换到其他数据源
df = get_hist_data(symbol="600000", source="sina")

# 方法2：使用多数据源自动切换
df = get_hist_data_multi_source(symbol="600000")
```

### 所有数据源故障

检查网络连接和数据源状态：

```python
from akshare_one import get_hist_data

try:
    df = get_hist_data_multi_source(symbol="600000")
except DataSourceUnavailableError:
    print("所有数据源不可用，请检查网络连接")
```

## 下一步

- 查看 [错误处理教程](03_error_handling.md) 学习如何处理数据源异常
- 查看 [最佳实践教程](04_best_practices.md) 了解性能优化技巧
- 查看 [多数据源示例](../../examples/basic/04_multi_source_failover.py)