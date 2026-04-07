# 入门教程

本教程将帮助你快速上手 akshare-one，从安装到实际使用。

## 安装

### 使用 pip 安装

```bash
pip install akshare-one
```

### 使用 uv 安装（推荐）

```bash
uv pip install akshare-one
```

## 快速开始

### 1. 获取股票历史数据

最简单的使用方式是获取股票的历史K线数据：

```python
from akshare_one import get_hist_data

# 获取浦发银行(600000)的日线数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(df.head())
```

输出示例：
```
timestamp    open    high     low   close    volume
2024-01-02   9.50   9.80    9.45   9.75   123456
2024-01-03   9.75   9.90    9.70   9.85   134567
...
```

### 2. 获取实时行情

获取股票的实时行情数据：

```python
from akshare_one import get_realtime_data

# 获取浦发银行的实时行情
df = get_realtime_data(symbol="600000")

print(df)
```

输出包含：
- `symbol`: 股票代码
- `price`: 最新价
- `change`: 涨跌额
- `pct_change`: 涨跌幅(%)
- `volume`: 成交量
- `amount`: 成交额

### 3. 获取股票基本信息

```python
from akshare_one import get_basic_info

# 获取股票基本信息
df = get_basic_info(symbol="600000")

print(df)
```

输出包含：
- 总市值、流通市值
- 总股本、流通股
- 行业分类
- 上市日期等

## 基本功能

### 时间间隔选择

支持多种时间间隔：

```python
# 日线
df = get_hist_data(symbol="600000", interval="day")

# 周线
df = get_hist_data(symbol="600000", interval="week")

# 月线
df = get_hist_data(symbol="600000", interval="month")

# 分钟线（5分钟）
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5
)

# 小时线
df = get_hist_data(
    symbol="600000",
    interval="hour",
    interval_multiplier=1
)
```

### 复权类型

支持三种复权方式：

```python
# 不复权
df = get_hist_data(symbol="600000", adjust="none")

# 前复权（向前调整价格）
df = get_hist_data(symbol="600000", adjust="qfq")

# 后复权（向后调整价格）
df = get_hist_data(symbol="600000", adjust="hfq")
```

**复权说明：**
- **不复权**：原始价格，可能有跳空
- **前复权**：保持当前价格不变，调整历史价格
- **后复权**：保持上市价格不变，调整后续价格

推荐使用前复权进行技术分析。

### 数据源选择

支持多个数据源：

```python
# 东方财富直连（推荐）
df = get_hist_data(symbol="600000", source="eastmoney_direct")

# 东方财富（标准接口）
df = get_hist_data(symbol="600000", source="eastmoney")

# 新浪财经
df = get_hist_data(symbol="600000", source="sina")
```

### 多数据源自动切换

使用多数据源功能，当一个数据源失败时自动切换：

```python
from akshare_one import get_hist_data_multi_source

# 自动切换数据源
df = get_hist_data_multi_source(
    symbol="600000",
    interval="day",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

## 数据过滤

使用 `apply_data_filter` 进行数据筛选：

```python
from akshare_one import get_realtime_data, apply_data_filter

# 获取全市场行情
df = get_realtime_data()

# 过滤：涨幅大于3%，成交量大于10万手
df_filtered = apply_data_filter(
    df,
    row_filter={
        'query': 'pct_change > 3 and volume > 100000',
        'sort_by': 'pct_change',
        'top_n': 20
    }
)
```

支持的过滤选项：
- `columns`: 选择特定列
- `query`: pandas query 表达式
- `sort_by`: 排序字段
- `ascending`: 升序/降序
- `top_n`: 取前N条
- `sample`: 随机采样比例

## 数据导出

将数据导出到文件：

```python
import pandas as pd

# 获取数据
df = get_hist_data(symbol="600000", interval="day")

# 导出为CSV
df.to_csv("600000_daily.csv", index=False)

# 导出为Excel
df.to_excel("600000_daily.xlsx", index=False)

# 导出为JSON
df.to_json("600000_daily.json", orient='records')
```

## 错误处理

正确处理可能的错误：

```python
from akshare_one import get_hist_data
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError
)

try:
    df = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
except InvalidParameterError as e:
    print(f"参数错误: {e}")
except NoDataError as e:
    print(f"无数据: {e}")
except DataSourceUnavailableError as e:
    print(f"数据源不可用: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 下一步

- 查看 [数据源选择教程](02_data_sources.md) 了解各数据源的特点
- 查看 [错误处理教程](03_error_handling.md) 学习如何正确处理异常
- 查看 [最佳实践教程](04_best_practices.md) 掌握高效使用技巧
- 查看 [基础示例](../../examples/basic/) 获取更多代码示例

## 常见问题

### 如何查看所有支持的功能？

```python
import akshare_one
print(dir(akshare_one))
```

### 如何查看某个函数的文档？

```python
from akshare_one import get_hist_data
help(get_hist_data)
```

### 数据缓存多久？

- 日线数据：缓存24小时
- 分钟/小时数据：缓存1小时
- 实时数据：不缓存

### 如何清空缓存？

缓存自动管理，无需手动清空。如需强制更新，可以重新调用函数。

### 支持哪些股票代码格式？

支持标准的6位股票代码，如：
- `600000`（上海主板）
- `000001`（深圳主板）
- `300059`（创业板）
- `688001`（科创板）

## 需要帮助？

- 查看 [FAQ](../FAQ.md)
- 查看 [API文档](../api/)
- 提交 Issue: https://github.com/akshare-one/akshare-one/issues