# Design Document: 市场数据扩展接口（Primitive Views）

## 1. 设计概述

本设计文档描述如何在 akshare-one 中实现 12 个缺失的 **Primitive Views**，覆盖资金流、公告信披、北向资金、宏观数据等核心维度。

**重要约束**：
- 本设计遵循 `view-api-spec.zh.md` 规范
- akshare-one 作为 **Provider 层**，为上层 View Service 提供数据
- 接口设计需要支持转换为 View API 的 Envelope 格式
- 数据标准化必须考虑 JSON 兼容性（无 NaN/Infinity）

## 2. 整体架构

### 2.1 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                   View Service (上层)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Feature Views (Dashboard)                           │  │
│  │  - margin_dashboard                                  │  │
│  │  - fund_flow_dashboard                               │  │
│  │  - hsgt_dashboard                                    │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │  Primitive Views (本次实现)                          │  │
│  │  - pv_fundflow                                       │  │
│  │  - pv_disclosure_news                                │  │
│  │  - pv_northbound_hsgt                                │  │
│  │  - pv_macro_cn                                       │  │
│  │  - ... (8 more)                                      │  │
│  └───────────────────┬───────────────────────────────────┘  │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                  akshare-one (Provider 层)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Module Factories (12 modules)                │  │
│  │  FundFlowFactory, DisclosureFactory, ...            │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│         ┌────────────┴────────────┐                         │
│         │                         │                         │
│  ┌──────▼──────┐          ┌──────▼──────┐                 │
│  │  EastMoney  │          │   Official  │                 │
│  │  Providers  │          │  Providers  │                 │
│  └─────────────┘          └─────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块组织

```
src/akshare_one/modules/
├── fundflow/           # P0: 资金流数据
│   ├── __init__.py
│   ├── factory.py      # FundFlowFactory
│   ├── base.py         # FundFlowProvider (抽象基类)
│   └── eastmoney.py    # EastmoneyFundFlowProvider
├── disclosure/         # P0: 公告信披
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── eastmoney.py
├── northbound/         # P0: 北向资金
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── eastmoney.py
├── macro/              # P1: 宏观数据
│   ├── __init__.py
│   ├── factory.py
│   ├── base.py
│   └── official.py     # 官方数据源（央行、统计局）
├── blockdeal/          # P1: 大宗交易
├── lhb/                # P2: 龙虎榜
├── limitup/            # P2: 涨停池
├── margin/             # P2: 融资融券
├── pledge/             # P2: 股权质押
├── restricted/         # P2: 限售解禁
├── goodwill/           # P2: 商誉
└── esg/                # P2: ESG 评级
```

## 3. 核心设计模式

### 3.1 Factory + Provider 模式

每个模块遵循统一的设计模式：

```python
# 1. 抽象基类
class BaseDataProvider(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """获取原始数据"""
        pass
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化数据格式"""
        pass

# 2. 具体实现
class EastmoneyProvider(BaseDataProvider):
    def fetch_data(self) -> pd.DataFrame:
        # 调用 akshare 原始接口
        pass
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # 字段映射和类型转换
        pass

# 3. 工厂类
class DataFactory:
    @staticmethod
    def get_provider(source: str, **kwargs) -> BaseDataProvider:
        providers = {
            'eastmoney': EastmoneyProvider,
        }
        return providers[source](**kwargs)
```

### 3.2 数据标准化流程

```
原始数据 → 字段映射 → 类型转换 → 缺失值处理 → 排序 → 标准化数据
```

## 4. 详细设计

### 4.1 P0: PV.FundFlow - 资金流数据

#### 4.1.1 模块结构

```python
# fundflow/base.py
class FundFlowProvider(ABC):
    @abstractmethod
    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_main_fund_flow_rank(self, date: str, indicator: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_industry_list(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_industry_constituents(self, industry_code: str) -> pd.DataFrame:
        pass
```

#### 4.1.2 数据标准化

**个股资金流标准格式**:
```python
{
    'date': str,              # YYYY-MM-DD
    'symbol': str,            # 股票代码
    'close': float,           # 收盘价
    'pct_change': float,      # 涨跌幅 (%)
    'main_net_inflow': float, # 主力净流入 (元)
    'main_net_inflow_rate': float,  # 主力净流入占比 (%)
    'super_large_net_inflow': float,  # 超大单净流入
    'large_net_inflow': float,        # 大单净流入
    'medium_net_inflow': float,       # 中单净流入
    'small_net_inflow': float,        # 小单净流入
}
```

