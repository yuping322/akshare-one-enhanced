# AKShare One Enhanced V2 — 架构设计文档

> 目标：从"薄包装集合"升级为"真正的金融数据基础设施"

---

## 一、现状诊断

### 1.1 当前架构

```
┌─────────────────────────────────────────────────────────┐
│                    Public API Layer                      │
│  170+ functions in __init__.py + 80+ JQ compat aliases   │
├─────────────────────────────────────────────────────────┤
│                    Factory + Router                      │
│  BaseFactory → create_provider → MultiSourceRouter       │
├─────────────────────────────────────────────────────────┤
│                    Provider Layer                        │
│  80+ modules × 多个数据源 = 数百个 Provider 类           │
│  大多数: akshare调用 → 重命名列 → 返回                    │
├─────────────────────────────────────────────────────────┤
│                    Infrastructure                        │
│  缓存(DuckDB+Parquet) / 异常体系 / 字段映射 / 日志       │
├─────────────────────────────────────────────────────────┤
│                    Data Sources                          │
│  AKShare / EastMoney / Sina / Lixinger / Tushare / ...   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心问题

| 问题 | 表现 | 影响 |
|------|------|------|
| 薄包装泛滥 | ~60-70% Provider 只做"调用+重命名" | 维护成本高，新增函数需写大量重复代码 |
| 验证分散 | 每个 Provider 各自写 symbol/date/enum 验证 | 代码重复，错误信息不一致 |
| 两套结构并存 | `modules/<type>/` 和 `modules/providers/<domain>/` | 目录混乱，新人难以理解 |
| 空 Provider | 大量 Provider 直接返回空 DataFrame | 功能缺失，API 承诺未兑现 |
| 缓存不智能 | 固定 TTL，不区分数据更新频率 | 缓存命中率低或数据过时 |
| 无数据质量保障 | 没有异常值检测、完整性校验 | 脏数据直接透传给用户 |

---

## 二、V2 架构设计

### 2.1 设计原则

1. **声明式优于命令式** — 配置定义 API，框架自动生成代码
2. **约定优于配置** — 合理的默认行为，减少样板代码
3. **关注点分离** — 数据获取、验证、转换、缓存各自独立
4. **可扩展性** — 插件化架构，新增数据源/数据类型最小化改动
5. **向后兼容** — 现有 API 签名不变，内部重构透明

### 2.2 总体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Public API Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ 170+ Stable │  │ JQ Compat    │  │ MCP Server (40+ tools) │  │
│  │ Functions   │  │ Layer        │  │                        │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Declarative API Engine (NEW)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ API Registry │  │ Param        │  │ Pipeline              │  │
│  │ (YAML/JSON)  │  │ Validator    │  │ Orchestrator          │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Data Processing Pipeline (NEW)               │
│  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Fetch  │→│ Validate │→│ Transform│→│ Quality Check      │  │
│  │ Stage  │  │ Stage    │  │ Stage    │  │ Stage            │  │
│  └────────┘  └──────────┘  └──────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Provider Layer (Refactored)                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ AutoProvider (declarative)  │  CustomProvider (hand-coded)│  │
│  │ 90% of APIs                 │  10% complex logic          │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure (Enhanced)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Smart    │ │ Multi-   │ │ Data     │ │ Field Mapping    │   │
│  │ Cache    │ │ Source   │ │ Quality  │ │ & Standardization│   │
│  │ Engine   │ │ Router   │ │ Monitor  │ │                  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    Data Source Adapters                         │
│  AKShare │ EastMoney │ Sina │ Lixinger │ Tushare │ BaoStock │  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块设计

### 3.1 声明式 API 引擎（核心新增）

#### 3.1.1 API 定义规范

将薄包装转为 YAML 配置：

```yaml
# apis/stock_hist.yaml
api:
  name: get_hist_data
  description: "获取股票历史行情数据"
  category: equities.quotes

  parameters:
    symbol:
      type: symbol
      market: A_STOCK
      required: true
      description: "6位股票代码"

    interval:
      type: enum
      choices: ["minute", "hour", "day", "week", "month", "year"]
      default: "day"

    interval_multiplier:
      type: int
      default: 1
      min: 1

    start_date:
      type: date
      default: "1970-01-01"

    end_date:
      type: date
      default: "2030-12-31"
      cross_validate:
        - field: start_date
          rule: "gte"  # end_date >= start_date

    adjust:
      type: enum
      choices: ["none", "qfq", "hfq"]
      default: "none"
      map:
        none: ""
        qfq: "qfq"
        hfq: "hfq"

  sources:
    sina:
      ak_func: stock_zh_a_daily
      param_mapping:
        symbol: symbol
        start_date: start_date
        end_date: end_date
        adjust: adjust  # 应用上面的 map

    eastmoney:
      ak_func: stock_zh_a_hist
      param_mapping:
        symbol: symbol
        start_date: start_date
        end_date: end_date
        adjust: adjust

    lixinger:
      api_func: get_stock_history
      param_mapping:
        symbol: symbol
        start_date: start_date
        end_date: end_date

  output:
    columns:
      日期: date
      开盘: open
      最高: high
      最低: low
      收盘: close
      成交量: volume
      成交额: amount

    post_process:
      - type: resample  # 仅当 interval != day 时
        condition: "interval in ['minute', 'hour']"
      - type: ensure_json_compatible
      - type: add_symbol_column
        value: "${symbol}"

  cache:
    enabled: true
    ttl:
      day: 86400      # 日线缓存24小时
      week: 86400
      month: 86400
      minute: 300     # 分钟线5分钟
      hour: 3600      # 小时线1小时
    key: "stock_daily"

  router:
    default_sources: ["sina", "lixinger", "eastmoney"]
    policy: RELAXED
