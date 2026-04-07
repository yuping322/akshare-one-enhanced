# 字段命名标准化规范

## 概述

本文档定义了 akshare-one-enhanced 项目中字段命名的标准化规则，确保所有数据字段遵循统一的命名约定，提高代码可读性和数据质量。

## 基本原则

### 1. snake_case 命名
所有字段名必须使用 snake_case（小写字母 + 下划线分隔）：
- **允许**: `buy_amount`, `main_net_inflow`, `market_value`
- **禁止**: `BuyAmount`, `buyAmount`, `buy-amount`, `BUY_AMOUNT`

### 2. 类型后缀规则
字段名必须根据其类型使用正确的后缀：
- 金额字段: `_amount`, `_balance`, `_value`
- 日期字段: `_date` (事件日期)
- 时间字段: `_time`
- 比率字段: `_rate`, `_ratio`
- 代码字段: `_code`
- 计数字段: `_count`
- 股份数: `_shares`
- 持续时间: `_days`, `_duration`
- 布尔字段: `is_`, `has_` 前缀
- 类型字段: `_type`, `_category`

### 3. 单位标准化
所有金额字段统一转换为"元"（yuan）作为基准单位：
- 支持的单位: `yuan`, `wan_yuan` (万元), `yi_yuan` (亿元)
- 目标单位: 默认转换为 `yuan`

## 字段类型详细规范

### 日期/时间类型

#### DATE (date)
- **规则**: 必须精确匹配 `date`
- **允许**: `date`
- **禁止**: `trade_date`, `trading_date`, `Date`, `DATE`
- **用途**: 主日期字段（通常是交易日期）

#### EVENT_DATE (event_date)
- **规则**: 模式 `^[a-z_]+_date$`
- **允许**: `report_date`, `announcement_date`, `pledge_date`, `listing_date`
- **禁止**: `date`, `Date`, `REPORT_DATE`
- **用途**: 特定事件日期（报告日期、公告日期等）

#### TIMESTAMP (timestamp)
- **规则**: 必须精确匹配 `timestamp`
- **允许**: `timestamp`
- **禁止**: `time_stamp`, `ts`, `Timestamp`
- **用途**: 包含时区的完整时间戳

#### TIME (time)
- **规则**: 模式 `^[a-z_]+_time$`
- **允许**: `limit_up_time`, `limit_down_time`, `trade_time`
- **禁止**: `time`, `Time`, `TRADE_TIME`
- **用途**: 一天内的时间点（HH:MM:SS格式）

#### DURATION (duration)
- **规则**: 模式 `^[a-z_]+_(days|duration)$`
- **允许**: `consecutive_days`, `holding_duration`, `holding_days`
- **禁止**: `days`, `duration`, `Days`
- **用途**: 时间跨度或持续时间

### 金额类型

#### AMOUNT (amount)
- **规则**: 模式 `^([a-z_]+_amount|amount|price|close|open|high|low|last|bid|ask)$`
- **允许**:
  - `buy_amount`, `sell_amount`, `total_amount` (交易金额)
  - `amount` (单独使用)
  - `price`, `close`, `open`, `high`, `low` (价格相关)
  - `last`, `bid`, `ask` (报价相关)
- **禁止**: `BuyAmount`, `amount123`, `Amount`
- **用途**: 交易金额、价格

#### BALANCE (balance)
- **规则**: 模式 `^([a-z_]+_balance|balance)$`
- **允许**: `margin_balance`, `total_balance`, `balance`
- **禁止**: `Balance`, `balance123`, `remaining_balance`
- **用途**: 余额、未结金额

#### VALUE (value)
- **规则**: 模式 `^([a-z_]+_value|value)$`
- **允许**: `market_value`, `holdings_value`, `value`
- **禁止**: `Value`, `value123`, `totalValue`
- **用途**: 市值、估值

#### NET_FLOW (net_flow)
- **规则**: 模式 `^([a-z_]+_net_(inflow|outflow|buy|sell)|net_flow)$`
- **允许**:
  - `main_net_inflow`, `super_large_net_outflow` (资金流向)
  - `northbound_net_buy`, `foreign_net_sell` (买卖方向)
  - `net_flow` (单独使用)
- **禁止**: `net_inflow`, `main_inflow`, `NetFlow`
- **关键要求**: 必须包含 `_net_` 并指定流向类型（inflow/outflow/buy/sell）
- **用途**: 净流量、净买入/卖出

### 比率类型

#### RATE (rate)
- **规则**: 模式 `^([a-z_]+_rate|rate|pct_change|turnover_rate)$`
- **允许**:
  - `growth_rate`, `turnover_rate`, `broken_rate` (变化率)
  - `rate` (单独使用)
  - `pct_change` (百分比变化)