**板块资金流标准格式**:
```python
{
    'date': str,
    'sector_code': str,       # 板块代码
    'sector_name': str,       # 板块名称
    'sector_type': str,       # 'industry' or 'concept'
    'main_net_inflow': float,
    'pct_change': float,
    'leading_stock': str,     # 领涨股代码
    'leading_stock_pct': float,  # 领涨股涨跌幅
}
```

#### 4.1.3 实现细节

```python
# fundflow/eastmoney.py
class EastmoneyFundFlowProvider(FundFlowProvider):
    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取个股资金流
        
        实现逻辑：
        1. 调用 akshare.stock_individual_fund_flow()
        2. 标准化字段名称
        3. 过滤日期范围
        4. 返回标准格式
        """
        import akshare as ak
        
        # 确定市场
        market = 'sh' if symbol.startswith('6') else 'sz'
        
        # 调用原始接口
        raw_df = ak.stock_individual_fund_flow(stock=symbol, market=market)
        
        # 标准化
        return self._standardize_stock_fund_flow(raw_df, start_date, end_date)
    
    def _standardize_stock_fund_flow(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """标准化个股资金流数据"""
        standardized = pd.DataFrame()
        
        # 字段映射
        standardized['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        standardized['close'] = df['收盘价'].astype(float)
        standardized['pct_change'] = df['涨跌幅'].astype(float)
        standardized['main_net_inflow'] = df['主力净流入-净额'].astype(float)
        standardized['main_net_inflow_rate'] = df['主力净流入-净占比'].astype(float)
        standardized['super_large_net_inflow'] = df['超大单净流入-净额'].astype(float)
        standardized['large_net_inflow'] = df['大单净流入-净额'].astype(float)
        standardized['medium_net_inflow'] = df['中单净流入-净额'].astype(float)
        standardized['small_net_inflow'] = df['小单净流入-净额'].astype(float)
        
        # 过滤日期
        mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
        return standardized[mask].reset_index(drop=True)
```

#### 4.1.4 公共接口

```python
# __init__.py
def get_stock_fund_flow(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """获取个股资金流数据
    
    Args:
        symbol: 股票代码 (e.g. '600000')
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源 ('eastmoney')
    
    Returns:
        pd.DataFrame: 标准化的资金流数据
    
    Example:
        >>> df = get_stock_fund_flow("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    from .modules.fundflow.factory import FundFlowFactory
    
    provider = FundFlowFactory.get_provider(
        source=source,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date
    )
    return provider.get_stock_fund_flow(symbol, start_date, end_date)
```

---

### 4.2 P0: PV.DisclosureNews - 公告信披

#### 4.2.1 模块结构

```python
# disclosure/base.py
class DisclosureProvider(ABC):
    @abstractmethod
    def get_disclosure_news(self, symbol: str | None, start_date: str, end_date: str, category: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_dividend_data(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_repurchase_data(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_st_delist_data(self, symbol: str | None) -> pd.DataFrame:
        pass
```

#### 4.2.2 数据标准化

**公告数据标准格式**:
```python
{
    'date': str,              # 公告日期
    'symbol': str,            # 股票代码
    'title': str,             # 公告标题
    'category': str,          # 公告类别
    'content': str,           # 公告摘要
    'url': str,               # 公告链接
}
```

**分红数据标准格式**:
```python
{
    'symbol': str,
    'fiscal_year': str,       # 分红年度
    'dividend_per_share': float,  # 每股分红
    'record_date': str,       # 股权登记日
    'ex_dividend_date': str,  # 除权除息日
    'payment_date': str,      # 派息日
    'dividend_ratio': float,  # 分红率
}
```

#### 4.2.3 实现细节

```python
# disclosure/eastmoney.py
class EastmoneyDisclosureProvider(DisclosureProvider):
    def get_dividend_data(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        """获取分红派息数据
        
        实现逻辑：
        1. 调用 akshare.stock_dividend_cninfo() 或 stock_fhps_em()
        2. 标准化字段
        3. 过滤日期范围
        """
        import akshare as ak
        
        if symbol:
            # 单个股票
            raw_df = ak.stock_dividend_cninfo(symbol=symbol)
        else:
            # 全市场（需要遍历或使用汇总接口）
            raw_df = self._fetch_all_dividends(start_date, end_date)
        
        return self._standardize_dividend_data(raw_df, start_date, end_date)
```