```

#### 3.1.2 API 注册表

```python
# src/akshare_one/api_registry/__init__.py

from pathlib import Path
import yaml

class APIRegistry:
    """集中管理所有 API 定义"""

    _instance = None
    _apis: dict[str, dict] = {}

    @classmethod
    def load(cls, api_dir: str | Path = None):
        """加载所有 YAML API 定义"""
        api_dir = api_dir or Path(__file__).parent / "apis"
        for yaml_file in Path(api_dir).glob("*.yaml"):
            with open(yaml_file) as f:
                api_def = yaml.safe_load(f)
                cls._apis[api_def["api"]["name"]] = api_def

    @classmethod
    def get(cls, name: str) -> dict:
        return cls._apis[name]

    @classmethod
    def list_apis(cls) -> list[str]:
        return list(cls._apis.keys())

    @classmethod
    def get_by_category(cls, category: str) -> list[str]:
        return [
            name for name, api in cls._apis.items()
            if api["api"]["category"] == category
        ]
```

#### 3.1.3 自动 Provider 生成器

```python
# src/akshare_one/api_engine/auto_provider.py

class AutoProvider(BaseProvider):
    """
    根据 YAML 配置自动生成的 Provider。
    无需手写代码，只需声明配置。
    """

    def __init__(self, api_def: dict, source: str, **kwargs):
        super().__init__(**kwargs)
        self.api_def = api_def
        self.source = source
        self.source_config = api_def["sources"][source]

        # 从配置构建验证器
        self.validators = self._build_validators()
        # 从配置构建参数映射
        self.param_mapper = self._build_param_mapper()
        # 从配置构建输出管道
        self.output_pipeline = self._build_output_pipeline()

    def _build_validators(self) -> list[BaseValidator]:
        """从 API 定义构建验证器链"""
        validators = []
        for param_name, param_def in self.api_def["parameters"].items():
            validator = ValidatorFactory.create(param_name, param_def)
            validators.append(validator)
        return validators

    def _build_param_mapper(self) -> ParamMapper:
        """构建参数映射器（内部参数 → 上游 API 参数）"""
        return ParamMapper(self.source_config.get("param_mapping", {}))

    def _build_output_pipeline(self) -> OutputPipeline:
        """构建输出处理管道"""
        stages = []
        for stage_def in self.api_def["output"].get("post_process", []):
            stage = StageFactory.create(stage_def)
            stages.append(stage)
        return OutputPipeline(stages)

    def execute(self, **kwargs) -> pd.DataFrame:
        """通用执行流程"""
        # 1. 验证参数
        for validator in self.validators:
            validator.validate(kwargs)

        # 2. 映射参数
        upstream_params = self.param_mapper.map(kwargs)

        # 3. 调用上游
        raw_df = self._call_upstream(upstream_params)

        # 4. 字段重命名
        df = self._rename_columns(raw_df)

        # 5. 后处理管道
        df = self.output_pipeline.execute(df, kwargs)

        # 6. 标准化 + 过滤
        return self.standardize_and_filter(
            df,
            source=self.source,
            columns=kwargs.get("columns"),
            row_filter=kwargs.get("row_filter"),
        )

    def _call_upstream(self, params: dict) -> pd.DataFrame:
        """调用上游数据源"""
        source_config = self.source_config
        if "ak_func" in source_config:
            return self.akshare_adapter.call(source_config["ak_func"], **params)
        elif "api_func" in source_config:
            # 其他数据源
            return self._call_custom_api(source_config, params)
        else:
            raise NotImplementedError(f"No upstream function configured for {self.source}")
```

### 3.2 统一参数验证框架（核心新增）

#### 3.2.1 验证器体系

```python
# src/akshare_one/validation/__init__.py

from abc import ABC, abstractmethod
from typing import Any
from .exceptions import ValidationError

class BaseValidator(ABC):
    """验证器基类"""

    def __init__(self, param_name: str, required: bool = True, message: str = None):
        self.param_name = param_name
        self.required = required
        self.message = message

    def validate(self, value: Any, context: dict = None) -> None:
        if value is None:
            if self.required:
                raise ValidationError(f"{self.param_name} is required")
            return
        self._do_validate(value, context or {})

    @abstractmethod
    def _do_validate(self, value: Any, context: dict) -> None:
        ...


