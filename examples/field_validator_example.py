"""
字段验证器使用示例

演示如何使用 FieldValidator 验证 DataFrame 字段命名是否符合规范。
"""

import pandas as pd
from akshare_one.modules.field_naming import FieldValidator, FieldType


def main():
    """主函数"""
    
    # 创建验证器
    print("创建字段验证器...")
    validator = FieldValidator()
    
    # 示例 1: 验证单个字段名
    print("\n=== 示例 1: 验证单个字段名 ===")
    
    test_cases = [
        ('date', FieldType.DATE),
        ('report_date', FieldType.EVENT_DATE),
        ('buy_amount', FieldType.AMOUNT),
        ('main_net_inflow', FieldType.NET_FLOW),
        ('turnover_rate', FieldType.RATE),
        ('invalid_field_name', FieldType.DATE),
    ]
    
    for field_name, field_type in test_cases:
        is_valid, error, suggestion = validator.validate_field_name(field_name, field_type)
        print(f"\n字段名: {field_name} (类型: {field_type.value})")
        print(f"  有效: {is_valid}")
        if not is_valid:
            print(f"  错误: {error}")
            print(f"  建议: {suggestion}")
    
    # 示例 2: 验证 DataFrame
    print("\n\n=== 示例 2: 验证 DataFrame ===")
    
    # 创建一个包含各种字段的 DataFrame
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'symbol': ['000001', '000002'],
        'name': ['平安银行', '万科A'],
        'close': [10.5, 20.3],
        'volume': [1000000, 2000000],
        'pct_change': [0.05, -0.02],
        'turnover_rate': [0.03, 0.04],
        'main_net_inflow': [1000000, -500000],
        'invalid_field': [100, 200],  # 不符合规范的字段
    })
    
    # 定义字段类型映射
    field_types = {
        'date': FieldType.DATE,
        'symbol': FieldType.SYMBOL,
        'name': FieldType.NAME,
        'close': FieldType.OTHER,
        'volume': FieldType.VOLUME,
        'pct_change': FieldType.RATE,
        'turnover_rate': FieldType.RATE,
        'main_net_inflow': FieldType.NET_FLOW,
        'invalid_field': FieldType.AMOUNT,  # 应该以 _amount 结尾
    }
    
    # 验证 DataFrame
    results = validator.validate_dataframe(df, field_types)
    
    print(f"\n验证结果:")
    print(f"总字段数: {len(results)}")
    
    valid_count = sum(1 for r in results.values() if r.is_valid)
    invalid_count = len(results) - valid_count
    
    print(f"有效字段: {valid_count}")
    print(f"无效字段: {invalid_count}")
    
    # 显示无效字段的详细信息
    if invalid_count > 0:
        print("\n无效字段详情:")
        for field_name, result in results.items():
            if not result.is_valid:
                print(f"\n  字段: {field_name}")
                print(f"    类型: {result.field_type.value if result.field_type else 'unknown'}")
                print(f"    错误: {result.error_message}")
                print(f"    建议: {result.suggested_name}")
    
    # 示例 3: 使用白名单
    print("\n\n=== 示例 3: 使用白名单 ===")
    
    # 将 invalid_field 添加到白名单
    validator.add_to_whitelist('invalid_field')
    print("已将 'invalid_field' 添加到白名单")
    
    # 重新验证
    results = validator.validate_dataframe(df, field_types)
    print(f"\n重新验证后:")
    print(f"  invalid_field 有效: {results['invalid_field'].is_valid}")
    
    # 示例 4: 生成验证摘要
    print("\n\n=== 示例 4: 验证摘要 ===")
    
    # 移除白名单中的字段以获得完整的验证结果
    validator.remove_from_whitelist('invalid_field')
    results = validator.validate_dataframe(df, field_types)
    
    summary = validator.get_validation_summary(results)
    
    print(f"\n验证摘要:")
    print(f"  总字段数: {summary['total_fields']}")
    print(f"  有效字段: {summary['valid_fields']}")
    print(f"  无效字段: {summary['invalid_fields']}")
    print(f"  验证通过率: {summary['validation_rate']:.1%}")
    
    if summary['type_statistics']:
        print(f"\n按类型统计:")
        for type_name, stats in summary['type_statistics'].items():
            print(f"  {type_name}:")
            print(f"    总数: {stats['total']}, 有效: {stats['valid']}, 无效: {stats['invalid']}")
    
    # 示例 5: 保存和加载白名单
    print("\n\n=== 示例 5: 保存和加载白名单 ===")
    
    # 添加一些字段到白名单
    whitelist_fields = ['open', 'high', 'low', 'close', 'adj_close']
    for field in whitelist_fields:
        validator.add_to_whitelist(field)
    
    print(f"添加了 {len(whitelist_fields)} 个字段到白名单")
    
    # 保存白名单
    whitelist_path = 'field_whitelist_example.json'
    validator.save_whitelist(whitelist_path)
    print(f"白名单已保存到: {whitelist_path}")
    
    # 创建新的验证器并加载白名单
    new_validator = FieldValidator()
    new_validator.load_whitelist(whitelist_path)
    print(f"从文件加载白名单，包含 {len(new_validator.whitelist)} 个字段")
    
    print("\n示例完成!")


if __name__ == '__main__':
    main()
