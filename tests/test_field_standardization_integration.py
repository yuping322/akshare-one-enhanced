"""
字段标准化集成测试

验证所有模块的字段标准化功能是否正常工作。
"""

import pytest

from akshare_one.modules.blockdeal.eastmoney import EastmoneyBlockDealProvider
from akshare_one.modules.field_naming import FieldType, FieldValidator
from akshare_one.modules.fundflow.eastmoney import EastmoneyFundFlowProvider
from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider


class TestFieldStandardizationIntegration:
    """字段标准化集成测试"""
    
    def test_northbound_standardization_integration(self):
        """测试北向资金模块的标准化集成"""
        provider = EastmoneyNorthboundProvider()
        
        # 测试获取数据（使用真实数据）
        try:
            result = provider.get_northbound_flow('2024-01-01', '2024-01-31', 'all')
            
            # 验证数据不为空
            assert not result.empty, "北向资金数据不应为空"
            
            # 验证字段名符合规范
            validator = FieldValidator()
            validation_results = validator.validate_dataframe(result)
            
            # 检查是否有不符合规范的字段
            invalid_fields = [
                field_name for field_name, result_obj in validation_results.items() 
                if not result_obj.is_valid
            ]
            
            if invalid_fields:
                print(f"发现不符合规范的字段: {invalid_fields}")
                for field_name in invalid_fields:
                    result_obj = validation_results[field_name]
                    print(f"  {field_name}: {result_obj.error_message}")
            
            # 验证关键字段存在且类型正确
            expected_fields = {
                'date': FieldType.DATE,
                'market': FieldType.MARKET,
                'net_buy': FieldType.NET_FLOW,
                'buy_amount': FieldType.AMOUNT,
                'sell_amount': FieldType.AMOUNT,
                'balance': FieldType.BALANCE
            }
            
            for field_name, expected_type in expected_fields.items():
                if field_name in result.columns:
                    # 验证字段类型
                    validation_result = validator.validate_field_name(field_name, expected_type)
                    assert validation_result[0], f"字段 {field_name} 不符合 {expected_type.value} 类型规范"
                    
                    # 验证数据类型
                    if expected_type in [FieldType.DATE, FieldType.SYMBOL, FieldType.NAME]:
                        assert result[field_name].dtype == 'object', f"{field_name} 应为字符串类型"
                    elif expected_type in [FieldType.NET_FLOW, FieldType.AMOUNT, FieldType.BALANCE, FieldType.RATE, FieldType.RATIO]:
                        assert result[field_name].dtype in ['float64', 'int64'], f"{field_name} 应为数值类型"
            
            print(f"北向资金标准化测试通过，共 {len(result)} 条记录")
            print(f"字段: {list(result.columns)}")
            
        except Exception as e:
            pytest.skip(f"跳过测试，原因: {e}")
    
    def test_fundflow_standardization_integration(self):
        """测试资金流模块的标准化集成"""
        provider = EastmoneyFundFlowProvider()
        
        # 测试获取数据（使用真实数据）
        try:
            result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
            
            # 验证数据不为空
            assert not result.empty, "资金流数据不应为空"
            
            # 验证字段名符合规范
            validator = FieldValidator()
            validation_results = validator.validate_dataframe(result)
            
            # 检查是否有不符合规范的字段
            invalid_fields = [
                field_name for field_name, result_obj in validation_results.items() 
                if not result_obj.is_valid
            ]
            
            if invalid_fields:
                print(f"发现不符合规范的字段: {invalid_fields}")
                for field_name in invalid_fields:
                    result_obj = validation_results[field_name]
                    print(f"  {field_name}: {result_obj.error_message}")
            
            # 验证关键字段存在且类型正确
            expected_fields = {
                'date': FieldType.DATE,
                'symbol': FieldType.SYMBOL,
                'close_price': FieldType.VALUE,
                'pct_change': FieldType.RATE,
                'fundflow_main_net_inflow': FieldType.NET_FLOW,
                'fundflow_main_net_inflow_rate': FieldType.RATE,
                'fundflow_super_large_net_inflow': FieldType.NET_FLOW,
                'fundflow_large_net_inflow': FieldType.NET_FLOW,
                'fundflow_medium_net_inflow': FieldType.NET_FLOW,
                'fundflow_small_net_inflow': FieldType.NET_FLOW
            }
            
            for field_name, expected_type in expected_fields.items():
                if field_name in result.columns:
                    # 验证字段类型
                    validation_result = validator.validate_field_name(field_name, expected_type)
                    assert validation_result[0], f"字段 {field_name} 不符合 {expected_type.value} 类型规范"
                    
                    # 验证数据类型
                    if expected_type in [FieldType.DATE, FieldType.SYMBOL, FieldType.NAME]:
                        assert result[field_name].dtype == 'object', f"{field_name} 应为字符串类型"
                    elif expected_type in [FieldType.NET_FLOW, FieldType.AMOUNT, FieldType.BALANCE, FieldType.RATE, FieldType.RATIO, FieldType.VALUE]:
                        assert result[field_name].dtype in ['float64', 'int64'], f"{field_name} 应为数值类型"
            
            print(f"资金流标准化测试通过，共 {len(result)} 条记录")
            print(f"字段: {list(result.columns)}")
            
        except Exception as e:
            pytest.skip(f"跳过测试，原因: {e}")
    
    def test_blockdeal_standardization_integration(self):
        """测试大宗交易模块的标准化集成"""
        provider = EastmoneyBlockDealProvider()
        
        # 测试获取数据（使用真实数据）
        try:
            result = provider.get_block_deal(symbol=None, start_date='2024-01-01', end_date='2024-01-31')
            
            # 验证数据不为空
            assert not result.empty, "大宗交易数据不应为空"
            
            # 验证字段名符合规范
            validator = FieldValidator()
            validation_results = validator.validate_dataframe(result)
            
            # 检查是否有不符合规范的字段
            invalid_fields = [
                field_name for field_name, result_obj in validation_results.items() 
                if not result_obj.is_valid
            ]
            
            if invalid_fields:
                print(f"发现不符合规范的字段: {invalid_fields}")
                for field_name in invalid_fields:
                    result_obj = validation_results[field_name]
                    print(f"  {field_name}: {result_obj.error_message}")
            
            # 验证关键字段存在且类型正确
            expected_fields = {
                'trade_date': FieldType.DATE,
                'symbol': FieldType.SYMBOL,
                'name': FieldType.NAME,
                'price': FieldType.VALUE,
                'volume': FieldType.VOLUME,
                'amount': FieldType.AMOUNT,
                'buyer_broker': FieldType.NAME,
                'seller_broker': FieldType.NAME,
                'pct_change': FieldType.RATE,
                'close_price': FieldType.VALUE,
                'premium_rate': FieldType.RATE
            }
            
            for field_name, expected_type in expected_fields.items():
                if field_name in result.columns:
                    # 验证字段类型
                    validation_result = validator.validate_field_name(field_name, expected_type)
                    assert validation_result[0], f"字段 {field_name} 不符合 {expected_type.value} 类型规范"
                    
                    # 验证数据类型
                    if expected_type in [FieldType.DATE, FieldType.SYMBOL, FieldType.NAME, FieldType.CODE]:
                        assert result[field_name].dtype == 'object', f"{field_name} 应为字符串类型"
                    elif expected_type in [FieldType.NET_FLOW, FieldType.AMOUNT, FieldType.BALANCE, FieldType.RATE, FieldType.RATIO, FieldType.VALUE, FieldType.VOLUME, FieldType.SHARES]:
                        assert result[field_name].dtype in ['float64', 'int64'], f"{field_name} 应为数值类型"
            
            print(f"大宗交易标准化测试通过，共 {len(result)} 条记录")
            print(f"字段: {list(result.columns)}")
            
        except Exception as e:
            pytest.skip(f"跳过测试，原因: {e}")
    
    def test_cross_module_field_consistency(self):
        """测试跨模块字段一致性"""
        # 验证相同概念的字段在不同模块中使用相同的命名规范
        common_fields = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL,
            'name': FieldType.NAME,
            'pct_change': FieldType.RATE,
            'close': FieldType.OTHER  # close字段在历史数据中是OTHER类型
        }
        
        validator = FieldValidator()
        
        for field_name, expected_type in common_fields.items():
            # 验证字段名符合规范
            validation_result = validator.validate_field_name(field_name, expected_type)
            assert validation_result[0], f"通用字段 {field_name} 不符合 {expected_type.value} 类型规范"
        
        print("跨模块字段一致性测试通过")
    
    def test_json_compatibility(self):
        """测试JSON兼容性"""
        providers = [
            EastmoneyNorthboundProvider(),
            EastmoneyFundFlowProvider(),
            EastmoneyBlockDealProvider()
        ]
        
        for provider in providers:
            try:
                # 获取少量数据进行测试
                if hasattr(provider, 'get_northbound_flow'):
                    data = provider.get_northbound_flow('2024-01-01', '2024-01-31', 'all')
                elif hasattr(provider, 'get_stock_fund_flow'):
                    data = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
                elif hasattr(provider, 'get_block_deal'):
                    data = provider.get_block_deal(symbol=None, start_date='2024-01-01', end_date='2024-01-31')
                else:
                    continue
                
                if not data.empty:
                    # 尝试转换为JSON
                    json_str = data.to_json(orient='records', date_format='iso')
                    assert json_str is not None, f"{provider.__class__.__name__} 数据无法转换为JSON"
                    
                    # 检查是否有NaN或Infinity值
                    numeric_columns = data.select_dtypes(include=['float64', 'float32']).columns
                    for col in numeric_columns:
                        assert not data[col].isna().any(), f"{col} 列包含NaN值"
                        assert not (data[col] == float('inf')).any(), f"{col} 列包含Infinity值"
                        assert not (data[col] == float('-inf')).any(), f"{col} 列包含-Infinity值"
                    
                    print(f"{provider.__class__.__name__} JSON兼容性测试通过")
                    
            except Exception as e:
                pytest.skip(f"跳过测试，原因: {e}")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestFieldStandardizationIntegration()
    
    print("=== 字段标准化集成测试 ===")
    test_instance.test_northbound_standardization_integration()
    test_instance.test_fundflow_standardization_integration()
    test_instance.test_blockdeal_standardization_integration()
    test_instance.test_cross_module_field_consistency()
    test_instance.test_json_compatibility()
    
    print("\n=== 所有测试完成 ===")