---

### 4.3 P0: PV.NorthboundHSGT - 北向资金

#### 4.3.1 模块结构

```python
# northbound/base.py
class NorthboundProvider(ABC):
    @abstractmethod
    def get_northbound_flow(self, start_date: str, end_date: str, market: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_northbound_holdings(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_northbound_top_stocks(self, date: str, market: str, top_n: int) -> pd.DataFrame:
        pass
```

#### 4.3.2 数据标准化

**北向资金流向标准格式**:
```python
{
    'date': str,
    'market': str,            # 'sh', 'sz', 'all'
    'net_buy': float,         # 净买入额 (亿元)
    'buy_amount': float,      # 买入额
    'sell_amount': float,     # 卖出额
    'balance': float,         # 余额
}
```

**北向持股标准格式**:
```python
{
    'date': str,
    'symbol': str,
    'holdings_shares': float,  # 持股数量 (股)
    'holdings_value': float,   # 持股市值 (元)
    'holdings_ratio': float,   # 持股占比 (%)
    'holdings_change': float,  # 持股变化 (股)
}
```

---

### 4.4 P1: PV.MacroCN - 宏观数据

#### 4.4.1 模块结构

```python
# macro/base.py
class MacroProvider(ABC):
    @abstractmethod
    def get_lpr_rate(self, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_cpi_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    # ... 其他宏观指标
```

#### 4.4.2 数据标准化

**LPR 利率标准格式**:
```python
{
    'date': str,
    'lpr_1y': float,          # 1年期LPR (%)
    'lpr_5y': float,          # 5年期LPR (%)
}
```

**PMI 指数标准格式**:
```python
{
    'date': str,
    'pmi_value': float,       # PMI值
    'yoy': float,             # 同比
    'mom': float,             # 环比
}
```

---

### 4.5 P1: PV.BlockDeal - 大宗交易

#### 4.5.1 数据标准化

**大宗交易标准格式**:
```python
{
    'date': str,
    'symbol': str,
    'price': float,           # 成交价
    'volume': float,          # 成交量 (股)
    'amount': float,          # 成交额 (元)
    'buyer_branch': str,      # 买方营业部
    'seller_branch': str,     # 卖方营业部
    'premium_rate': float,    # 折溢价率 (%)
}
```

---

### 4.6 P2: 其他接口

其他 7 个 P2 接口遵循相同的设计模式，具体实现细节见各模块设计文档。

## 5. 错误处理设计

### 5.1 异常类型

```python
class MarketDataError(Exception):
    """市场数据相关异常基类"""
    pass

class DataSourceUnavailableError(MarketDataError):
    """数据源不可用"""
    pass

class InvalidParameterError(MarketDataError):
    """无效的参数"""
    pass

class NoDataError(MarketDataError):
    """无数据返回"""
    pass
```

### 5.2 错误处理策略

| 错误场景 | 处理策略 | 返回值 |
|---------|---------|--------|
| 参数错误 | 抛出 InvalidParameterError | - |
| 数据源不可用 | 多源模式：切换；单源模式：抛出异常 | - |
| 无数据 | 记录警告日志 | 空 DataFrame |
| 网络超时 | 重试 3 次 | - |
| API 限流 | 等待后重试 | - |

## 6. JSON 兼容性设计（关键约束）

### 6.1 数据类型约束

为确保数据可以被上层 View Service 转换为 JSON Envelope，所有 Provider 必须遵循：

**禁止输出**:
- `NaN` / `Infinity` / `-Infinity`（pandas 默认会产生）
- `datetime` / `date` 对象（必须转为字符串）
- `bytes` 类型

**处理策略**:
```python
def standardize_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """确保 DataFrame 可以安全转换为 JSON"""
    df = df.copy()
    
    # 1. 处理 NaN/Infinity
    for col in df.select_dtypes(include=['float64', 'float32']).columns:
        # NaN → None (JSON null)
        df[col] = df[col].replace([float('nan')], None)
        # Infinity → None + warning
        df[col] = df[col].replace([float('inf'), float('-inf')], None)
    
    # 2. 日期转字符串
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d')
    
    # 3. 确保股票代码为字符串（保留前导0）
    if 'symbol' in df.columns:
        df['symbol'] = df['symbol'].astype(str).str.zfill(6)
    
    return df
```