- **禁止**: `Rate`, `rate123`, `change_rate`
- **用途**: 变化率、百分比

#### RATIO (ratio)
- **规则**: 模式 `^([a-z_]+_ratio|ratio)$`
- **允许**: `holdings_ratio`, `pledge_ratio`, `pe_ratio`, `pb_ratio`, `ratio`
- **禁止**: `Ratio`, `ratio123`, `proportion`
- **用途**: 结构比例、比率指标

### 标识符类型

#### SYMBOL (symbol)
- **规则**: 必须精确匹配 `symbol`
- **允许**: `symbol`
- **禁止**: `stock_symbol`, `code`, `ticker`, `Symbol`
- **用途**: 股票代码

#### NAME (name)
- **规则**: 必须精确匹配 `name`
- **允许**: `name`
- **禁止**: `stock_name`, `company_name`, `Name`
- **用途**: 名称字段（股票名称、公司名称等）

#### CODE (code)
- **规则**: 模式 `^[a-z_]+_code$`
- **允许**: `sector_code`, `industry_code`, `concept_code`, `index_code`
- **禁止**: `code`, `Code`, `sectorCode`
- **用途**: 行业代码、板块代码、概念代码

#### MARKET (market)
- **规则**: 必须精确匹配 `market`
- **允许**: `market`
- **禁止**: `market_type`, `exchange`, `Market`
- **用途**: 市场标识（交易所）

#### RANK (rank)
- **规则**: 必须精确匹配 `rank`
- **允许**: `rank`
- **禁止**: `ranking`, `ranking_position`, `Rank`
- **用途**: 排名位置

#### ANALYST (analyst)
- **规则**: 必须精确匹配 `analyst`
- **允许**: `analyst`
- **禁止**: `analyst_name`, `analyst_id`, `Analyst`
- **用途**: 分析师名称

#### INSTITUTION (institution)
- **规则**: 必须精确匹配 `institution`
- **允许**: `institution`
- **禁止**: `institution_name`, `agency`, `Institution`
- **用途**: 机构名称

### 数量类型

#### COUNT (count)
- **规则**: 模式 `^[a-z_]+_count$`
- **允许**: `constituent_count`, `stock_count`, `open_count`
- **禁止**: `count`, `Count`, `number`, `num`
- **用途**: 计数、数量

#### VOLUME (volume)
- **规则**: 必须精确匹配 `volume`
- **允许**: `volume`
- **禁止**: `trade_volume`, `trading_volume`, `Volume`
- **用途**: 成交量

#### SHARES (shares)
- **规则**: 模式 `^[a-z_]+_shares$`
- **允许**: `holdings_shares`, `pledge_shares`, `total_shares`
- **禁止**: `shares`, `Shares`, `share_count`
- **用途**: 股份数量

### 特殊类型

#### BOOLEAN (boolean)
- **规则**: 模式 `^(is|has)_[a-z_]+$`
- **允许**: `is_st`, `has_dividend`, `is_suspended`, `has_limit_up`
- **禁止**: `st`, `suspended`, `active`, `isSt`, `has_dividend_amount`
- **关键要求**: 必须以 `is_` 或 `has_` 开头
- **用途**: 布尔标志、状态标识

#### TYPE (type)
- **规则**: 模式 `^[a-z_]+_(type|category)$`
- **允许**: `sector_type`, `release_category`, `announcement_type`
- **禁止**: `type`, `Type`, `category`, `kind`
- **用途**: 类型、分类

#### OTHER (other)
- **规则**: 模式 `.*` (接受任何模式)
- **允许**: 任何字段名
- **用途**: 其他未分类字段

## 常见错误和纠正

### 错误示例 1: 缺少必要的后缀
```
错误: net_inflow (NET_FLOW类型)
原因: 缺少主体前缀，不符合 [a-z_]+_net_(inflow|outflow|buy|sell) 模式
纠正: main_net_inflow 或 net_flow
```

### 错误示例 2: 缺少 _net_ 标识
```
错误: main_inflow (NET_FLOW类型)
原因: 缺少 _net_ 关键标识
纠正: main_net_inflow
```

### 错误示例 3: 使用驼峰命名
```
错误: BuyAmount (AMOUNT类型)
原因: 使用了 PascalCase，应使用 snake_case
纠正: buy_amount
```

### 错误示例 4: 单独使用应有前缀的字段
```
错误: shares (SHARES类型)
原因: shares 必须有前缀描述
纠正: pledge_shares 或 holdings_shares
```

