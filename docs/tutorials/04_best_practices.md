# 最佳实践教程

本教程分享使用 akshare-one 的最佳实践和优化技巧。

## 性能优化

### 1. 使用多数据源提高可靠性

**最佳实践：**

```python
from akshare_one import get_hist_data_multi_source

# 推荐方式：使用多数据源
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

**不推荐：**

```python
# 单数据源，可能失败
df = get_hist_data(symbol="600000", source="eastmoney_direct")
```

### 2. 合理利用缓存

数据会自动缓存，避免重复获取相同数据：

```python
# 第一次调用（从数据源获取）
df1 = get_hist_data(symbol="600000", start_date="2024-01-01")

# 相同参数的第二次调用（使用缓存）
df2 = get_hist_data(symbol="600000", start_date="2024-01-01")  # 更快
```

**注意：**
- 日线数据缓存24小时
- 分钟数据缓存1小时
- 实时数据不缓存

### 3. 批量获取优化

**推荐方式：一次获取全市场数据**

```python
from akshare_one import get_realtime_data

# 获取全市场实时行情（一次请求）
df_all = get_realtime_data()

# 从中筛选需要的股票
stocks = ["600000", "000001", "600519"]
df_filtered = df_all[df_all['symbol'].isin(stocks)]
```

**不推荐：循环获取**

```python
# 不推荐：每个股票单独请求
stocks = ["600000", "000001", "600519"]
for symbol in stocks:
    df = get_realtime_data(symbol)  # 多次请求，较慢
```

### 4. 合理的时间范围

根据需求设置合理的日期范围：

```python
# 推荐：根据实际需求设置范围
# 分析近期趋势
df = get_hist_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 不推荐：获取过多历史数据
df = get_hist_data(
    symbol="600000",
    start_date="2000-01-01",  # 24年数据，可能过多
    end_date="2024-12-31"
)
```

### 5. 使用正确的数据类型

选择合适的时间间隔：

```python
# 日线分析：使用日线数据
df = get_hist_data(symbol="600000", interval="day")

# 短线分析：使用分钟数据
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5  # 5分钟
)

# 长线分析：使用周线或月线
df = get_hist_data(symbol="600000", interval="week")
```

## 数据处理最佳实践

### 1. 使用前复权数据

技术分析推荐使用前复权数据：

```python
# 推荐：技术分析使用前复权
df = get_hist_data(
    symbol="600000",
    adjust="qfq",  # 前复权
    source="eastmoney_direct"
)

# 计算均线等技术指标
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma10'] = df['close'].rolling(window=10).mean()
```

### 2. 数据验证

获取数据后进行验证：

```python
def validate_and_process(df):
    """验证和处理数据"""

    # 1. 检查数据是否为空
    if df.empty:
        print("警告：数据为空")
        return None

    # 2. 检查必需字段
    required = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required):
        print("警告：缺少必需字段")
        return None

    # 3. 检查数据类型
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 4. 检查异常值
    # 价格不能为负
    if (df[['open', 'high', 'low', 'close']] < 0).any().any():
        print("警告：包含负价格")
        return None

    # 5. 检查逻辑关系
    # 最高价 >= 最低价
    if (df['high'] < df['low']).any():
        print("警告：最高价低于最低价")
        return None

    return df

# 使用示例
df = get_hist_data(symbol="600000")
df = validate_and_process(df)
```

### 3. 使用 apply_data_filter

高效的数据过滤：

```python
from akshare_one import get_realtime_data, apply_data_filter

# 获取全市场数据
df = get_realtime_data()

# 高效过滤
df_filtered = apply_data_filter(
    df,
    columns=['symbol', 'price', 'pct_change', 'volume'],
    row_filter={
        'query': 'pct_change > 3 and volume > 100000',
        'sort_by': 'pct_change',
        'top_n': 20
    }
)
```

### 4. 合理的数据存储

```python
import pandas as pd
import os

def save_data_efficiently(df, filename):
    """高效保存数据"""

    # 创建目录
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 根据文件大小选择格式
    if len(df) > 10000:
        # 大数据：使用CSV（更紧凑）
        df.to_csv(filename, index=False, compression='gzip')
    else:
        # 小数据：使用Excel（便于查看）
        df.to_excel(filename, index=False)
```

## 代码组织最佳实践

### 1. 模块化设计

将常用操作封装成函数：

```python
from akshare_one import get_hist_data, get_realtime_data