### 6.2 元数据字段设计

每个 Provider 返回的 DataFrame 应包含足够的元数据，便于上层 View Service 构建 Envelope：

**建议在 Provider 类中添加元数据属性**:
```python
class FundFlowProvider(ABC):
    @property
    def metadata(self) -> dict:
        """返回数据源元数据"""
        return {
            'source': 'eastmoney',
            'data_type': 'fundflow',
            'update_frequency': 'realtime',  # realtime, daily, monthly
            'delay_minutes': 0,  # 数据延迟（分钟）
        }
```

### 6.3 空结果处理

**重要**: 空结果 ≠ 无事件，必须明确区分：

```python
def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    raw_df = self._fetch_data(symbol, start_date, end_date)
    
    if raw_df.empty:
        # 返回空 DataFrame，但保留列结构
        return pd.DataFrame(columns=[
            'date', 'symbol', 'close', 'pct_change',
            'main_net_inflow', 'main_net_inflow_rate',
            'super_large_net_inflow', 'large_net_inflow',
            'medium_net_inflow', 'small_net_inflow'
        ])
    
    return self._standardize(raw_df)
```

上层 View Service 会检测空结果并添加 `EMPTY_RESULT` warning。

## 7. 性能优化设计

### 7.1 缓存策略

```python
# 不同数据类型使用不同的缓存策略
CACHE_CONFIG = {
    'fundflow': {'ttl': 3600},      # 1小时
    'disclosure': {'ttl': 1800},    # 30分钟
    'northbound': {'ttl': 86400},   # 24小时 (T+1数据)
    'macro': {'ttl': 2592000},      # 30天 (月度数据)
    'blockdeal': {'ttl': 86400},    # 24小时
    'lhb': {'ttl': 86400},          # 24小时
    'limitup': {'ttl': 3600},       # 1小时
    'margin': {'ttl': 86400},       # 24小时
    'pledge': {'ttl': 604800},      # 7天
    'restricted': {'ttl': 86400},   # 24小时
    'goodwill': {'ttl': 2592000},   # 30天（季度数据）
    'esg': {'ttl': 2592000},        # 30天
}
```

**注意**: 缓存主要在上层 View Service 实现，Provider 层保持无状态。

### 7.2 并发支持

- 所有 Provider 类无状态设计
- 支持多线程并发调用
- 使用连接池管理 HTTP 请求

### 7.3 内存优化

- 使用生成器处理大数据量
- 及时释放中间数据
- 避免数据复制

## 8. 错误处理与降级策略

### 8.1 异常类型

```python
class MarketDataError(Exception):
    """市场数据相关异常基类"""
    pass

class DataSourceUnavailableError(MarketDataError):
    """数据源不可用"""
    pass

class InvalidParameterError(MarketDataError):
    """无效的参数"""
    pass

class NoDataError(MarketDataError):
    """无数据返回"""
    pass

class UpstreamChangedError(MarketDataError):
    """上游数据结构变化"""
    pass
```

### 8.2 错误处理策略

| 错误场景 | Provider 层处理 | View Service 层处理 |
|---------|----------------|-------------------|
| 参数错误 | 抛出 InvalidParameterError | 返回 INVALID_PARAMS |
| 数据源不可用 | 抛出 DataSourceUnavailableError | 切换数据源或返回 UPSTREAM_TIMEOUT |
| 无数据 | 返回空 DataFrame（保留列结构） | 添加 EMPTY_RESULT warning |
| 网络超时 | 重试 3 次后抛出异常 | 返回 UPSTREAM_TIMEOUT |
| API 限流 | 抛出异常 | 返回 RATE_LIMITED + stale cache |
| 字段变化 | 抛出 UpstreamChangedError | 返回 UPSTREAM_CHANGED warning |

### 8.3 参数验证

每个 Provider 必须验证：
```python
def validate_params(self, symbol: str, start_date: str, end_date: str):
    """参数验证"""
    # 1. 股票代码格式
    if not re.match(r'^\d{6}$', symbol):
        raise InvalidParameterError(f"Invalid symbol format: {symbol}")
    
    # 2. 日期格式
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        raise InvalidParameterError(f"Invalid date format: {e}")
    
    # 3. 日期范围
    if start > end:
        raise InvalidParameterError("start_date must be <= end_date")
```