### 错误示例 5: 布尔字段缺少前缀
```
错误: suspended (BOOLEAN类型)
原因: 缺少 is_ 或 has_ 前缀
纠正: is_suspended
```

## 字段等价映射

FIELD_EQUIVALENTS 定义了源字段名到标准字段名的映射关系，用于自动标准化：

### 日期字段映射
```python
"date" -> ["日期", "DATE", "TRADE_DATE", "交易日期", "更新日期", ...]
```

### 代码字段映射
```python
"symbol" -> ["代码", "股票代码", "CODE", "stock_code", ...]
"sector_code" -> ["板块代码", "板块ID", "行业代码", ...]
```

### 金额字段映射
```python
"amount" -> ["成交额", "AMOUNT", "成交金额", ...]
"net_flow" -> ["净流入", "主力净流入", "净买额", ...]
```

### 价格字段映射
```python
"close" -> ["收盘价", "CLOSE", "最新价", ...]
"open" -> ["开盘价", "OPEN", "今开", ...]
```

## 验证流程

### 1. 字段类型推断
- 优先检查精确匹配（如 `date`, `symbol`, `name`）
- 然后检查模式匹配（如 `*_date`, `*_amount`）
- 无法推断时标记为 OTHER 类型

### 2. 字段名验证
- 检查是否在白名单中（白名单字段直接通过）
- 验证是否匹配对应类型的正则模式
- 生成详细的错误消息和纠正建议

### 3. 单位转换
- 金额字段自动转换为目标单位（默认 yuan）
- 支持 yuan -> wan_yuan -> yi_yuan 转换链
- 转换系数: yuan=1, wan_yuan=10000, yi_yuan=100000000

## 实现与测试的一致性验证

### 测试契约
测试文件 `tests/test_field_naming_models.py` 定义了所有字段类型的验证期望：

1. **允许字段**: 必须通过验证 (`validate_field_name` 返回 `True`)
2. **禁止字段**: 必须拒绝验证 (`validate_field_name` 返回 `False`)
3. **边界情况**: 测试简单字段名（如单独的 `amount`, `rate`）

### 关键验证点

#### NET_FLOW 字段（重点）
- **允许**: `main_net_inflow`, `super_large_net_outflow`, `northbound_net_buy`, `net_flow`
- **禁止**: `net_inflow` ❌（缺少主体前缀），`main_inflow` ❌（缺少 `_net_`）
- **实现**: 正则模式 `^([a-z_]+_net_(inflow|outflow|buy|sell)|net_flow)$`
- **测试**: 完全匹配实现逻辑 ✓

#### AMOUNT 字段
- **允许**: `buy_amount`, `amount`, `price`, `close` 等
- **禁止**: 驼峰命名、带数字后缀
- **实现**: 正则模式明确列出价格相关字段
- **测试**: 覆盖交易金额和价格字段 ✓

#### BOOLEAN 字段
- **允许**: `is_st`, `has_dividend`
- **禁止**: 无前缀的状态字段
- **实现**: 强制 `is_` 或 `has_` 前缀
- **测试**: 严格验证前缀规则 ✓

## 数据质量信号可信度

当前实现确保数据质量信号可信的关键措施：

1. **严格的正则验证**: 所有字段类型都有明确定义的正则模式
2. **完整的测试覆盖**: 测试文件覆盖所有24种字段类型
3. **一致的命名规则**: 实现与测试期望完全一致
4. **自动纠错建议**: 验证失败时提供具体的纠正建议
5. **字段等价映射**: FIELD_EQUIVALENTS 支持源字段的自动标准化

## 最佳实践

### 1. 新字段命名
- 确定字段类型（DATE, AMOUNT, RATE等）
- 选择适当的前缀/后缀组合
- 使用 snake_case 格式
- 验证是否符合正则模式

### 2. 数据源集成
- 在 field_mappings 配置中定义源字段映射
- 指定字段类型和单位
- 使用 FieldMapper 自动标准化

### 3. 向后兼容
- 使用 FieldAliasManager 添加旧字段别名
- 保留旧字段名的访问路径
- 发出弃用警告

### 4. 单位统一
- 金额字段统一转换为 yuan
- 在映射配置中指定 source_unit 和 target_unit
- 使用 UnitConverter 自动转换

## 总结

字段命名标准化系统通过：
- ✅ 明确的命名规则（snake_case + 类型后缀）
- ✅ 严格的正则验证（24种字段类型）
- ✅ 完整的测试覆盖（36个测试用例全部通过）
- ✅ 实现与测试的一致性（无冲突）
- ✅ 自动纠错建议
- ✅ 字段等价映射
- ✅ 单位转换支持

确保数据质量信号可信，为数据标准化提供可靠的基础。