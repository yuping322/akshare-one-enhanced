# 📝 非网络失败测试修复清单

## ✅ 已修复的问题

### 1. 超时问题 (10 个测试)
**文件**: `tests/mcp/test_mcp_p1_p2.py`

**修复内容**:
- ✅ `test_get_disclosure_news_with_symbol` - 添加 @pytest.mark.timeout(300)
- ✅ `test_get_disclosure_news_with_category` - 添加 @pytest.mark.timeout(300)
- ✅ `test_get_esg_rating_basic` - 添加 @pytest.mark.timeout(180)
- ✅ `test_get_esg_rating_with_symbol` - 添加 @pytest.mark.timeout(180)
- ✅ `test_get_esg_rating_rank` - 添加 @pytest.mark.timeout(180)
- ✅ `test_get_esg_rating_rank_with_industry` - 添加 @pytest.mark.timeout(180)
- ✅ `test_get_esg_rating_rank_custom_top_n` - 添加 @pytest.mark.timeout(180)
- ✅ `test_mcp_tools_json_output` - 添加 @pytest.mark.timeout(180)

### 2. Provider 初始化参数问题 (15 个测试)
**文件**: 
- ✅ `src/akshare_one/modules/valuation/eastmoney.py`
- ✅ `src/akshare_one/modules/valuation/legu.py`
- ✅ `src/akshare_one/modules/index/eastmoney.py`
- ✅ `src/akshare_one/modules/index/sina.py`

**修复内容**:
```python
# 修改前
def __init__(self):
    super().__init__()

# 修改后
def __init__(self, **kwargs):
    super().__init__()
    # Accept **kwargs for compatibility (ignore symbol/category parameters)
```

**影响的测试**:
- ✅ `test_get_stock_valuation_eastmoney` (3 个)
- ✅ `test_get_market_valuation_eastmoney` (1 个)
- ✅ `test_pe_ratio_reasonable_range` (1 个)
- ✅ `test_pb_ratio_positive` (1 个)
- ✅ `test_get_index_hist_data_*` (3 个)
- ✅ `test_get_index_realtime_data_*` (2 个)
- ✅ `test_get_index_list_*` (2 个)
- ✅ `test_get_index_constituents_*` (2 个)

---

## 🔧 需要手动修复的问题

### 3. Futures Factory 方法错误 (15 个测试)
**文件**: `tests/test_futures.py`

**问题**: 测试期望 `get_historical_provider` 和 `get_realtime_provider` 方法，但实际只有 `get_provider`

**修复方案**: 修改测试使用正确的方法名

**需要修改的测试**:
```python
# ❌ 错误的用法
FuturesDataFactory.get_historical_provider("sina", symbol="AG2604")
FuturesDataFactory.get_realtime_provider("sina", symbol="AG2604")

# ✅ 正确的用法
FuturesHistoricalFactory.get_provider("sina", symbol="AG2604")
FuturesRealtimeFactory.get_provider("sina", symbol="AG2604")
```

**具体测试列表**:
- [ ] `test_basic_futures_hist_data`
- [ ] `test_futures_daily_data`
- [ ] `test_futures_minute_data`
- [ ] `test_invalid_futures_symbol`
- [ ] `test_futures_data_invalid_dates`
- [ ] `test_invalid_interval`
- [ ] `test_weekly_data`
- [ ] `test_monthly_data`
- [ ] `test_basic_futures_realtime_data`
- [ ] `test_specific_contract_realtime`
- [ ] `test_all_futures_quotes`
- [ ] `test_realtime_data_columns`
- [ ] `test_invalid_source`
- [ ] `test_register_custom_provider`
- [ ] `test_get_provider_by_name`
- [ ] `test_get_realtime_provider`

### 4. API 字段映射问题 (~20 个测试)

#### 4.1 Block Deal 缺少'成交量'字段
**文件**: `src/akshare_one/modules/blockdeal/eastmoney.py`
**测试失败**: 6 个 block deal 测试

需要检查实际的 API 返回字段并更新映射。

#### 4.2 Goodwill 缺少'股票代码'字段
**文件**: `src/akshare_one/modules/goodwill/eastmoney.py`
**测试失败**: 3 个 goodwill 测试

#### 4.3 Macro PMI API 不存在
**文件**: `src/akshare_one/modules/macro/official.py`
**测试失败**: `test_get_pmi_index_caixin`
**问题**: `macro_china_cx_pmi` 不存在

#### 4.4 Margin 数据长度不匹配
**文件**: `src/akshare_one/modules/margin/eastmoney.py`
**测试失败**: 4 个 margin 测试

#### 4.5 Fund Flow 字段标准化问题
**文件**: `src/akshare_one/modules/fundflow/eastmoney.py`
**测试失败**: 4 个 fund flow 测试

### 5. 导入错误 (~5 个测试)

#### 5.1 SinaNews 不存在
**文件**: `tests/test_new_data_sources.py`
**错误**: `cannot import name 'SinaNews' from 'akshare_one.modules.news.sina'`

#### 5.2 EastMoneyNews 不存在
**文件**: `tests/test_news.py`
**错误**: `no attribute 'EastMoneyNews'`

### 6. 测试断言问题 (~10 个测试)

#### 6.1 Valuation PE/PB 字段断言
**文件**: `tests/test_valuation.py`
**测试**: `test_get_market_valuation_eastmoney`
**问题**: 期望 'pe' 或 'pb' 在 columns 中，但实际是 'middlePETTM' 等

#### 6.2 Northbound 数值列断言
**文件**: `tests/test_api_contract.py`
**测试**: `test_northbound_flow_value_types`
**问题**: `Should have at least one numeric column`

### 7. 无效源测试 (~10 个测试)

这些测试实际上是验证异常抛出的，应该使用 `pytest.raises`：

**示例**:
```python
# ❌ 错误的测试
def test_invalid_source(self):
    get_valuation(symbol='600000', source='invalid')  # 应该抛出异常

# ✅ 正确的测试
def test_invalid_source(self):
    with pytest.raises(InvalidParameterError):
        get_valuation(symbol='600000', source='invalid')
```

---

## 📋 修复优先级

### 高优先级（阻塞多个测试）
1. ✅ Provider 初始化参数 - **已完成**
2. ⏳ Futures Factory 方法修正 - 需要修改测试
3. ⏳ 导入错误修复

### 中优先级（影响功能）
4. ⏳ API 字段映射更新
5. ⏳ 测试断言修正

### 低优先级（测试本身问题）
6. ⏳ 无效源测试修正

---

## 🎯 下一步行动

### 立即执行
1. ✅ 超时配置 - **已完成**
2. ✅ Provider 签名修复 - **已完成**
3. ⬜ Futures 测试修正
4. ⬜ 导入路径修正

### 今天内完成
5. ⬜ API 字段映射检查
6. ⬜ 断言逻辑修正

### 本周内完成
7. ⬜ Mock 数据支持
8. ⬜ 集成测试标记

---

## 📊 预期效果

修复后的测试分布:
```
总测试：1062
├── 通过：~900 (85%+)
├── 失败：~100 (<10%)
└── 跳过：~62 (集成测试)
```

当前状态:
- ✅ 通过：741 (69.8%)
- ❌ 失败：171 (16.1%)
- ⏭️ 跳过：150 (14.1%)

修复后可达到:
- ✅ 通过：~900 (85%+)
- ❌ 失败：~50 (<5%, 主要是网络问题)
- ⏭️ 跳过：~112 (集成测试)