class SymbolValidator(BaseValidator):
    """股票代码验证"""

    PATTERNS = {
        "A_STOCK": r"^\d{6}$",
        "BOND": r"^(sh|sz)\d{6}$",
        "ETF": r"^\d{6}$",
        "FUTURES": r"^[A-Z]{1,2}\d{4}$",
        "INDEX": r"^\d{6}$",
    }

    def __init__(self, param_name: str = "symbol", market: str = "A_STOCK", **kwargs):
        super().__init__(param_name, **kwargs)
        self.market = market
        self.pattern = self.PATTERNS[market]

    def _do_validate(self, value: str, context: dict) -> None:
        import re
        if not re.match(self.pattern, value):
            raise ValidationError(
                f"Invalid {self.market} symbol: {value}",
                param=self.param_name,
                value=value,
            )


class DateValidator(BaseValidator):
    """日期格式验证"""

    def __init__(self, param_name: str = "date", fmt: str = "%Y-%m-%d", **kwargs):
        super().__init__(param_name, **kwargs)
        self.fmt = fmt

    def _do_validate(self, value: str, context: dict) -> None:
        from datetime import datetime
        try:
            datetime.strptime(value, self.fmt)
        except ValueError:
            raise ValidationError(
                f"Invalid date format: {value}, expected {self.fmt}",
                param=self.param_name,
                value=value,
            )


class DateRangeValidator(BaseValidator):
    """日期范围交叉验证"""

    def __init__(self, start_field: str = "start_date", end_field: str = "end_date", **kwargs):
        super().__init__(end_field, **kwargs)
        self.start_field = start_field
        self.end_field = end_field

    def validate(self, value: Any, context: dict = None) -> None:
        """需要传入完整参数字典"""
        start = context.get(self.start_field)
        end = context.get(self.end_field)
        if start and end:
            from datetime import datetime
            if datetime.strptime(start, "%Y-%m-%d") > datetime.strptime(end, "%Y-%m-%d"):
                raise ValidationError(
                    f"start_date ({start}) must be <= end_date ({end})",
                    param=self.end_field,
                    value=end,
                )


class EnumValidator(BaseValidator):
    """枚举值验证"""

    def __init__(self, param_name: str, choices: list, **kwargs):
        super().__init__(param_name, **kwargs)
        self.choices = choices

    def _do_validate(self, value: str, context: dict) -> None:
        if value not in self.choices:
            raise ValidationError(
                f"Invalid value '{value}' for {self.param_name}. "
                f"Must be one of: {self.choices}",
                param=self.param_name,
                value=value,
            )


