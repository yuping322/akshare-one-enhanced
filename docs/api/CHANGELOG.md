# API 文档更新日志

## [2026-02-14] - 文档拆分重构

### 新增
- ✨ **12个独立模块文档** - 将 interfaces-reference.md 拆分为独立文档
  - fundflow.md - 资金流模块
  - disclosure.md - 公告信披模块
  - northbound.md - 北向资金模块
  - macro.md - 宏观数据模块
  - blockdeal.md - 大宗交易模块
  - lhb.md - 龙虎榜模块
  - limitup.md - 涨停池模块
  - margin.md - 融资融券模块
  - pledge.md - 股权质押模块
  - restricted.md - 限售解禁模块
  - goodwill.md - 商誉模块
  - esg.md - ESG评级模块
- ✨ **split_interfaces.py** - 自动拆分脚本

### 更新
- 📝 **README.md** - 更新扩展接口文档链接
- 📝 **overview.md** - 更新快速导航链接
- 📝 **verify_docs.py** - 更新文档列表
- 📝 **CHANGELOG.md** - 添加本次更新记录
- 📝 **REFACTORING_SUMMARY.md** - 更新重构总结

### 删除
- ❌ **interfaces-reference.md** - 已拆分为12个独立文档

### 改进
- ✅ 每个模块一份独立文档，避免重复内容
- ✅ 文档结构更清晰，易于查找和维护
- ✅ 每个文档包含完整的导入方式和接口列表
- ✅ 保持统一的文档格式

### 验证
- ✅ 所有25个文档文件存在
- ✅ 所有文档链接有效
- ✅ 所有16个核心函数在代码中存在

---

## [2026-02-14] - 文档重构

### 新增
- ✨ **README.md** - 文档目录索引和使用指南
- ✨ **REFACTORING_SUMMARY.md** - 文档重构总结
- ✨ **verify_docs.py** - 文档验证脚本
- ✨ **CHANGELOG.md** - 本文档

### 更新
- 📝 **overview.md** - 添加12个扩展模块说明，更新快速导航
- 📝 **futures.md** - 为3个函数添加异常说明
- 📝 **options.md** - 为4个函数添加异常说明
- 📝 **insider.md** - 为1个函数添加异常说明

### 删除
- ❌ **market-data-extension.md** - 与 interfaces-reference.md 内容重复

### 改进
- ✅ 统一所有文档格式
- ✅ 确保文档与代码一致
- ✅ 消除重复内容
- ✅ 添加完整的异常说明
- ✅ 提高文档可维护性

### 验证
- ✅ 所有13个文档文件存在
- ✅ 所有文档链接有效
- ✅ 所有16个核心函数在代码中存在

---

## 文档结构

```
docs/api/
├── README.md                    # 📖 文档索引
├── overview.md                  # 🏠 API 概览
├── CHANGELOG.md                 # 📋 更新日志
├── REFACTORING_SUMMARY.md       # 📝 重构总结
├── verify_docs.py               # 🔍 验证脚本
├── split_interfaces.py          # 🔧 文档拆分脚本
│
├── 核心接口文档 (9个)
│   ├── basic-info.md
│   ├── historical.md
│   ├── realtime.md
│   ├── financial.md
│   ├── news.md
│   ├── futures.md
│   ├── options.md
│   ├── insider.md
│   └── indicators.md
│
└── 扩展接口文档 (12个)
    ├── fundflow.md              # 资金流
    ├── disclosure.md            # 公告信披
    ├── northbound.md            # 北向资金
    ├── macro.md                 # 宏观数据
    ├── blockdeal.md             # 大宗交易
    ├── lhb.md                   # 龙虎榜
    ├── limitup.md               # 涨停池
    ├── margin.md                # 融资融券
    ├── pledge.md                # 股权质押
    ├── restricted.md            # 限售解禁
    ├── goodwill.md              # 商誉
    └── esg.md                   # ESG评级
```

## 统计数据

- **文档总数**: 25个
- **核心接口文档**: 9个
- **扩展接口文档**: 12个（每个模块独立文档）
- **核心函数**: 16个
- **扩展函数**: 37个
- **技术指标函数**: 30+个
- **总函数数**: 90+个

## 维护指南

### 添加新接口
1. 在相应模块文档中添加函数说明
2. 遵循统一格式（函数签名、参数、返回值、异常、示例）
3. 更新 overview.md 的导航链接
4. 运行 `python verify_docs.py` 验证

### 修改接口
1. 同步更新文档中的函数签名
2. 更新参数说明和返回值说明
3. 更新示例代码
4. 运行验证脚本

### 定期审查
- 每月检查文档与代码的一致性
- 运行示例代码验证正确性
- 检查链接是否有效
- 更新过时的信息

---

**最后更新**: 2026-02-14  
**维护者**: AKShare One Team