## 9. 测试设计

### 9.1 单元测试

每个模块需要测试：
- Provider 的数据获取功能
- 数据标准化逻辑（包括 JSON 兼容性）
- 错误处理机制
- 参数验证

**测试示例**:
```python
def test_fundflow_json_compatibility():
    """测试资金流数据的 JSON 兼容性"""
    provider = EastmoneyFundFlowProvider()
    df = provider.get_stock_fund_flow("600000", "2024-01-01", "2024-01-31")
    
    # 1. 检查无 NaN/Infinity
    assert not df.isnull().any().any(), "Should not contain NaN"
    
    # 2. 检查日期为字符串
    assert df['date'].dtype == 'object', "Date should be string"
    
    # 3. 检查股票代码为字符串
    assert df['symbol'].dtype == 'object', "Symbol should be string"
    
    # 4. 测试 JSON 序列化
    json_str = df.to_json(orient='records')
    assert json_str is not None
```

### 9.2 集成测试

- 测试 Factory 创建 Provider
- 测试多数据源自动切换
- 测试与现有接口的集成
- 测试空结果处理

### 9.3 契约测试（Golden Sample）

为每个接口建立 golden sample，检测上游字段变化：
```python
def test_fundflow_schema_stability():
    """测试资金流数据字段稳定性"""
    expected_columns = [
        'date', 'symbol', 'close', 'pct_change',
        'main_net_inflow', 'main_net_inflow_rate',
        'super_large_net_inflow', 'large_net_inflow',
        'medium_net_inflow', 'small_net_inflow'
    ]
    
    provider = EastmoneyFundFlowProvider()
    df = provider.get_stock_fund_flow("600000", "2024-01-01", "2024-01-01")
    
    assert list(df.columns) == expected_columns, "Schema changed!"
```

### 9.4 端到端测试

- 测试真实数据获取
- 测试不同参数组合
- 测试数据源切换场景
- 测试性能（响应时间 < 10秒）

## 10. 实现计划

### 10.1 Phase 1: P0 接口 + 基础设施 (Week 1-2)

**Week 1**:
- Day 1: 建立基础设施
  - 创建 `modules/base.py`（BaseProvider 抽象类）
  - 实现 JSON 兼容性工具函数
  - 实现参数验证工具
- Day 2-3: PV.FundFlow
  - 实现 FundFlowProvider 基类
  - 实现 EastmoneyFundFlowProvider（个股资金流）
  - 单元测试 + 契约测试
- Day 4-5: PV.FundFlow（续）
  - 实现板块资金流
  - 实现主力资金排名
  - 实现板块列表和成分股查询
  - 集成测试

**Week 2**:
- Day 1-2: PV.DisclosureNews
  - 实现 DisclosureProvider 基类
  - 实现公告数据和分红数据
  - 单元测试
- Day 3: PV.DisclosureNews（续）
  - 实现回购数据和 ST/退市数据
  - 集成测试
- Day 4-5: PV.NorthboundHSGT
  - 实现 NorthboundProvider 基类
  - 实现北向资金流向和持股数据
  - 实现排名查询
  - 完整测试

### 10.2 Phase 2: P1 接口 (Week 3)

**Week 3**:
- Day 1-3: PV.MacroCN
  - 实现 MacroProvider 基类
  - 实现 LPR、PMI、CPI/PPI 接口
  - 实现 M2、Shibor、社融接口
  - 单元测试 + 集成测试
- Day 4-5: PV.BlockDeal
  - 实现 BlockDealProvider 基类
  - 实现大宗交易明细和统计
  - 完整测试

### 10.3 Phase 3: P2 接口 (Week 4-5)

**Week 4**:
- Day 1: PV.DragonTigerLHB（龙虎榜）
- Day 2: PV.LimitUpDown（涨停池）
- Day 3: PV.MarginFinancing（融资融券）
- Day 4: PV.EquityPledge（股权质押）
- Day 5: 测试和文档

**Week 5**:
- Day 1: PV.RestrictedRelease（限售解禁）
- Day 2: PV.Goodwill（商誉）
- Day 3: PV.ESG（ESG 评级）
- Day 4-5: 全面测试、性能优化、文档完善

### 10.4 里程碑

