# TickFlow API 集成使用指南

本文档介绍如何在 akshare-one-enhanced 项目中使用 TickFlow API。

## 配置

### 1. 设置 API Key

TickFlow API 需要 API Key 进行认证。你可以通过以下两种方式配置：

**方式一：环境变量**
```bash
export TICKFLOW_API_KEY="tk_b1369c7ce7af4d12a17dbd52b3688c06"
```

**方式二：配置文件**
在项目根目录创建 `tickflow.cfg` 文件：
```
tk_b1369c7ce7af4d12a17dbd52b3688c06
```

或者使用 INI 格式：
```ini
[tickflow]
api_key = tk_b1369c7ce7af4d12a17dbd52b3688c06
```

## 使用示例

### 1. 实时行情

```python
from akshare_one.modules.realtime import get_current_data

# 查询单个股票实时行情
df = get_current_data(symbol="600000.SH", source="tickflow")
print(df)

# 查询多个股票实时行情（通过批量API）
from akshare_one.tickflow_client import get_tickflow_client
client = get_tickflow_client()
response = client.query_api("/v1/quotes", method="POST", 
                            data={"symbols": ["600000.SH", "000001.SZ"]})
import pandas as pd
df = pd.DataFrame(response.get("data", []))
print(df)

# 查询整个标的池的实时行情
df = get_current_data(source="tickflow")  # 默认使用 CN_Equity_A 标的池
print(df)
```

### 2. K线数据

```python
from akshare_one.modules.historical import get_hist_data

# 查询日线数据
df = get_hist_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-01-31",
    interval="day",
    adjust="qfq",  # 前复权
    source="tickflow"
)
print(df)

# 支持的时间周期
# minute, 5min, 10min, 15min, 30min, 60min, day, week, month, quarter, year

# 支持的复权类型
# none: 不复权
# qfq: 前复权
# hfq: 后复权
```

### 3. 标的元数据

```python
from akshare_one.modules.market import get_instruments

# 查询单个标的
df = get_instruments(symbols="600000.SH", source="tickflow")
print(df)

# 查询多个标的
df = get_instruments(symbols=["600000.SH", "000001.SZ"], source="tickflow")
print(df)
```

### 4. 交易所信息

```python
from akshare_one.modules.market import get_exchanges, get_exchange_instruments

# 获取所有交易所列表
df = get_exchanges(source="tickflow")
print(df)

# 获取某个交易所的标的列表
df = get_exchange_instruments(exchange="SH", type="stock", source="tickflow")
print(df)

# type 参数可选: stock, etf, index, bond, fund, futures, options, other
```

### 5. 标的池

```python
from akshare_one.modules.market import get_universes, get_universe_detail

# 获取所有标的池列表
df = get_universes(source="tickflow")
print(df)

# 获取标的池详情
df = get_universe_detail(universe_id="CN_Equity_A", source="tickflow")
print(df)
```

### 6. 财务数据（需要额外权限）

```python
from akshare_one.modules.financial import (
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_financial_metrics
)

# 查询资产负债表
df = get_balance_sheet(symbol="600000", source="tickflow")
print(df)

# 查询利润表
df = get_income_statement(symbol="600000", source="tickflow")
print(df)

# 查询现金流量表
df = get_cash_flow(symbol="600000", source="tickflow")
print(df)

# 查询核心财务指标
df = get_financial_metrics(symbol="600000", source="tickflow")
print(df)
```

## API 覆盖范围

TickFlow API 支持以下市场和数据类型：

### 市场覆盖
- **A股市场**: 上海证券交易所 (SH)、深圳证券交易所 (SZ)、北京证券交易所 (BJ)
- **港股市场**: 香港交易所 (HK)
- **美股市场**: 美国主要交易所 (US)
- **期货市场**: SHFE, DCE, CZCE, CFFEX, INE, GFEX

### 数据类型
- ✅ 实时行情（所有市场）
- ✅ K线数据（所有市场）
- ✅ 标的元数据
- ✅ 交易所信息
- ✅ 标的池管理
- ⚠️ 财务数据（需要额外权限）

### K线周期
- 日内周期: 1m, 5m, 10m, 15m, 30m, 60m, 4h
- 日线及以上: 1d, 1w, 1M, 1Q, 1Y

### 复权类型
- `none`: 不复权
- `forward` / `qfq`: 前复权
- `backward` / `hfq`: 后复权

## 注意事项

1. **权限限制**: 部分数据需要额外的 API 权限，如财务数据
2. **速率限制**: 根据 API Key 配置的权限，可能有请求频率限制
3. **批量查询**: POST 方法支持大批量查询，不受 URL 长度限制
4. **时间戳格式**: TickFlow API 使用毫秒级时间戳

## 错误处理

```python
from akshare_one.tickflow_client import get_tickflow_client

try:
    client = get_tickflow_client()
    response = client.query_api("/v1/quotes", method="POST", 
                                data={"symbols": ["600000.SH"]})
except RuntimeError as e:
    print(f"API 请求失败: {e}")
```

## 更多资源

- [TickFlow 官方文档](https://docs.tickflow.org)
- [API 参考](https://docs.tickflow.org/zh-hans/api-reference/introduction)
- [Python SDK 快速开始](https://docs.tickflow.org/zh-hans/sdk/python-quickstart)