class RangeValidator(BaseValidator):
    """数值范围验证"""

    def __init__(self, param_name: str, min_val: float = None, max_val: float = None, **kwargs):
        super().__init__(param_name, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def _do_validate(self, value: float, context: dict) -> None:
        if self.min_val is not None and value < self.min_val:
            raise ValidationError(f"{self.param_name} must be >= {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValidationError(f"{self.param_name} must be <= {self.max_val}")


class CrossFieldValidator(BaseValidator):
    """跨字段关系验证"""

    def __init__(self, fields: list[str], rule: str, **kwargs):
        super().__init__(fields[0], **kwargs)
        self.fields = fields
        self.rule = rule  # "gte", "lte", "eq", "neq", "at_least_one_required"

    def validate(self, value: Any, context: dict = None) -> None:
        values = {f: context.get(f) for f in self.fields}
        if self.rule == "at_least_one_required":
            if not any(values.values()):
                raise ValidationError(f"At least one of {self.fields} is required")
        elif self.rule == "gte":
            if values[self.fields[0]] and values[self.fields[1]]:
                if values[self.fields[0]] > values[self.fields[1]]:
                    raise ValidationError(f"{self.fields[0]} must be <= {self.fields[1]}")
        # ... 其他规则
```

#### 3.2.2 验证器工厂

```python
class ValidatorFactory:
    """根据配置创建验证器"""

    @staticmethod
    def create(param_name: str, param_def: dict) -> BaseValidator:
        param_type = param_def.get("type")

        if param_type == "symbol":
            return SymbolValidator(
                param_name,
                market=param_def.get("market", "A_STOCK"),
                required=param_def.get("required", True),
            )
        elif param_type == "date":
            return DateValidator(
                param_name,
                fmt=param_def.get("format", "%Y-%m-%d"),
                required=param_def.get("required", True),
            )
        elif param_type == "enum":
            return EnumValidator(
                param_name,
                choices=param_def["choices"],
                required=param_def.get("required", True),
            )
        elif param_type == "int":
            return RangeValidator(
                param_name,
                min_val=param_def.get("min"),
                max_val=param_def.get("max"),
                required=param_def.get("required", True),
            )
        # ... 更多类型

        return None  # 无验证器
```

#### 3.2.3 验证链装饰器

```python
def validated(validators: list[BaseValidator]):
    """验证链装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for validator in validators:
                validator.validate(kwargs.get(validator.param_name), kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3.3 数据处理管道（核心新增）

#### 3.3.1 管道架构

```python
# src/akshare_one/pipeline/__init__.py

class PipelineStage(ABC):
    """管道阶段基类"""

    @abstractmethod
    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        ...

    @abstractmethod
    def should_run(self, context: dict) -> bool:
        """根据上下文决定是否执行此阶段"""
        return True


class OutputPipeline:
    """输出处理管道"""

    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        for stage in self.stages:
            if stage.should_run(context):
                df = stage.execute(df, context)
        return df


# 内置阶段
class ColumnRenameStage(PipelineStage):
    """列重命名"""
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        return df.rename(columns=self.mapping)

    def should_run(self, context: dict) -> bool:
        return True


class ResampleStage(PipelineStage):
    """数据重采样"""
    def __init__(self, interval: str, multiplier: int):
        self.interval = interval
        self.multiplier = multiplier

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        # 重采样逻辑
        ...

    def should_run(self, context: dict) -> bool:
        interval = context.get("interval", "day")
        return interval in ["minute", "hour"]


class UnitConversionStage(PipelineStage):
    """单位转换"""
    def __init__(self, conversions: dict[str, str]):
        self.conversions = conversions  # {"amount": "yi_yuan_to_yuan"}

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        for col, conversion in self.conversions.items():
            if col in df.columns:
                df[col] = self._convert(df[col], conversion)
        return df


class QualityCheckStage(PipelineStage):
    """数据质量检查（NEW）"""
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        issues = []
        for rule in self.rules:
            issue = self._check_rule(df, rule)
            if issue:
                issues.append(issue)

        if issues:
            # 记录质量警告（不阻断）
            log_data_quality_issues(context.get("source"), context.get("api"), issues)

        return df

    def _check_rule(self, df: pd.DataFrame, rule: dict) -> dict | None:
        rule_type = rule["type"]
        if rule_type == "null_rate":
            col = rule["column"]
            threshold = rule.get("max_null_rate", 0.5)
            null_rate = df[col].isna().mean()
            if null_rate > threshold:
                return {
                    "type": "high_null_rate",
                    "column": col,
                    "rate": null_rate,
                    "threshold": threshold,
                }
        elif rule_type == "negative_values":
            col = rule["column"]
            if col in df.columns and (df[col] < 0).any():
                return {"type": "negative_values", "column": col}
        elif rule_type == "date_order":
            col = rule["column"]
            if col in df.columns:
                if not pd.Series(df[col]).is_monotonic_increasing:
                    return {"type": "date_not_sorted", "column": col}
        return None
```

### 3.4 智能缓存引擎（增强）

#### 3.4.1 当前问题

- 固定 TTL，不区分数据更新频率
- 实时数据缓存 24 小时 → 数据过时
- 日线数据缓存 5 分钟 → 无意义请求

#### 3.4.2 新设计

```python
# src/akshare_one/cache/smart_cache.py

from enum import Enum
from datetime import timedelta

class DataFreshness(Enum):
    """数据更新频率分类"""
    REALTIME = "realtime"        # 实时行情
    INTRADAY = "intraday"        # 盘中数据（分钟线）
    DAILY = "daily"              # 日级数据
    WEEKLY = "weekly"            # 周级数据
    QUARTERLY = "quarterly"      # 季度数据（财报）
    STATIC = "static"            # 静态数据（股票列表）


# 缓存策略表
CACHE_POLICIES = {
    DataFreshness.REALTIME: {
        "memory_ttl": timedelta(minutes=1),
        "disk_ttl": timedelta(minutes=5),
        "refresh_during_trading": True,
    },
    DataFreshness.INTRADAY: {
        "memory_ttl": timedelta(minutes=5),
        "disk_ttl": timedelta(hours=1),
        "refresh_during_trading": True,
    },
    DataFreshness.DAILY: {
        "memory_ttl": timedelta(hours=1),
        "disk_ttl": timedelta(days=1),
        "refresh_during_trading": False,  # 收盘后刷新
    },
    DataFreshness.WEEKLY: {
        "memory_ttl": timedelta(hours=1),
        "disk_ttl": timedelta(weeks=1),
        "refresh_during_trading": False,
    },
    DataFreshness.QUARTERLY: {
        "memory_ttl": timedelta(hours=1),
        "disk_ttl": timedelta(days=30),
        "refresh_during_trading": False,
    },
    DataFreshness.STATIC: {
        "memory_ttl": timedelta(hours=24),
        "disk_ttl": timedelta(days=7),
        "refresh_during_trading": False,
    },
}


class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self):
        self.policies = CACHE_POLICIES
        self.trading_calendar = TradingCalendar()

    def get_ttl(self, freshness: DataFreshness, is_trading_hours: bool) -> dict:
        """根据数据新鲜度和交易时间获取 TTL"""
        policy = self.policies[freshness]

        # 交易时间内，实时/盘中数据缩短 TTL
        if is_trading_hours and policy["refresh_during_trading"]:
            return {
                "memory_ttl": policy["memory_ttl"] / 2,
                "disk_ttl": policy["disk_ttl"] / 2,
            }

        return {
            "memory_ttl": policy["memory_ttl"],
            "disk_ttl": policy["disk_ttl"],
        }

    def should_refresh(self, cache_time: datetime, freshness: DataFreshness) -> bool:
        """判断是否应该刷新缓存"""
        policy = self.policies[freshness]
        now = datetime.now()

        # 检查是否在交易时间内需要刷新
        if self.trading_calendar.is_trading_hours(now) and policy["refresh_during_trading"]:
            return (now - cache_time) > policy["memory_ttl"] / 2

        return (now - cache_time) > policy["memory_ttl"]
```

#### 3.4.3 缓存注解增强

```python
def smart_cache_v2(
    freshness: DataFreshness = DataFreshness.DAILY,
    key_builder: Callable = None,
):
    """
    智能缓存装饰器 V2

    根据数据更新频率自动选择 TTL。
    自动判断交易时间，动态调整缓存策略。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mgr = get_smart_cache_manager()
            is_trading = is_trading_hours()
            ttl_config = mgr.get_ttl(freshness, is_trading)

            # 构建缓存 key
            cache_key = (key_builder or default_key_builder)(func, args, kwargs)

            # 尝试从缓存获取
            cached = mgr.get(cache_key)
            if cached and not mgr.should_refresh(cached.time, freshness):
                return cached.data

            # 缓存未命中或过期，重新获取
            result = func(*args, **kwargs)
            mgr.put(cache_key, result, ttl_config)
            return result

        return wrapper
    return decorator
```

### 3.5 数据质量监控（核心新增）

#### 3.5.1 质量监控体系

```python
# src/akshare_one/quality/__init__.py

class DataQualityReport:
    """数据质量报告"""

    def __init__(self, source: str, api: str, df: pd.DataFrame):
        self.source = source
        self.api = api
        self.df = df
        self.issues: list[QualityIssue] = []
        self.metrics: dict = {}

    def run_checks(self, rules: list[QualityRule]) -> "DataQualityReport":
        """执行质量检查"""
        for rule in rules:
            result = rule.check(self.df)
            if not result.passed:
                self.issues.append(result)
        self._compute_metrics()
        return self

    def _compute_metrics(self):
        self.metrics = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "null_rate": self.df.isna().mean().mean(),
            "duplicate_rate": self.df.duplicated().mean(),
        }

    @property
    def is_healthy(self) -> bool:
        return len(self.issues) == 0

    @property
    def severity(self) -> str:
        if any(i.severity == "critical" for i in self.issues):
            return "critical"
        if any(i.severity == "warning" for i in self.issues):
            return "warning"
        return "healthy"


class QualityRule(ABC):
    """质量规则基类"""

    def __init__(self, severity: str = "warning"):
        self.severity = severity

    @abstractmethod
    def check(self, df: pd.DataFrame) -> QualityIssue | None:
        ...


# 内置规则
class NullRateRule(QualityRule):
    """空值率检查"""
    def __init__(self, column: str, max_rate: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.max_rate = max_rate

    def check(self, df: pd.DataFrame) -> QualityIssue | None:
        if self.column not in df.columns:
            return QualityIssue(
                rule="missing_column",
                severity="critical",
                message=f"Column '{self.column}' not found",
            )
        rate = df[self.column].isna().mean()
        if rate > self.max_rate:
            return QualityIssue(
                rule="high_null_rate",
                severity="warning",
                message=f"Column '{self.column}' null rate {rate:.2%} > {self.max_rate:.2%}",
                column=self.column,
                value=rate,
            )
        return None


class SchemaRule(QualityRule):
    """Schema 变更检查"""
    def __init__(self, required_columns: list[str], **kwargs):
        super().__init__(**kwargs)
        self.required_columns = required_columns

    def check(self, df: pd.DataFrame) -> QualityIssue | None:
        missing = set(self.required_columns) - set(df.columns)
        if missing:
            return QualityIssue(
                rule="schema_changed",
                severity="critical",
                message=f"Missing required columns: {missing}",
                missing_columns=list(missing),
            )
        return None


class RangeRule(QualityRule):
    """数值范围检查"""
    def __init__(self, column: str, min_val: float, max_val: float, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.min_val = min_val
        self.max_val = max_val

    def check(self, df: pd.DataFrame) -> QualityIssue | None:
        if self.column not in df.columns:
            return None
        out_of_range = df[
            (df[self.column] < self.min_val) | (df[self.column] > self.max_val)
        ]
        if len(out_of_range) > 0:
            return QualityIssue(
                rule="out_of_range",
                severity="warning",
                message=f"Column '{self.column}' has {len(out_of_range)} values outside [{self.min_val}, {self.max_val}]",
                column=self.column,
                count=len(out_of_range),
            )
        return None


class MonotonicRule(QualityRule):
    """单调性检查（用于时间序列）"""
    def __init__(self, column: str, increasing: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.increasing = increasing

    def check(self, df: pd.DataFrame) -> QualityIssue | None:
        if self.column not in df.columns or len(df) < 2:
            return None
        series = pd.Series(df[self.column])
        is_mono = series.is_monotonic_increasing if self.increasing else series.is_monotonic_decreasing
        if not is_mono:
            return QualityIssue(
                rule="not_monotonic",
                severity="warning",
                message=f"Column '{self.column}' is not {'increasing' if self.increasing else 'decreasing'}",
                column=self.column,
            )
        return None
```

#### 3.5.2 质量监控集成到管道

```python
class QualityCheckStage(PipelineStage):
    """数据质量检查阶段"""

    def __init__(self, rules: list[QualityRule], on_failure: str = "warn"):
        """
        on_failure: "warn" | "raise" | "skip"
        """
        self.rules = rules
        self.on_failure = on_failure

    def execute(self, df: pd.DataFrame, context: dict) -> pd.DataFrame:
        report = DataQualityReport(
            source=context.get("source", "unknown"),
            api=context.get("api", "unknown"),
            df=df,
        )
        report.run_checks(self.rules)

        # 记录质量报告
        log_quality_report(report)

        # 根据策略处理
        if self.on_failure == "raise" and report.severity == "critical":
            raise DataValidationError(
                f"Data quality check failed: {report.issues}"
            )

        # 将报告附加到 DataFrame attrs
        df.attrs["quality_report"] = report
        return df
```

### 3.6 多源路由增强

#### 3.6.1 当前问题

- 固定源顺序，不根据成功率动态调整
- 没有源健康度评分
- 空数据处理策略不够灵活

#### 3.6.2 新设计

```python
# src/akshare_one/modules/core/smart_router.py

class SourceHealthTracker:
    """数据源健康追踪器"""

    def __init__(self):
        self.stats: dict[str, dict] = {}

    def record(self, source: str, success: bool, duration_ms: float, rows: int = 0):
        if source not in self.stats:
            self.stats[source] = {
                "total": 0, "success": 0, "failure": 0,
                "total_duration": 0, "total_rows": 0,
            }
        s = self.stats[source]
        s["total"] += 1
        if success:
            s["success"] += 1
        else:
            s["failure"] += 1
        s["total_duration"] += duration_ms
        s["total_rows"] += rows

    def get_score(self, source: str) -> float:
        """计算源健康评分 (0-1)"""
        s = self.stats.get(source)
        if not s or s["total"] == 0:
            return 0.5  # 默认中等评分

        success_rate = s["success"] / s["total"]
        avg_duration = s["total_duration"] / s["total"]

        # 综合评分：成功率 70% + 速度 30%
        speed_score = max(0, 1 - (avg_duration / 5000))  # 5秒内为满分
        return success_rate * 0.7 + speed_score * 0.3

    def get_sorted_sources(self, sources: list[str]) -> list[str]:
        """按健康评分排序源"""
        return sorted(sources, key=lambda s: self.get_score(s), reverse=True)


class SmartRouter(MultiSourceRouter):
    """智能多源路由器"""

    def __init__(self, providers: list[tuple[str, Any]], **kwargs):
        super().__init__(providers, **kwargs)
        self.health_tracker = SourceHealthTracker()

    def execute(self, method_name: str, *args, **kwargs) -> pd.DataFrame:
        # 按健康评分排序源
        sorted_providers = self.health_tracker.get_sorted_sources(
            [name for name, _ in self.providers]
        )

        best_result = None
        for source_name in sorted_providers:
            provider = dict(self.providers)[source_name]
            start = time.time()
            try:
                result = getattr(provider, method_name)(*args, **kwargs)
                duration = (time.time() - start) * 1000

                if isinstance(result, pd.DataFrame) and not result.empty:
                    self.health_tracker.record(
                        source_name, True, duration, len(result)
                    )
                    return result

                self.health_tracker.record(source_name, True, duration, 0)
                if best_result is None:
                    best_result = result

            except Exception as e:
                duration = (time.time() - start) * 1000
                self.health_tracker.record(source_name, False, duration)

        return best_result or pd.DataFrame()
```

---

## 四、目录结构重构

### 4.1 新目录结构

```
src/akshare_one/
├── __init__.py                    # 公共 API 入口（保持不变，向后兼容）
├── api_registry/                  # NEW: 声明式 API 定义
│   ├── __init__.py
│   ├── apis/                      # YAML API 定义文件
│   │   ├── equities/
│   │   │   ├── hist_data.yaml
│   │   │   ├── realtime.yaml
│   │   │   └── basic_info.yaml
│   │   ├── funds/
│   │   ├── indices/
│   │   ├── derivatives/
│   │   ├── fixed_income/
│   │   ├── capital/
│   │   ├── macro/
│   │   └── ...
│   └── loader.py
├── api_engine/                    # NEW: API 执行引擎
│   ├── __init__.py
│   ├── auto_provider.py           # 自动 Provider 生成器
│   ├── param_mapper.py            # 参数映射器
│   ├── output_pipeline.py         # 输出管道
│   └── stage_factory.py           # 管道阶段工厂
├── validation/                    # NEW: 统一验证框架
│   ├── __init__.py
│   ├── validators.py              # 验证器实现
│   ├── factory.py                 # 验证器工厂
│   └── exceptions.py              # 验证异常
├── pipeline/                      # NEW: 数据处理管道
│   ├── __init__.py
│   ├── stages.py                  # 管道阶段
│   └── orchestrator.py            # 管道编排器
├── quality/                       # NEW: 数据质量监控
│   ├── __init__.py
│   ├── rules.py                   # 质量规则
│   ├── report.py                  # 质量报告
│   └── monitor.py                 # 质量监控器
├── cache/                         # 增强: 智能缓存
│   ├── __init__.py
│   ├── smart_cache.py             # 智能缓存管理器
│   ├── engine.py                  # DuckDB 引擎
│   ├── store.py                   # Parquet 存储
│   └── schema.py                  # Schema 定义
├── modules/                       # 重构: Provider 层
│   ├── core/                      # 核心基础设施
│   │   ├── base.py                # BaseProvider（简化）
│   │   ├── factory.py             # BaseFactory
│   │   ├── router.py              # MultiSourceRouter
│   │   ├── smart_router.py        # NEW: 智能路由
│   │   ├── exceptions.py          # 异常体系
│   │   ├── calendar.py            # 交易日历
│   │   └── field_mapping/         # 字段映射
│   ├── providers/                 # 按领域组织的 Provider
│   │   ├── equities/
│   │   │   ├── quotes/            # 行情
│   │   │   ├── fundamentals/      # 基本面
│   │   │   ├── capital/           # 资金
│   │   │   ├── corporate_events/  # 公司事件
│   │   │   └── trading_events/    # 交易事件
│   │   ├── funds/
│   │   ├── indices/
│   │   ├── derivatives/
│   │   ├── fixed_income/
│   │   ├── sectors/
│   │   ├── macro/
│   │   ├── news/
│   │   └── sentiment/
│   └── indicators/                # 技术指标
├── indicators.py                  # 技术指标（保持不变）
├── risk.py                        # 风控（保持不变）
├── strategy.py                    # 策略（保持不变）
├── jq_compat/                     # JoinQuant 兼容（保持不变）
├── mcp/                           # MCP Server
└── constants.py
```

### 4.2 迁移策略

```
Phase 1: 基础设施（2-3周）
├── 实现 validation 模块
├── 实现 pipeline 模块
├── 实现 quality 模块
├── 增强 cache 模块
└── 编写单元测试

Phase 2: 声明式引擎（3-4周）
├── 实现 API Registry
├── 实现 AutoProvider
├── 定义 20 个核心 API 的 YAML 配置
├── 新旧 Provider 并行运行
└── 对比测试结果

Phase 3: 渐进迁移（4-6周）
├── 每周迁移 10-15 个 API 到声明式
├── 清理空 Provider
├── 统一目录结构
└── 更新文档

Phase 4: 高价值功能（持续）
├── 智能路由（动态源排序）
├── 增量更新机制
├── 跨源数据融合
└── 回测引擎集成
```

---

## 五、关键设计决策

### 5.1 为什么用 YAML 而不是纯 Python 配置？

| 维度 | YAML | Python |
|------|------|--------|
| 可读性 | 高，非程序员可理解 | 中，需要 Python 知识 |
| 可维护性 | 高，配置集中管理 | 低，散落在代码中 |
| 代码生成 | 容易，可自动生成 Python | 需要手动写 |
| 版本控制 | 友好，diff 清晰 | 友好 |
| 灵活性 | 中，复杂逻辑受限 | 高，任意逻辑 |

**结论**：90% 的薄包装用 YAML，10% 的复杂逻辑保留 Python 实现（CustomProvider）。

### 5.2 向后兼容策略

- **API 签名不变** — `get_hist_data(symbol, interval, ...)` 签名完全不变
- **内部重构透明** — 用户无感知
- **渐进迁移** — 新旧实现并行，逐步切换
- **Feature Flag** — 通过环境变量控制是否启用新引擎

```python
# 环境变量控制
AKSHARE_ONE_USE_V2_ENGINE=true   # 使用新引擎
AKSHARE_ONE_USE_V2_ENGINE=false  # 使用旧实现（默认）
```

### 5.3 性能考量

| 优化点 | 方案 | 预期效果 |
|--------|------|---------|
| 缓存命中率 | 智能 TTL + 交易时间感知 | +30% |
| 多源路由 | 健康评分动态排序 | -50% 失败率 |
| 参数验证 | 预编译正则 + 批量验证 | -20% 验证开销 |
| 字段映射 | 缓存映射结果 | -40% 映射开销 |
| 数据质量 | 抽样检查（非全量） | 可忽略 |

---

## 六、预期效果

### 6.1 代码量对比

| 指标 | 当前 | V2 目标 |
|------|------|---------|
| Provider 类数量 | ~500+ | ~50（CustomProvider）+ YAML 配置 |
| 验证代码行数 | 分散在 200+ 文件 | 集中在 validation 模块（~500行） |
| 新增 API 成本 | 写 50-100 行 Python | 写 30 行 YAML 配置 |
| 单元测试覆盖 | ~60% | ~90%（声明式 API 自动测试） |

### 6.2 功能增强

| 功能 | 当前 | V2 |
|------|------|-----|
| 参数验证 | 分散、不一致 | 统一框架、声明式 |
| 缓存策略 | 固定 TTL | 智能、数据频率感知 |
| 多源路由 | 固定顺序 | 动态健康评分排序 |
| 数据质量 | 无 | 完整监控体系 |
| 新增 API | 写代码 | 写配置 |
| 错误诊断 | 基础 | 质量报告 + 源追踪 |

---

## 七、示例：迁移一个 API

### 7.1 当前实现（~80行）

```python
# src/akshare_one/modules/providers/equities/quotes/historical/sina.py
class SinaHistorical(BaseProvider):
    def __init__(self, symbol, interval="day", interval_multiplier=1,
                 start_date="1970-01-01", end_date="2030-12-31", adjust="none"):
        super().__init__()
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        if interval not in ["minute", "hour", "day", "week", "month", "year"]:
            raise ValueError(f"Invalid interval: {interval}")
        if interval_multiplier < 1:
            raise ValueError("interval_multiplier must be >= 1")
        if adjust not in ["none", "qfq", "hfq"]:
            raise ValueError(f"Invalid adjust: {adjust}")
        self.symbol = symbol
        self.interval = interval
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self.adjust = adjust

    def get_hist_data(self):
        if self.interval in ["minute", "hour"]:
            return self._get_minute_data()
        return self._get_daily_data()

    def _get_daily_data(self):
        raw_df = ak.stock_zh_a_daily(
            symbol=self.symbol,
            start_date=self.start_date,
            end_date=self.end_date,
            adjust=self._map_adjust(self.adjust),
        )
        return self.standardize_and_filter(raw_df, source="sina", ...)

    def _get_minute_data(self):
        # 分钟数据获取逻辑...
        ...

    def _map_adjust(self, adjust):
        return adjust if adjust != "none" else ""

    def _resample_data(self, df, interval, multiplier):
        # 重采样逻辑...
        ...
```

### 7.2 V2 实现（YAML 配置 ~50行 + 1个 CustomProvider ~30行）

```yaml
# src/akshare_one/api_registry/apis/equities/hist_data.yaml
api:
  name: get_hist_data
  parameters:
    symbol: { type: symbol, market: A_STOCK, required: true }
    interval: { type: enum, choices: [minute, hour, day, week, month, year], default: day }
    interval_multiplier: { type: int, default: 1, min: 1 }
    start_date: { type: date, default: "1970-01-01" }
    end_date: { type: date, default: "2030-12-31", cross_validate: { field: start_date, rule: gte } }
    adjust: { type: enum, choices: [none, qfq, hfq], default: none, map: { none: "" } }

  sources:
    sina:
      ak_func: stock_zh_a_daily
      param_mapping: { symbol: symbol, start_date: start_date, end_date: end_date, adjust: adjust }

  output:
    columns: { 日期: date, 开盘: open, 最高: high, 最低: low, 收盘: close, 成交量: volume }
    post_process:
      - { type: resample, condition: "interval in ['minute', 'hour']" }

  cache: { enabled: true, freshness: daily }
  quality:
    rules:
      - { type: schema, required_columns: [date, open, high, low, close, volume] }
      - { type: null_rate, column: close, max_rate: 0.1, severity: critical }
```

```python
# 仅需为分钟数据写自定义逻辑
class SinaHistoricalCustom(CustomProvider):
    """处理分钟数据等复杂场景"""

    def _get_minute_data(self):
        # 仅保留无法声明式的复杂逻辑
        raw_df = ak.stock_zh_a_hist_min_em(symbol=self.symbol, period=self._map_period())
        return self._resample(raw_df)
```

**代码量对比**：80行 → 50行YAML + 30行Python，且 YAML 可自动生成。

---

## 八、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| YAML 配置错误 | API 行为异常 | Schema 验证 + CI 测试 |
| 迁移过程 bug | 用户受影响 | 新旧并行 + 灰度切换 |
| 性能回退 | 响应变慢 | 基准测试 + 性能监控 |
| 团队学习成本 | 开发效率下降 | 文档 + 示例 + 代码生成工具 |

---

## 九、总结

V2 架构的核心转变：

```
从 "写 Provider 类" → "写 YAML 配置"
从 "手动验证" → "声明式验证链"
从 "固定缓存" → "智能缓存引擎"
从 "无质量保障" → "完整质量监控"
从 "固定源顺序" → "动态健康评分路由"
```

这将使 AKShare One 从一个"薄包装集合"升级为"真正的金融数据基础设施"。
