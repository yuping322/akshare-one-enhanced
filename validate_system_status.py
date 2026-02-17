"""
系统状态验证脚本

验证AKShare-One字段标准化升级后的系统状态
"""

def test_basic_imports():
    """测试基本导入"""
    print("=== 基本导入测试 ===")
    try:
        import akshare_one
        print("✓ AKShare-One 主模块导入成功")
    except Exception as e:
        print(f"✗ AKShare-One 主模块导入失败: {e}")
        return False
    
    try:
        from akshare_one.modules.field_naming import FieldValidator, FieldType, FieldMapper
        print("✓ 字段命名模块导入成功")
    except Exception as e:
        print(f"✗ 字段命名模块导入失败: {e}")
        return False
    
    try:
        from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider
        print("✓ 北向资金模块导入成功")
    except Exception as e:
        print(f"✗ 北向资金模块导入失败: {e}")
        return False
    
    try:
        from akshare_one.modules.fundflow.eastmoney import EastmoneyFundFlowProvider
        print("✓ 资金流模块导入成功")
    except Exception as e:
        print(f"✗ 资金流模块导入失败: {e}")
        return False
    
    return True

def test_field_validation():
    """测试字段验证功能"""
    print("\n=== 字段验证功能测试 ===")
    try:
        from akshare_one.modules.field_naming import FieldValidator, FieldType
        
        validator = FieldValidator()
        
        # 测试有效字段
        test_cases = [
            ('date', FieldType.DATE, True),
            ('symbol', FieldType.SYMBOL, True),
            ('northbound_net_buy', FieldType.NET_FLOW, True),
            ('fundflow_main_net_inflow', FieldType.NET_FLOW, True),
            ('invalid_field_name', FieldType.AMOUNT, False)
        ]
        
        all_passed = True
        for field_name, field_type, expected in test_cases:
            is_valid, error_msg, suggestion = validator.validate_field_name(field_name, field_type)
            if is_valid == expected:
                print(f"✓ {field_name} ({field_type.value}): 通过")
            else:
                print(f"✗ {field_name} ({field_type.value}): 失败 - {error_msg}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 字段验证功能测试失败: {e}")
        return False

def test_providers():
    """测试Provider功能"""
    print("\n=== Provider功能测试 ===")
    try:
        from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider
        from akshare_one.modules.fundflow.eastmoney import EastmoneyFundFlowProvider
        
        # 测试北向资金Provider
        northbound_provider = EastmoneyNorthboundProvider()
        print(f"✓ 北向资金Provider创建成功")
        print(f"  - 数据源: {northbound_provider.get_source_name()}")
        print(f"  - 数据类型: {northbound_provider.get_data_type()}")
        print(f"  - 更新频率: {northbound_provider.get_update_frequency()}")
        
        # 测试资金流Provider
        fundflow_provider = EastmoneyFundFlowProvider()
        print(f"✓ 资金流Provider创建成功")
        print(f"  - 数据源: {fundflow_provider.get_source_name()}")
        print(f"  - 数据类型: {fundflow_provider.get_data_type()}")
        print(f"  - 更新频率: {fundflow_provider.get_update_frequency()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Provider功能测试失败: {e}")
        return False

def test_field_mapping():
    """测试字段映射功能"""
    print("\n=== 字段映射功能测试 ===")
    try:
        from akshare_one.modules.field_naming import FieldMapper
        import pandas as pd
        
        mapper = FieldMapper()
        print("✓ 字段映射器创建成功")
        
        # 测试配置加载
        if mapper.mappings:
            print(f"✓ 加载了 {len(mapper.mappings)} 个数据源的映射配置")
            for source, modules in mapper.mappings.items():
                print(f"  - {source}: {len(modules)} 个模块")
        else:
            print("⚠ 未加载到映射配置")
        
        return True
        
    except Exception as e:
        print(f"✗ 字段映射功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("AKShare-One 系统状态验证")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_field_validation,
        test_providers,
        test_field_mapping
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统状态正常。")
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置。")
        return False

if __name__ == "__main__":
    main()