# AKShare One 快速开始指南

欢迎使用 AKShare One！本指南将帮助您在 5 分钟内完成安装并开始使用。

## 前置要求

### 系统要求

- **Python**: >= 3.10, < 3.14（**注意：暂不支持Python 3.14+**）
- **操作系统**: Windows / macOS / Linux
- **网络**: 需要访问中国金融数据 API

### 检查 Python 版本

```bash
# Linux/macOS
python3 --version

# Windows
python --version
```

**版本要求**：确保输出显示 Python 3.10、3.11、3.12 或 3.13。Python 3.14 及以上版本暂不支持。

## 一键安装

### 方式一：自动安装脚本（推荐）

#### Linux/macOS

```bash
# 下载项目
git clone https://github.com/zwldarren/akshare-one.git
cd akshare-one

# 运行快速开始脚本
bash scripts/quickstart.sh
```

#### Windows

```cmd
# 下载项目
git clone https://github.com/zwldarren/akshare-one.git
cd akshare-one

# 运行快速开始脚本
scripts\quickstart.bat
```

脚本将自动完成：
1. ✓ 检查 Python 版本
2. ✓ 创建虚拟环境（可选）
3. ✓ 安装依赖
4. ✓ 运行验证测试
5. ✓ 显示下一步指引

### 方式二：手动安装

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate.bat  # Windows

# 安装基础版本
pip install -e .

# 安装完整版本（包含 TA-Lib）
pip install -e ".[talib]"

# 验证安装
python scripts/verify_installation.py

# 可选：安装测试依赖以运行测试
pip install -r requirements-dev.txt
```

### 安装后验证

**快速验证**（无需额外依赖）：
```bash
python scripts/verify_installation.py
```

**完整验证**（需要测试依赖）：
```bash
# 安装测试工具
pip install pytest pytest-mock

# 运行最小测试集（离线测试，约1分钟）
pytest tests/ -m "not integration" --tb=no -q

# 预期结果：≥95%通过率（850+/900 tests）
```

**基准数据复现**：
```bash
# 运行示例程序验证数据输出
python examples/northbound_example.py
python examples/fundflow_example.py

# 对照 docs/MINIMUM_TEST_SUITE.md 中的基准结果验证输出
```

### 方式三：从 PyPI 安装

```bash
# 安装最新稳定版本
pip install akshare-one

# 安装完整版本
pip install akshare-one[talib]
```

## 5 分钟快速上手

**重要提示**：推荐使用多源API（`get_*_multi_source`）获得更高稳定性。单源API在网络不稳定时可能失败。

### 1. 获取历史数据（推荐多源版本，30秒）

```python
# 推荐：多源自动切换，容错性更强
from akshare_one import get_hist_data_multi_source

df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]  # 按优先级尝试
)
print(df.head())
print("数据来源:", df.attrs.get("source", "unknown"))
```

**或使用单源版本**：
```python
from akshare_one import get_hist_data

# 单源版本（需指定source，默认eastmoney_direct）
df = get_hist_data(symbol="600000", source="eastmoney")
print(df.head())
```

**输出字段结构**（实际数值随市场变化）：
```
   timestamp   open   high    low  close   volume
0 2024-01-02  XX.XX  XX.XX  XX.XX  XX.XX  XXXXXX
1 2024-01-03  XX.XX  XX.XX  XX.XX  XX.XX  XXXXXX
```

### 2. 获取实时行情（推荐多源版本，30秒）

```python
# 推荐：多源版本
from akshare_one import get_realtime_data_multi_source

df = get_realtime_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "xueqiu"]
)
print(df.head())
```

**输出字段结构**：
```
  symbol  price  change  pct_change            timestamp  volume    amount
0 600000  XX.XX   X.XX       X.XX  YYYY-MM-DD HH:MM:SS  XXXXXX  XXXXXXXX
```

### 3. 计算技术指标（1分钟）

```python
from akshare_one import get_hist_data_multi_source
from akshare_one.indicators import get_sma, get_rsi

# 使用多源API获取数据（更稳定）
df = get_hist_data_multi_source("600000", sources=["eastmoney", "sina"])

# 计算20日均线
sma_20 = get_sma(df, window=20)
print("最近5天20日均线:", sma_20.tail())

