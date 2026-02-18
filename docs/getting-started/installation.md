# 安装指南

本指南帮助您快速安装 AKShare One。

## 环境要求

- Python 3.10 或更高版本
- pip 包管理器

## 安装方式

### 基础安装

```bash
pip install akshare-one
```

这将安装 AKShare One 的核心功能，包括所有基础数据接口和市场数据扩展模块。

### 完整安装（包含 TA-Lib 技术指标支持）

```bash
pip install akshare-one[talib]
```

### 从源码安装

```bash
git clone https://github.com/zwldarren/akshare-one.git
cd akshare-one
pip install -e .
```

## 验证安装

安装完成后，可以运行以下代码验证安装是否成功：

```python
import akshare_one

# 检查版本
print(f"AKShare One 版本: {akshare_one.__version__}")

# 测试获取历史数据
df = akshare_one.get_hist_data("600000", interval="day")
print(f"获取到 {len(df)} 条数据")
print(df.head())
```

## 依赖项说明

### 必需依赖

- **akshare** (>=1.17.80) - 底层数据接口
- **pandas** - 数据处理
- **requests** - HTTP 客户端
- **cachetools** (>=5.5.0) - 缓存系统

### 可选依赖

- **ta-lib** (>=0.6.4) - 技术指标计算（推荐安装以获得更准确的指标）

#### TA-Lib 安装注意

TA-Lib 需要单独安装系统库：

**macOS**:
```bash
brew install ta-lib
pip install TA-Lib
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ta-lib
pip install TA-Lib
```

**Windows**: 请访问 [TA-Lib 官网](https://ta-lib.org/hdr_dw.html) 下载安装包

详细安装说明请参考 [TA-Lib 官方文档](https://ta-lib.org/install/)。

## 常见安装问题

### SSL 证书问题

某些环境下可能会遇到 SSL 证书验证失败，可以通过以下方式解决：

```python
import akshare_one

# 禁用 SSL 验证（不推荐生产环境使用）
akshare_one.configure_ssl_verification(False)
```

### 代理设置

如果您在国内，可能需要配置代理：

```bash
# 设置环境变量
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### 缓存配置

AKShare One 默认启用缓存。可以通过环境变量控制缓存行为：

```bash
# 禁用缓存
export AKSHARE_ONE_CACHE_ENABLED=False
```

## 升级安装

如需升级到最新版本：

```bash
pip install --upgrade akshare-one
```

## 卸载

```bash
pip uninstall akshare-one
```

## 下一步

完成安装后，建议继续阅读 [快速开始](quickstart.md) 了解基本使用方法。
