# 常见问题解答 (FAQ)

本FAQ收集了使用 akshare-one 过程中最常见的问题和解决方案。

## 安装问题

### Q1: 如何安装 akshare-one？

**A:** 有两种推荐方式：

```bash
# 方式1：使用 pip
pip install akshare-one

# 方式2：使用 uv（推荐，更快）
uv pip install akshare-one
```

### Q2: 安装时提示依赖错误怎么办？

**A:** akshare-one 主要依赖 pandas 和 requests。如果安装失败：

```bash
# 先安装依赖
pip install pandas requests

# 再安装 akshare-one
pip install akshare-one
```

### Q3: 如何升级到最新版本？

**A:**

```bash
pip install --upgrade akshare-one
```

或查看当前版本：

```python
import akshare_one
print(akshare_one.__version__)
```

## 数据获取问题

### Q4: 如何获取股票历史数据？

**A:** 使用 `get_hist_data` 函数：

```python
from akshare_one import get_hist_data

df = get_hist_data(
    symbol="600000",
    interval="day",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### Q5: 股票代码格式要求是什么？

**A:** 股票代码必须是6位数字：
- 上海主板：600xxx, 601xxx, 603xxx
- 深圳主板：000xxx, 001xxx
- 创业板：300xxx
- 科创板：688xxx

不支持带前缀的格式（如 sh600000, sz000001）。

### Q6: 如何获取分钟级数据？

**A:** 设置 `interval="minute"` 并指定倍数：

```python
# 5分钟K线
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5
)

# 15分钟K线
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=15
)
```

### Q7: 支持哪些时间间隔？

**A:** 支持6种时间间隔：
- `minute`: 分钟线（需指定倍数）
- `hour`: 小时线（需指定倍数）
- `day`: 日线
- `week`: 周线
- `month`: 月线
- `year`: 年线

### Q8: 如何获取实时行情？

**A:** 使用 `get_realtime_data` 函数：

```python
from akshare_one import get_realtime_data

# 获取单个股票实时行情
df = get_realtime_data(symbol="600000")

# 获取全市场实时行情
df = get_realtime_data()  # 不指定symbol
```

### Q9: 数据返回为空怎么办？

**A:** 可能的原因和解决方案：

1. **股票不存在或已退市**
   - 检查股票代码是否正确
   - 尝试其他已知存在的股票

2. **时间范围内无数据**
   - 扩大时间范围
   - 检查日期是否在交易日范围内

3. **数据源问题**
   - 使用多数据源：`get_hist_data_multi_source`
   - 切换数据源：`source="sina"`

```python
# 使用多数据源提高成功率
from akshare_one import get_hist_data_multi_source

df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

### Q10: 如何获取ETF数据？

**A:** ETF使用与股票相同的接口：

```python
# 获取沪深300ETF历史数据
df = get_hist_data(
    symbol="510300",  # ETF代码
    interval="day"
)

# 获取ETF实时行情
df = get_realtime_data(symbol="510300")
```

常见ETF代码：
- 510300: 沪深300ETF
- 510500: 中证500ETF
- 159915: 创业板ETF

### Q11: 如何获取指数数据？

**A:** 指数数据暂不支持，建议使用ETF代替：
- 沪深300指数 → 510300ETF
- 中证500指数 → 510500ETF
- 创业板指数 → 159915ETF

### Q12: 如何获取财务数据？

**A:** 使用财务数据相关函数：

```python
from akshare_one import (
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_financial_metrics
)

# 获取资产负债表
df = get_balance_sheet(symbol="600000")

# 获取利润表
df = get_income_statement(symbol="600000")

# 获取现金流量表
df = get_cash_flow(symbol="600000")

# 获取财务指标摘要
df = get_financial_metrics(symbol="600000")
```

## 数据源问题

### Q13: 支持哪些数据源？

**A:** 支持4个数据源：
1. `eastmoney_direct` - 东方财富直连（推荐）
2. `eastmoney` - 东方财富标准接口
3. `sina` - 新浪财经
4. `xueqiu` - 雪球

### Q14: 哪个数据源最好？

**A:** 推荐使用优先级：
1. **eastmoney_direct**: 快速、稳定、数据完整（首选）
2. **eastmoney**: 数据全面（备用）
3. **sina**: 响应快、覆盖广（备用）
4. **xueqiu**: 实时性好（实时行情备用）

最佳实践：使用多数据源自动切换