# 计算14日RSI
rsi_14 = get_rsi(df, window=14)
print("最近5天14日RSI:", rsi_14.tail())
```

### 4. 获取财务数据（1分钟）

```python
from akshare_one import get_balance_sheet, get_income_statement

# 获取资产负债表
balance = get_balance_sheet(symbol="600000")
print("资产负债表字段:", balance.columns.tolist())

# 获取利润表
income = get_income_statement(symbol="600000")
print("利润表行数:", len(income))
```

### 5. 使用数据过滤（2分钟）

```python
from akshare_one import get_hist_data_multi_source, apply_data_filter

# 获取数据（多源版本）
df = get_hist_data_multi_source("600000", sources=["eastmoney", "sina"])

# 只保留最近30天
recent = apply_data_filter(df, row_filter={"top_n": 30})

# 只保留特定列
filtered = apply_data_filter(df, columns=["timestamp", "close", "volume"])

# 按收盘价排序并取前10
top_10 = apply_data_filter(
    df,
    row_filter={"sort_by": "close", "ascending": False, "top_n": 10}
)

print("最高收盘价日期:", top_10)
```

### 6. 多数据源自动切换（核心特性）

AKShare One支持多数据源自动切换，提升数据获取稳定性：

```python
from akshare_one import get_hist_data_multi_source

# 按优先级尝试多个数据源
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)

# 查看实际使用的数据源（注：部分版本可能返回None，以实际成功获取为准）
source = df.attrs.get("source")
if source:
    print(f"数据来源: {source}")
else:
    print("多源数据获取成功")

# 对比：单源版本失败时直接报错
# from akshare_one import get_hist_data
# df = get_hist_data("600000", source="eastmoney_direct")  # 可能失败
```

**多源优势**：
- ✓ 自动故障转移，提升稳定性
- ✓ 支持多个备用数据源
- ✓ 适用于生产环境和对稳定性要求高的场景

## 常见安装问题

### Q1: Python 版本过低

**错误**: `Error: Python version must be >= 3.10`

**解决**:
- macOS: `brew install python@3.10`
- Linux: `sudo apt-get install python3.10`
- Windows: 从 [python.org](https://www.python.org/downloads/) 下载安装

### Q2: TA-Lib 安装失败

**错误**: `pip install ta-lib` 失败

**解决**:

**macOS**:
```bash
brew install ta-lib
pip install ta-lib
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install ta-lib
```

**Windows**:
1. 从 [这里](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) 下载对应版本的 .whl 文件
2. 安装: `pip install TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`

**注意**: TA-Lib 是可选依赖，不影响核心功能使用。

### Q3: 网络连接问题

**错误**: 无法获取数据，连接超时

**解决**:
1. 检查网络连接
2. 检查防火墙设置
3. 尐使用代理或 VPN
4. 使用多数据源 API 自动切换:
```python
from akshare_one import get_hist_data_multi_source
df = get_hist_data_multi_source("600000")  # 自动尝试多个源
```

### Q4: 权限错误

**错误**: `Permission denied`

**解决**:
```bash
# 使用虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 或使用用户安装
pip install --user -e .
```

### Q5: pip 未找到

**错误**: `pip: command not found`

**解决**:
```bash
# 使用 python -m pip
python3 -m pip install -e .

# 或安装 pip
python3 -m ensurepip
```

### Q6: 导入错误

**错误**: `ModuleNotFoundError: No module named 'akshare_one'`

**解决**:
1. 确认安装成功: `pip show akshare-one`
2. 确认 Python 环境: `python3 -c "import sys; print(sys.path)"`
3. 使用正确导入: `from akshare_one import get_hist_data`

### Q7: 虚拟环境激活问题

**问题**: 如何在虚拟环境中运行？

**解决**:
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate.bat

# 验证环境
python -c "import sys; print(sys.executable)"
```

## 下一步学习路径

### 📖 阅读文档

1. **API 参考**: [docs/api/overview.md](api/overview.md)
2. **完整示例**: [docs/examples.md](examples.md)
3. **高级用法**: [docs/advanced/](advanced/)

### 🔍 探索示例代码

查看 `examples/` 目录中的实际应用示例：