| 里程碑 | 时间 | 交付物 |
|-------|------|--------|
| M1: 基础设施 + P0 完成 | Week 2 结束 | 3 个 P0 接口 + 测试 |
| M2: P1 完成 | Week 3 结束 | 5 个接口 + 测试 |
| M3: P2 完成 | Week 5 结束 | 12 个接口 + 完整文档 |
| M4: 上线准备 | Week 6 | 性能测试 + 文档 + 发布 |

## 11. 依赖关系

### 11.1 外部依赖
- pandas >= 1.0.0
- requests >= 2.25.0
- akshare (原始数据源)
- python-dateutil >= 2.8.0

### 11.2 内部依赖
- akshare_one.modules.multi_source.MultiSourceRouter
- akshare_one.http_client
- akshare_one.modules.cache（如果存在）

### 11.3 新增依赖
无需新增外部依赖，使用现有技术栈。

## 12. 监控与可观测性

### 12.1 日志设计

```python
import logging

logger = logging.getLogger('akshare_one.modules.fundflow')

# 关键操作日志
logger.info(f"Fetching fund flow data: symbol={symbol}, date_range={start_date}~{end_date}")
logger.warning(f"Empty result for symbol={symbol}, returning empty DataFrame")
logger.error(f"Failed to fetch data from {source}: {error}")
```

### 12.2 日志级别
- DEBUG: 详细的调试信息（HTTP 请求、响应）
- INFO: 正常操作信息（数据获取开始/完成）
- WARNING: 警告信息（空结果、数据源切换）
- ERROR: 错误信息（网络错误、API 错误）

### 12.3 关键指标（供上层 View Service 使用）

Provider 层不直接实现指标收集，但设计应便于上层收集：
- API 调用次数（按接口、数据源）
- 响应时间（p50, p95, p99）
- 错误率（按错误类型）
- 空结果率
- 数据源切换次数

## 13. 安全考虑

### 13.1 输入验证
- 所有用户输入必须验证（股票代码、日期、参数）
- 防止 SQL 注入（虽然不直接操作数据库）
- 防止路径遍历（如果涉及文件操作）

### 13.2 敏感信息
- 不在日志中记录完整的 API Key
- 不在错误信息中暴露内部实现细节

### 13.3 速率限制
- Provider 层实现基础的请求间隔控制
- 避免触发上游 API 的限流机制

## 14. 文档要求

### 14.1 代码文档
- 每个公共函数必须有完整的 docstring
- 包含参数说明、返回值说明、示例代码
- 使用 Google 风格的 docstring

### 14.2 API 文档
- 更新 README.md，添加新接口说明
- 提供完整的使用示例
- 说明数据源和更新频率

### 14.3 设计文档
- 本文档作为设计参考
- 记录重要的设计决策和权衡

## 15. 验收标准

### 15.1 功能验收
- [ ] 12 个接口全部实现
- [ ] 数据字段标准化（符合 JSON 兼容性要求）
- [ ] 多数据源支持（至少 P0 接口）
- [ ] 错误处理完善（所有异常类型覆盖）
- [ ] 空结果正确处理（保留列结构）

### 15.2 质量验收
- [ ] 代码覆盖率 >= 80%
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 契约测试建立（golden sample）
- [ ] 代码符合 PEP 8 规范
- [ ] 类型注解完整

### 15.3 文档验收
- [ ] API 文档完整（每个接口有 docstring）
- [ ] 使用示例齐全（至少 2 个示例/接口）
- [ ] README 更新（新增接口列表）
- [ ] CHANGELOG 更新

### 15.4 性能验收
- [ ] 单次请求响应时间 < 10 秒（95%）
- [ ] 支持并发调用（无状态设计）
- [ ] 内存使用合理（无内存泄漏）
- [ ] JSON 序列化成功率 100%

### 15.5 兼容性验收
- [ ] 与现有接口风格一致
- [ ] 不破坏现有功能
- [ ] 向后兼容（如果修改现有代码）
- [ ] 符合 view-api-spec.zh.md 规范

## 16. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 数据源 API 变更 | 高 | 中 | 多数据源支持 + 契约测试 + 监控告警 |
| 数据格式不一致 | 中 | 低 | 严格的数据标准化 + 单元测试 |
| 性能问题 | 中 | 低 | 性能测试 + 优化代码 + 缓存策略 |
| 接口数量多 | 中 | 高 | 分阶段实现 + 优先 P0 + 代码复用 |
| JSON 兼容性问题 | 高 | 中 | 专门的兼容性测试 + 工具函数 |
| 上游限流 | 中 | 中 | 请求间隔控制 + 重试机制 + 降级策略 |