```python
from akshare_one import get_hist_data_multi_source

df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

### Q15: 数据源不可用怎么办？

**A:** 解决方案：

1. **使用多数据源**
   ```python
   df = get_hist_data_multi_source(symbol="600000")
   ```

2. **切换数据源**
   ```python
   df = get_hist_data(symbol="600000", source="sina")
   ```

3. **检查网络连接**
   - 确认网络可用
   - 检查防火墙设置

4. **稍后重试**
   ```python
   import time
   time.sleep(5)  # 等待5秒后重试
   df = get_hist_data(symbol="600000")
   ```

### Q16: 如何提高数据获取成功率？

**A:** 建议措施：

1. **使用多数据源**
   ```python
   df = get_hist_data_multi_source(
       symbol="600000",
       sources=["eastmoney_direct", "eastmoney", "sina"]
   )
   ```

2. **添加重试机制**
   ```python
   max_retries = 3
   for i in range(max_retries):
       try:
           df = get_hist_data_multi_source(symbol="600000")
           break
       except:
           time.sleep(2)
   ```

3. **使用错误处理**
   ```python
   try:
       df = get_hist_data_multi_source(symbol="600000")
   except DataSourceUnavailableError:
       print("数据源不可用，稍后重试")
   ```

## 数据处理问题

### Q17: 什么是复权？如何选择？

**A:** 复权是调整历史价格以消除分红、配股等影响。

三种复权方式：
- **不复权** (`adjust="none"`): 原始价格，可能有跳空
- **前复权** (`adjust="qfq"`): 保持当前价格不变，调整历史价格
- **后复权** (`adjust="hfq"`): 保持上市价格不变，调整后续价格

**推荐使用场景：**
- 技术分析：使用前复权
- 基本面分析：可使用不复权
- 长期趋势分析：使用前复权或后复权

```python
# 技术分析推荐使用前复权
df = get_hist_data(
    symbol="600000",
    adjust="qfq"
)
```

### Q18: 如何过滤和筛选数据？

**A:** 使用 `apply_data_filter` 函数：

```python
from akshare_one import get_realtime_data, apply_data_filter

# 获取全市场数据
df = get_realtime_data()

# 过滤涨幅大于3%且成交量大于10万手的股票
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
- `query`: pandas query表达式
- `sort_by`: 排序字段
- `ascending`: 升序/降序
- `top_n`: 取前N条
- `sample`: 随机采样比例

### Q19: 如何导出数据到文件？

**A:** 使用 pandas 的导出功能：

```python
from akshare_one import get_hist_data

# 获取数据
df = get_hist_data(symbol="600000")

# 导出为CSV
df.to_csv("600000.csv", index=False, encoding='utf-8-sig')

# 导出为Excel（需要openpyxl）
df.to_excel("600000.xlsx", index=False)

# 导出为JSON
df.to_json("600000.json", orient='records', indent=2)
```

### Q20: 数据包含哪些字段？

**A:** 常用字段：

**历史数据：**
- `timestamp`: 时间戳
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

**实时数据：**
- `symbol`: 股票代码
- `price`: 最新价
- `change`: 涨跌额
- `pct_change`: 涨跌幅(%)
- `volume`: 成交量
- `amount`: 成交额
- `open`: 今开
- `high`: 最高
- `low`: 最低
- `prev_close`: 昨收

查看完整字段：
```python
df = get_hist_data(symbol="600000")
print(df.columns.tolist())
```

### Q21: 如何批量获取多个股票数据？

**A:** 推荐使用批量获取方式：

```python
from akshare_one import get_realtime_data

# 方式1：一次获取全市场，再筛选（推荐）
stocks = ["600000", "000001", "600519"]
df_all = get_realtime_data()  # 不指定symbol，获取全市场
df_filtered = df_all[df_all['symbol'].isin(stocks)]

# 方式2：循环获取（不推荐，较慢）
for symbol in stocks:
    df = get_realtime_data(symbol)
    # 处理数据
```

### Q22: 如何计算技术指标？

**A:** 使用 pandas 计算常见指标：

```python
from akshare_one import get_hist_data

df = get_hist_data(symbol="600000", adjust="qfq")

# 涨跌幅
df['pct_change'] = df['close'].pct_change() * 100

# 均线
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma10'] = df['close'].rolling(window=10).mean()
df['ma20'] = df['close'].rolling(window=20).mean()

# MACD
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = ema12 - ema26
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))
```

## 性能问题

### Q23: 数据获取很慢怎么办？

**A:** 优化方法：