```bash
ls examples/
# blockdeal_example.py    - 大宗交易示例
# disclosure_example.py   - 公告披露示例
# esg_example.py          - ESG评级示例
# fundflow_example.py     - 资金流示例
# macro_example.py        - 宏观经济示例
# northbound_example.py   - 北向资金示例
```

运行示例：
```bash
python examples/northbound_example.py
```

### 🎯 学习核心功能

按顺序学习以下模块：

1. **基础数据** (1天)
   - 历史数据 `get_hist_data`
   - 实时行情 `get_realtime_data`
   - 基本信息 `get_basic_info`

2. **财务分析** (1天)
   - 资产负债表 `get_balance_sheet`
   - 利润表 `get_income_statement`
   - 现金流量表 `get_cash_flow`

3. **技术指标** (1天)
   - 移动平均 `get_sma`
   - RSI指标 `get_rsi`
   - MACD指标 `get_macd`

4. **市场数据** (2天)
   - 北向资金 `get_northbound_flow`
   - 资金流向 `get_stock_fund_flow`
   - 龙虎榜 `get_dragon_tiger_list`

5. **高级功能** (2天)
   - 多数据源切换 `*_multi_source`
   - 数据过滤 `apply_data_filter`
   - 自定义分析

### 🛠️ 实践项目建议

#### 项目1：股票监控脚本（初级，半天）

```python
from akshare_one import get_realtime_data

symbols = ["600000", "000001", "000002"]

for symbol in symbols:
    df = get_realtime_data(symbol)
    print(f"{symbol}: ¥{df['price'].iloc[0]:.2f} ({df['pct_change'].iloc[0]:.2f}%)")
```

#### 项目2：量化策略回测（中级，1天）

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# 获取数据
df = get_hist_data("600000", adjust="hfq")

# 计算均线
sma_5 = get_sma(df, window=5)
sma_20 = get_sma(df, window=20)

# 简单策略：5日线突破20日线
signals = (sma_5 > sma_20) & (sma_5.shift(1) <= sma_20.shift(1))
buy_dates = df[signals]["timestamp"]

print("买入信号:", buy_dates)
```

#### 项目3：市场分析报告（高级，2天）

```python
from akshare_one import (
    get_northbound_flow,
    get_stock_fund_flow,
    get_limit_up_pool,
)

# 获取北向资金
northbound = get_northbound_flow(market="all")

# 获取资金流
fund_flow = get_stock_fund_flow("600000")

# 获取涨停池
limit_up = get_limit_up_pool(date="2024-04-04")

# 生成分析报告
# ... (详见 examples/)
```

### 📚 进阶资源

1. **在线文档**: https://zwldarren.github.io/akshare-one/
2. **GitHub 讨论**: https://github.com/zwldarren/akshare-one/discussions
3. **问题反馈**: https://github.com/zwldarren/akshare-one/issues
4. **AKShare 原项目**: https://github.com/akfamily/akshare

### 💡 获取帮助

遇到问题？按以下顺序寻求帮助：

1. **查看文档**: 90%的问题都能在文档中找到答案
2. **运行验证**: `python scripts/verify_installation.py`
3. **搜索 Issues**: 在 GitHub Issues 中搜索类似问题
4. **提问**: 在 GitHub Discussions 中提问

## 性能优化建议

### 使用缓存

```python
# 多数据源API自动启用缓存
from akshare_one import get_hist_data_multi_source

# 日线数据缓存24小时
df = get_hist_data_multi_source("600000", interval="day")
```

### 批量获取

```python
# 获取所有实时数据（不指定symbol）
from akshare_one import get_realtime_data

df = get_realtime_data()  # 获取全市场数据
print(f"总计 {len(df)} 只股票")
```

### 数据过滤

```python
# 只获取需要的列，减少内存占用
from akshare_one import get_hist_data

df = get_hist_data(
    "600000",
    columns=["timestamp", "close"]
)
```

## 总结

完成快速开始后，您应该能够：

✓ 成功安装 AKShare One
✓ 获取历史和实时数据
✓ 计算基本技术指标
✓ 使用数据过滤功能
✓ 理解常见问题解决方法

**下一步**: 查看 [完整示例](examples.md) 或 [API 参考](api/overview.md)

---

**安装耗时**: 2-3分钟
**学习耗时**: 5分钟上手，1小时掌握基础
**问题反馈**: [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)