## 17. 后续优化方向

### 17.1 短期（3 个月内）
- 增加更多数据源（提高可靠性）
- 优化性能（并发、缓存）
- 完善监控和告警

### 17.2 中期（6 个月内）
- 实现本地缓存（减少 API 调用）
- 增加数据质量检查（异常值检测）
- 支持增量更新（减少数据传输）

### 17.3 长期（1 年内）
- 实现数据血缘追踪
- 支持自定义数据源
- 提供数据质量报告

## 18. 总结

本设计文档提供了 12 个市场数据扩展接口的完整实现方案，核心要点：

1. **架构清晰**: 三层架构（Providers → Primitive Views → Feature Views），akshare-one 作为 Provider 层
2. **统一模式**: Factory + Provider 模式，所有接口遵循相同设计
3. **JSON 兼容**: 严格的数据类型约束，确保可转换为 JSON Envelope
4. **数据标准化**: 统一字段名称、日期格式、数值类型
5. **错误处理**: 完善的异常体系和降级策略
6. **多数据源**: 支持自动切换和容错（优先 P0 接口）
7. **可测试性**: 单元测试 + 集成测试 + 契约测试
8. **可观测性**: 详细日志 + 元数据支持
9. **分阶段实现**: P0 → P1 → P2，优先高价值接口
10. **符合规范**: 遵循 view-api-spec.zh.md 的设计约束

该设计方案可扩展性强，易于维护，符合 akshare-one 的设计理念，并为上层 View Service 提供稳定可靠的数据支持。

---

## 附录 A: 接口命名映射

| Primitive View 名称 | akshare-one 模块名 | 公共函数前缀 |
|-------------------|------------------|------------|
| PV.FundFlow | fundflow | get_*_fund_flow |
| PV.DisclosureNews | disclosure | get_disclosure_*, get_dividend_*, get_repurchase_*, get_st_* |
| PV.NorthboundHSGT | northbound | get_northbound_* |
| PV.MacroCN | macro | get_lpr_*, get_pmi_*, get_cpi_*, get_m2_*, get_shibor_*, get_social_financing |
| PV.BlockDeal | blockdeal | get_block_deal* |
| PV.DragonTigerLHB | lhb | get_dragon_tiger_* |
| PV.LimitUpDown | limitup | get_limit_up_*, get_limit_down_* |
| PV.MarginFinancing | margin | get_margin_* |
| PV.EquityPledge | pledge | get_equity_pledge_* |
| PV.RestrictedRelease | restricted | get_restricted_release_* |
| PV.Goodwill | goodwill | get_goodwill_* |
| PV.ESG | esg | get_esg_* |

## 附录 B: 数据源映射

| 接口 | 主数据源 | 备用数据源 | 数据更新频率 |
|-----|---------|-----------|------------|
| FundFlow | eastmoney | - | 实时 |
| DisclosureNews | eastmoney | - | 实时 |
| NorthboundHSGT | eastmoney | - | T+1 |
| MacroCN | 官方网站 | - | 月度/季度 |
| BlockDeal | eastmoney | - | T+1 |
| DragonTigerLHB | eastmoney | - | T+1 |
| LimitUpDown | eastmoney | - | 实时 |
| MarginFinancing | eastmoney | - | T+1 |
| EquityPledge | eastmoney | - | 不定期 |
| RestrictedRelease | eastmoney | - | 不定期 |
| Goodwill | eastmoney | - | 季度 |
| ESG | 第三方机构 | - | 不定期 |

## 附录 C: 错误码映射

| Provider 异常 | View Service 错误码 | HTTP 状态码 |
|-------------|-------------------|-----------|
| InvalidParameterError | INVALID_PARAMS | 400 |
| DataSourceUnavailableError | UPSTREAM_TIMEOUT | 503 |
| NoDataError | EMPTY_RESULT (warning) | 200 |
| UpstreamChangedError | UPSTREAM_CHANGED (warning) | 200 |
| RateLimitError | RATE_LIMITED | 429 |
| 其他异常 | INTERNAL_ERROR | 500 |