class StockAnalyzer:
    """股票分析工具"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.hist_data = None
        self.realtime_data = None

    def load_hist_data(self, start_date, end_date):
        """加载历史数据"""
        self.hist_data = get_hist_data(
            symbol=self.symbol,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

    def load_realtime_data(self):
        """加载实时数据"""
        self.realtime_data = get_realtime_data(symbol=self.symbol)

    def calculate_indicators(self):
        """计算技术指标"""
        if self.hist_data is None:
            return

        df = self.hist_data
        df['pct_change'] = df['close'].pct_change() * 100
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()

    def analyze(self):
        """执行分析"""
        print(f"分析股票: {self.symbol}")

        if self.realtime_data is not None and not self.realtime_data.empty:
            latest = self.realtime_data.iloc[0]
            print(f"当前价格: {latest['price']:.2f}")
            print(f"涨跌幅: {latest['pct_change']:.2f}%")
```

### 2. 错误处理封装

```python
def safe_get_data(symbol, retry=3):
    """安全获取数据（带重试）"""

    import time
    from akshare_one import get_hist_data_multi_source
    from akshare_one.modules.exceptions import DataSourceUnavailableError

    for attempt in range(retry):
        try:
            df = get_hist_data_multi_source(symbol=symbol)

            if not df.empty:
                return df
            else:
                print(f"警告：数据为空（第 {attempt+1} 次）")

        except DataSourceUnavailableError as e:
            if attempt < retry - 1:
                print(f"数据源不可用，{2}秒后重试（第 {attempt+1} 次）")
                time.sleep(2)
            else:
                print("所有尝试失败")
                return None

        except Exception as e:
            print(f"错误: {e}")
            return None

    return None
```

### 3. 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('akshare_one_app')

def get_data_with_logging(symbol):
    """带日志记录的数据获取"""

    logger.info(f"开始获取股票 {symbol} 数据")

    try:
        df = get_hist_data_multi_source(symbol=symbol)
        logger.info(f"成功获取 {len(df)} 条数据")
        return df

    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        raise
```

## 实战案例

### 案例1：每日股票报告

```python
from akshare_one import get_realtime_data, get_basic_info
import pandas as pd

def generate_daily_report(stocks):
    """生成每日股票报告"""

    report_data = []

    # 批量获取实时数据
    df_realtime = get_realtime_data()

    for symbol in stocks:
        # 筛选该股票的数据
        stock_data = df_realtime[df_realtime['symbol'] == symbol]

        if stock_data.empty:
            continue

        latest = stock_data.iloc[0]

        report_data.append({
            'symbol': symbol,
            'price': latest['price'],
            'change': latest['change'],
            'pct_change': latest['pct_change'],
            'volume': latest['volume'],
            'amount': latest['amount']
        })

    # 创建报告
    report_df = pd.DataFrame(report_data)

    # 添加统计信息
    print("\n每日股票报告")
    print("=" * 60)
    print(report_df.to_string(index=False))
    print("\n统计摘要：")
    print(f"上涨股票: {len(report_df[report_df['pct_change'] > 0])}")
    print(f"下跌股票: {len(report_df[report_df['pct_change'] < 0])}")
    print(f"平均涨跌幅: {report_df['pct_change'].mean():.2f}%")

    return report_df

# 使用示例
stocks = ["600000", "000001", "600519", "000858"]
report = generate_daily_report(stocks)
```

### 案例2：技术指标计算

```python
from akshare_one import get_hist_data
import pandas as pd
import numpy as np

def calculate_technical_indicators(symbol):
    """计算技术指标"""

    # 获取数据
    df = get_hist_data(
        symbol=symbol,
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="qfq"
    )

    if df.empty:
        return None

    # 均线系统
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()

    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # 布林带
    df['boll_mid'] = df['close'].rolling(window=20).mean()
    df['boll_std'] = df['close'].rolling(window=20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * df['boll_std']
    df['boll_lower'] = df['boll_mid'] - 2 * df['boll_std']

    return df

# 使用示例
df = calculate_technical_indicators("600000")
if df is not None:
    print("\n技术指标计算结果：")
    print(df[['timestamp', 'close', 'ma5', 'ma10', 'macd', 'rsi']].tail(10))
```

### 案例3：数据管道

```python
import os
from datetime import datetime
from akshare_one import get_hist_data

class DataPipeline:
    """数据管道"""

    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def fetch_and_process(self, stocks, start_date, end_date):
        """获取和处理数据"""

        for symbol in stocks:
            print(f"处理股票: {symbol}")

            # 获取数据
            df = get_hist_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )

            if df.empty:
                print(f"  警告：{symbol} 数据为空")
                continue

            # 处理数据
            df['pct_change'] = df['close'].pct_change() * 100
            df['ma5'] = df['close'].rolling(window=5).mean()

            # 保存数据
            filename = os.path.join(
                self.output_dir,
                f"{symbol}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            df.to_csv(filename, index=False)
            print(f"  已保存: {filename}")

# 使用示例
pipeline = DataPipeline()
stocks = ["600000", "000001", "600519"]
pipeline.fetch_and_process(stocks, "2024-01-01", "2024-12-31")
```

## 性能对比

### 批量获取 vs 循环获取

```python
import time

# 方法1：循环获取（慢）
start_time = time.time()
for symbol in ["600000", "000001", "600519"]:
    df = get_realtime_data(symbol)
elapsed1 = time.time() - start_time

# 方法2：批量获取（快）
start_time = time.time()
df_all = get_realtime_data()
df_filtered = df_all[df_all['symbol'].isin(["600000", "000001", "600519"])]
elapsed2 = time.time() - start_time

print(f"循环获取: {elapsed1:.2f}秒")
print(f"批量获取: {elapsed2:.2f}秒")
print(f"性能提升: {(elapsed1/elapsed2):.1f}倍")
```

典型结果：
- 循环获取：3-5秒
- 批量获取：0.5-1秒
- 性能提升：3-5倍

## 资源管理

### 1. 避免内存泄漏

处理大量数据时注意内存：

```python
# 不推荐：累积大量数据
all_data = []
for symbol in stock_list:  # 1000个股票
    df = get_hist_data(symbol)
    all_data.append(df)  # 内存累积

# 推荐：及时处理和释放
for symbol in stock_list:
    df = get_hist_data(symbol)

    # 立即处理
    result = process_data(df)

    # 保存后释放内存
    save_result(result, symbol)
    del df, result  # 显式释放
```

### 2. 分批处理

大量股票分批处理：

```python
def batch_process(stocks, batch_size=50):
    """分批处理大量股票"""

    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        print(f"处理批次 {i//batch_size + 1}/{len(stocks)//batch_size + 1}")

        for symbol in batch:
            process_stock(symbol)

        # 批次间休息，避免过载
        time.sleep(1)
```

## 下一步

- 查看 [高级示例](../../examples/advanced/) 学习更多实战技巧
- 查看 [FAQ](../FAQ.md) 查找常见问题解答
- 查看 [API文档](../api/) 了解所有功能