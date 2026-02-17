"""
字段标准化功能使用示例

展示如何使用AKShare-One的字段标准化框架来确保数据字段的一致性。
"""

import pandas as pd
from datetime import datetime

from akshare_one.modules.field_naming import (
    FieldValidator, 
    FieldStandardizer, 
    FieldMapper,
    FieldType,
    NamingRules
)
from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider
from akshare_one.modules.fundflow.eastmoney import EastmoneyFundFlowProvider


def demonstrate_field_validation():
    """演示字段验证功能"""
    print("=== 字段验证功能演示 ===")
    
    # 创建验证器
    validator = FieldValidator()
    
    # 测试一些字段名
    test_fields = [
        ('date', FieldType.DATE),
        ('symbol', FieldType.SYMBOL),
        ('main_net_inflow', FieldType.NET_FLOW),
        ('pct_change', FieldType.RATE),
        ('market_value', FieldType.VALUE),
        ('invalid_field_name', FieldType.AMOUNT)  # 这个应该失败
    ]
    
    print("字段验证结果:")
    for field_name, field_type in test_fields:
        is_valid, error_msg, suggested_name = validator.validate_field_name(field_name, field_type)
        status = "✓ 通过" if is_valid else "✗ 失败"
        print(f"  {field_name} ({field_type.value}): {status}")
        if not is_valid:
            print(f"    错误: {error_msg}")
            if suggested_name:
                print(f"    建议: {suggested_name}")
    
    print()


def demonstrate_field_standardization():
    """演示字段标准化功能"""
    print("=== 字段标准化功能演示 ===")
    
    # 创建标准化器
    rules = NamingRules()
    standardizer = FieldStandardizer(rules)
    
    # 测试字段标准化
    test_fields = [
        ('date', FieldType.DATE),
        ('net_buy', FieldType.NET_FLOW),
        ('buy_amount', FieldType.AMOUNT),
        ('pct_change', FieldType.RATE)
    ]
    
    print("字段标准化结果:")
    for field_name, field_type in test_fields:
        try:
            standardized = standardizer.standardize_field_name(field_name, field_type)
            print(f"  {field_name} -> {standardized}")
        except ValueError as e:
            print(f"  {field_name} -> 错误: {e}")
    
    print()


def demonstrate_field_mapping():
    """演示字段映射功能"""
    print("=== 字段映射功能演示 ===")
    
    # 创建映射器
    mapper = FieldMapper()
    
    # 创建模拟的原始数据
    raw_data = pd.DataFrame({
        '日期': ['2024-01-01', '2024-01-02'],
        '股票代码': ['600000', '600001'],
        '股票简称': ['浦发银行', '白云机场'],
        '当日成交净买额': [100000000.0, 50000000.0],  # 1亿元
        '涨跌幅': [1.5, -0.8]
    })
    
    print("原始数据列名:", list(raw_data.columns))
    
    # 应用字段映射
    try:
        mapped_data = mapper.map_fields(raw_data, source='eastmoney', module='northbound')
        print("映射后数据列名:", list(mapped_data.columns))
        print("映射后的数据:")
        print(mapped_data.head())
    except Exception as e:
        print(f"映射失败: {e}")
    
    print()


def demonstrate_provider_standardization():
    """演示Provider中的标准化功能"""
    print("=== Provider标准化功能演示 ===")
    
    # 创建北向资金Provider
    provider = EastmoneyNorthboundProvider()
    
    print("Provider元数据:")
    print(f"  数据源: {provider.get_source_name()}")
    print(f"  数据类型: {provider.get_data_type()}")
    print(f"  更新频率: {provider.get_update_frequency()}")
    print(f"  延迟时间: {provider.get_delay_minutes()} 分钟")
    
    # 测试数据获取（使用真实数据）
    try:
        print("\n获取北向资金数据...")
        result = provider.get_northbound_flow('2024-01-01', '2024-01-31', 'all')
        
        if not result.empty:
            print(f"成功获取 {len(result)} 条记录")
            print("字段名:", list(result.columns))
            
            # 验证字段标准化
            validator = FieldValidator()
            validation_results = validator.validate_dataframe(result)
            
            print("\n字段验证结果:")
            for field_name, validation_result in validation_results.items():
                status = "✓" if validation_result.is_valid else "✗"
                print(f"  {field_name}: {status}")
                if not validation_result.is_valid:
                    print(f"    错误: {validation_result.error_message}")
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"数据获取失败: {e}")
        print("这可能是因为网络问题或数据源不可用")
    
    print()


def demonstrate_cross_module_consistency():
    """演示跨模块字段一致性"""
    print("=== 跨模块字段一致性演示 ===")
    
    # 验证常用字段在不同模块中的一致性
    common_fields = {
        'date': FieldType.DATE,
        'symbol': FieldType.SYMBOL,
        'name': FieldType.NAME,
        'pct_change': FieldType.RATE
    }
    
    validator = FieldValidator()
    
    print("跨模块通用字段验证:")
    for field_name, expected_type in common_fields.items():
        is_valid, error_msg, suggested_name = validator.validate_field_name(field_name, expected_type)
        status = "✓ 一致" if is_valid else "✗ 不一致"
        print(f"  {field_name}: {status}")
        if not is_valid:
            print(f"    错误: {error_msg}")
            if suggested_name:
                print(f"    建议: {suggested_name}")
    
    print()


def main():
    """主函数"""
    print("AKShare-One 字段标准化功能演示")
    print("=" * 50)
    
    # 运行所有演示
    demonstrate_field_validation()
    demonstrate_field_standardization()
    demonstrate_field_mapping()
    demonstrate_provider_standardization()
    demonstrate_cross_module_consistency()
    
    print("=== 演示完成 ===")
    print("\n字段标准化框架的主要优势:")
    print("1. 确保字段命名的一致性")
    print("2. 提供字段类型验证")
    print("3. 支持字段映射和转换")
    print("4. 保证跨模块字段一致性")
    print("5. 提供详细的错误信息和建议")


if __name__ == "__main__":
    main()