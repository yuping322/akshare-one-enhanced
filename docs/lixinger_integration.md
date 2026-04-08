# Lixinger 数据源接入文档

理杏仁(Lixinger) OpenAPI 已成功接入到 akshare-one-enhanced 项目的各个模块中。

## 架构设计

理杏仁数据源采用与其他数据源相同的架构模式，分散到各个现有模块中：

```
modules/
├── valuation/
│   ├── base.py
│   ├── eastmoney.py
│   ├── legu.py
│   └── lixinger.py  ← 新增
├── historical/
│   ├── base.py
│   ├── eastmoney.py
│   ├── sina.py
│   └── lixinger.py  ← 新增
├── index/
│   ├── base.py
│   ├── eastmoney.py
│   ├── sina.py
│   └── lixinger.py  ← 新增
├── margin/
│   ├── base.py
│   ├── eastmoney.py
│   ├── sina.py
│   └── lixinger.py  ← 新增
└── macro/
    ├── base.py
    ├── official.py
    ├── sina.py
    └── lixinger.py  ← 新增
```

## 接入的接口

### 1. Valuation 模块 (valuation/lixinger.py)
**API**: `cn/company/fundamental/non_financial`

```python
from akshare_one.modules.valuation import get_stock_valuation

# 获取估值数据(PE、PB、PS、市值等)
df = get_stock_valuation(
    symbol="600519",
    start_date="2024-12-01",
    end_date="2024-12-10",
    source="lixinger"
)
```

**可用指标**:
- pe_ttm: PE-TTM
- pb: PB
- ps_ttm: PS-TTM
- mc: 总市值
- cmc: 流通市值
- dyr: 股息率
- 等40+估值指标

### 2. Historical 模块 (historical/lixinger.py)
**API**: `cn/company/candlestick`

```python
from akshare_one.modules.historical import get_hist_data

# 获取K线数据
df = get_hist_data(
    symbol="600519",
    start_date="2024-12-01",
    end_date="2024-12-10",
    adjust="qfq",  # 前复权
    source="lixinger"
)
```

**复权类型**:
- "none" - 不复权
- "qfq" - 前复权
- "hfq" - 后复权

### 3. Index 模块 (index/lixinger.py)
**API**: 
- `cn/index` - 指数列表
- `cn/index/constituents` - 成分股
- `cn/index/constituent-weightings` - 成分权重
- `cn/index/candlestick` - K线

```python
from akshare_one.modules.index import get_index_list, get_index_constituents

# 获取指数列表
df = get_index_list(category="cn", source="lixinger")

# 获取指数成分股(含权重)
df = get_index_constituents(
    symbol="000300",  # 沪深300
    include_weight=True,
    source="lixinger"
)
```

### 4. Margin 模块 (margin/lixinger.py)
**API**: `cn/company/margin-trading-and-securities-lending`

```python
from akshare_one.modules.margin import get_margin_data

# 获取融资融券数据
df = get_margin_data(
    symbol="600519",
    start_date="2024-12-01",
    end_date="2024-12-10",
    source="lixinger"
)
```

### 5. Macro 模块 (macro/lixinger.py)
**API**:
- `macro/price-index` - CPI/PPI
- `macro/money-supply` - M0/M1/M2
- `macro/social-financing` - 社融
- `macro/interest-rates` - 利率

```python
from akshare_one.modules.macro import get_cpi_data, get_m2_supply

# 获取CPI数据
df = get_cpi_data(
    start_date="2024-01-01",
    end_date="2024-12-31",
    source="lixinger"
)

# 获取M2数据
df = get_m2_supply(
    start_date="2024-01-01",
    end_date="2024-12-31",
    source="lixinger"
)
```

## 配置Token

### 方法1: 环境变量
```bash
export LIXINGER_TOKEN="your_token_here"
```

### 方法2: 配置文件
```bash
# 在项目根目录创建 token.cfg
echo "your_token_here" > token.cfg
```

## 核心组件

### LixingerClient (lixinger_client.py)

单例模式的API客户端，负责：
- Token管理（自动从环境变量或配置文件加载）
- HTTP请求（带重试机制）
- 错误处理和日志记录