1. **使用批量获取**
   ```python
   # 获取全市场数据（一次请求）
   df_all = get_realtime_data()
   ```

2. **合理利用缓存**
   ```python
   # 相同参数的请求会使用缓存
   df1 = get_hist_data(symbol="600000")
   df2 = get_hist_data(symbol="600000")  # 使用缓存，更快
   ```

3. **缩小时间范围**
   ```python
   # 只获取需要的数据
   df = get_hist_data(
       symbol="600000",
       start_date="2024-12-01",  # 一个月
       end_date="2024-12-31"
   )
   ```

4. **选择合适的时间间隔**
   ```python
   # 长期分析使用日线或周线
   df = get_hist_data(symbol="600000", interval="day")
   ```

### Q24: 缓存多久？如何清空缓存？

**A:** 缓存时长：
- 日线及以上：缓存24小时
- 分钟/小时数据：缓存1小时
- 实时数据：不缓存

缓存自动管理，无需手动清空。如需强制更新：
```python
# 重新调用函数即可（缓存过期后自动更新）
df = get_hist_data(symbol="600000")
```

### Q25: 如何避免请求过快被限流？

**A:** 建议：

1. **批量获取代替循环获取**
   ```python
   # 推荐：一次获取
   df_all = get_realtime_data()

   # 不推荐：循环获取
   for symbol in stocks:
       df = get_realtime_data(symbol)
   ```

2. **添加间隔**
   ```python
   import time

   for symbol in stocks:
       df = get_hist_data(symbol)
       time.sleep(0.1)  # 100毫秒间隔
   ```

3. **使用多数据源**
   ```python
   # 自动切换，分散请求压力
   df = get_hist_data_multi_source(symbol="600000")
   ```

## 错误处理问题

### Q26: 遇到错误如何处理？

**A:** 使用异常处理：

```python
from akshare_one import get_hist_data
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError
)

try:
    df = get_hist_data(symbol="600000")

except InvalidParameterError as e:
    print(f"参数错误: {e}")

except NoDataError as e:
    print(f"无数据: {e}")

except DataSourceUnavailableError as e:
    print(f"数据源不可用: {e}")
```

### Q27: 如何查看详细错误信息？

**A:** 使用详细日志：

```python
import logging
import traceback

# 开启详细日志
logging.basicConfig(level=logging.DEBUG)

try:
    df = get_hist_data(symbol="600000")
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()  # 打印详细堆栈
```

### Q28: 如何测试数据源是否可用？

**A:** 测试方法：

```python
from akshare_one import get_realtime_data

def test_source(source):
    """测试数据源可用性"""
    try:
        df = get_realtime_data(symbol="600000", source=source)
        print(f"✓ {source} 可用")
        return True
    except:
        print(f"✗ {source} 不可用")
        return False

# 测试所有数据源
sources = ["eastmoney_direct", "eastmoney", "sina", "xueqiu"]
for source in sources:
    test_source(source)
```

## 使用场景问题

### Q29: 如何构建简单的预警系统？

**A:** 参考 [预警系统示例](../examples/advanced/alert_system.py)：

```python
from akshare_one import get_realtime_data

def check_alert(symbol, target_price):
    """检查价格预警"""
    df = get_realtime_data(symbol=symbol)
    current_price = df.iloc[0]['price']

    if current_price >= target_price:
        print(f"预警：{symbol} 价格 {current_price:.2f} 已达到目标 {target_price}")

# 使用
check_alert("600000", 10.0)
```

### Q30: 如何进行简单的策略回测？

**A:** 参考 [回测策略示例](../examples/advanced/backtesting_strategy.py)：

```python
from akshare_one import get_hist_data

# 获取数据
df = get_hist_data(symbol="600000", adjust="qfq")

# 计算均线
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma20'] = df['close'].rolling(window=20).mean()

# 生成信号
df['signal'] = 0
df.loc[df['ma5'] > df['ma20'], 'signal'] = 1  # 买入
df.loc[df['ma5'] < df['ma20'], 'signal'] = -1  # 卖出

# 计算收益
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['signal'].shift(1) * df['returns']
total_return = df['strategy_returns'].sum()

print(f"策略总收益: {total_return:.2%}")
```

### Q31: 如何分析投资组合？

**A:** 参考 [组合分析示例](../examples/advanced/portfolio_analysis.py)：