```python
from akshare_one.lixinger_client import get_lixinger_client

client = get_lixinger_client()

# 直接调用API
response = client.query_api(
    "cn/company/fundamental/non_financial",
    {
        "stockCodes": ["600519"],
        "metricsList": ["pe_ttm", "pb"],
        "date": "2024-12-10"
    }
)
```

## 使用示例

### 示例1: 获取多只股票的估值数据
```python
from akshare_one.modules.valuation import get_stock_valuation

symbols = ["600519", "000001", "600036"]
for symbol in symbols:
    df = get_stock_valuation(
        symbol=symbol,
        date="2024-12-10",
        source="lixinger"
    )
    print(f"{symbol}: PE={df['pe_ttm'].iloc[0]:.2f}")
```

### 示例2: 获取指数成分股
```python
from akshare_one.modules.index import get_index_constituents

# 获取沪深300成分股
df = get_index_constituents(
    symbol="000300",
    include_weight=True,
    source="lixinger"
)

# 按权重排序
df_sorted = df.sort_values('weight', ascending=False)
print(df_sorted.head(10))
```

### 示例3: 批量获取宏观数据
```python
from akshare_one.modules.macro import (
    get_cpi_data,
    get_m2_supply,
    get_social_financing
)

# 获取多个宏观指标
cpi = get_cpi_data(start_date="2024-01-01", source="lixinger")
m2 = get_m2_supply(start_date="2024-01-01", source="lixinger")
sf = get_social_financing(start_date="2024-01-01", source="lixinger")
```

## 测试

运行测试脚本:
```bash
python test_lixinger_integration.py
```

## 特性

1. **统一架构**: 与其他数据源保持一致的架构模式
2. **自动注册**: 通过 Factory 模式自动注册到各模块
3. **Token管理**: 支持环境变量和配置文件，自动查找
4. **重试机制**: HTTP请求失败自动重试（最多3次）
5. **数据标准化**: 自动字段映射和类型转换
6. **错误处理**: 完善的异常处理和日志记录
7. **JSON兼容**: 自动处理NaN/Infinity等特殊值

## 已接入接口统计

| 模块 | 接口数量 | 主要功能 |
|------|---------|----------|
| Valuation | 1个 | 估值数据(PE/PB/PS/市值等) |
| Historical | 1个 | K线数据(支持复权) |
| Index | 4个 | 指数列表、成分股、权重、K线 |
| Margin | 1个 | 融资融券数据 |
| Macro | 4个 | CPI、M2、社融、利率 |
| **总计** | **11个核心接口** | 覆盖主要业务场景 |

## 扩展说明

如需添加更多Lixinger接口：

1. 找到对应的模块（如需添加龙虎榜数据，找到 `modules/lhb`）
2. 创建 `lixinger.py` 文件
3. 继承对应的 BaseProvider
4. 实现相应的方法
5. 使用 `@Factory.register("lixinger")` 注册
6. 在模块 `__init__.py` 中导入

示例：
```python
# modules/lhb/lixinger.py
from .base import LhbProvider, LhbFactory
from ..lixinger_client import get_lixinger_client

@LhbFactory.register("lixinger")
class LixingerLhbProvider(LhbProvider):
    def get_source_name(self) -> str:
        return "lixinger"
    
    def get_lhb_data(self, **kwargs):
        client = get_lixinger_client()
        response = client.query_api("cn/company/trading-abnormal", params)
        # 处理数据...
```

## 注意事项

1. **Token限制**: Lixinger API有调用次数限制，请合理使用
2. **数据延迟**: 部分数据可能有延迟，具体请参考Lixinger官方文档
3. **仅日线数据**: K线数据目前仅支持日线级别
4. **市场覆盖**: 
   - A股: 完整支持
   - 港股: 部分支持（通过扩展可添加）
   - 美股: 部分支持（通过扩展可添加）

## 相关文档

- [Lixinger OpenAPI 官方文档](https://www.lixinger.com/open/api)
- [API接口列表](https://www.lixinger.com/open/api/doc)
- 本地API文档: `/Users/fengzhi/Downloads/git/testlixingren/skills/query_data/lixinger-api-docs/docs/`