```python
from akshare_one import get_hist_data
import pandas as pd

stocks = ["600000", "000001", "600519"]
weights = [0.3, 0.3, 0.4]

# 获取数据
portfolio_data = {}
for symbol in stocks:
    df = get_hist_data(symbol=symbol, adjust="qfq")
    df['pct_change'] = df['close'].pct_change()
    portfolio_data[symbol] = df

# 计算组合收益（简化示例）
# 详细实现请参考示例文件
```

### Q32: 如何构建数据管道？

**A:** 参考 [数据管道示例](../examples/advanced/data_pipeline.py)：

```python
import os
from akshare_one import get_hist_data

def data_pipeline(stocks, start_date, end_date, output_dir):
    """数据管道"""

    os.makedirs(output_dir, exist_ok=True)

    for symbol in stocks:
        # 获取数据
        df = get_hist_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

        # 处理数据
        df['pct_change'] = df['close'].pct_change() * 100
        df['ma5'] = df['close'].rolling(window=5).mean()

        # 保存数据
        filename = os.path.join(output_dir, f"{symbol}.csv")
        df.to_csv(filename, index=False)
        print(f"已保存: {filename}")

# 使用
data_pipeline(
    stocks=["600000", "000001"],
    start_date="2024-01-01",
    end_date="2024-12-31",
    output_dir="data"
)
```

## 其他问题

### Q33: 是否支持港股、美股？

**A:** 目前主要支持A股市场。港股、美股暂不支持。

### Q34: 是否支持期货、期权数据？

**A:** 支持：

**期货数据：**
```python
from akshare_one import get_futures_hist_data, get_futures_realtime_data

# 期货历史数据
df = get_futures_hist_data(symbol="AG0")  # 白银

# 期货实时数据
df = get_futures_realtime_data(symbol="CF")  # 棉花
```

**期权数据：**
```python
from akshare_one import get_options_chain, get_options_realtime

# 期权链数据
df = get_options_chain(underlying_symbol="510300")

# 期权实时数据
df = get_options_realtime(underlying_symbol="510300")
```

### Q35: 是否支持加密货币？

**A:** 不支持加密货币数据。

### Q36: 如何获取帮助？

**A:** 多种方式：

1. **查看文档**
   - [入门教程](tutorials/01_getting_started.md)
   - [API文档](api/)
   - [示例代码](../examples/)

2. **查看函数帮助**
   ```python
   from akshare_one import get_hist_data
   help(get_hist_data)
   ```

3. **提交Issue**
   - GitHub: https://github.com/akshare-one/akshare-one/issues

### Q37: 如何贡献代码或报告Bug？

**A:**

1. **报告Bug**
   - 提交Issue，描述问题和复现步骤
   - 提供相关日志和错误信息

2. **贡献代码**
   - Fork项目
   - 提交Pull Request
   - 遵循项目代码规范

详见：[贡献指南](../CONTRIBUTING.md)

### Q38: 是否有使用限制？

**A:**

1. **免费使用**
   - 所有功能免费
   - 无需注册或认证

2. **请求频率**
   - 建议合理控制请求频率
   - 避免过快请求导致被限流

3. **数据版权**
   - 数据来自公开数据源
   - 请遵守数据源的使用条款

### Q39: 数据准确性如何？

**A:**

1. **数据来源**
   - 所有数据来自公开数据源（东方财富、新浪、雪球等）
   - 数据质量与数据源一致

2. **数据验证**
   - 建议在使用前验证数据
   - 对比多个数据源确保准确性

```python
# 对比不同数据源的数据
from akshare_one import get_hist_data

sources = ["eastmoney_direct", "sina"]
for source in sources:
    df = get_hist_data(symbol="600000", source=source)
    print(f"{source}: 最新价格 {df.iloc[-1]['close']:.2f}")
```

### Q40: 如何保持数据更新？

**A:** 建议：

1. **定期更新**
   ```python
   # 每日更新（缓存24小时后自动更新）
   df = get_hist_data(symbol="600000")
   ```

2. **实时监控**
   ```python
   # 实时数据不缓存，每次都是最新
   df = get_realtime_data(symbol="600000")
   ```

3. **增量更新**
   ```python
   # 定期获取最新数据
   import datetime

   end_date = datetime.now().strftime('%Y-%m-%d')
   start_date = (datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

   df_new = get_hist_data(
       symbol="600000",
       start_date=start_date,
       end_date=end_date
   )
   ```

## 总结

以上是 akshare-one 常见问题解答。如有其他问题：

1. 查看 [文档目录](index.md)
2. 查看 [示例代码](../examples/)
3. 提交 GitHub Issue

持续更新中...